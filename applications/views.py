import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Min, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ApplicationForm
from .helpers import render_htmx
from .models import Application, Company


@login_required
def add_application(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            comp_name = form.cleaned_data["company_name"].strip()
            company, _ = Company.objects.get_or_create(name=comp_name)

            application = form.save(commit=False)
            application.user = request.user
            application.company = company
            application.save()

            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Refresh"] = "true"
                return response

            return redirect("applications:list")

    else:
        form = ApplicationForm()

    if request.headers.get("HX-Request"):
        return render(request, "applications/partials/_add_application_drawer.html", {"form": form})

    return render(request, "applications/add_application.html", {"form": form})

@login_required
def edit_details(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, instance=application)

        if form.is_valid():
            comp_name = form.cleaned_data.get("company_name", "").strip()
            if comp_name:
                company, _ = Company.objects.get_or_create(name=comp_name)
                application.company = company

            form.save()

            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Refresh"] = "true"
                return response

            return redirect("applications:list")

    else:
        initial_data = {}
        if application.company:
            initial_data["company_name"] = application.company.name

        form = ApplicationForm(instance=application, initial=initial_data)

    context = {
        "form": form,
        "app": application,
    }

    if request.headers.get("HX-Request"):
        return render(request, "applications/partials/_edit_application_drawer.html", context)

    return render(request, "applications/edit_application.html", context)

@login_required
def delete_details(request, pk):
    app = get_object_or_404(Application, pk=pk)

    if request.method in ["POST", "DELETE"]:
        app.delete()
        response = HttpResponse()
        response['HX-Refresh'] = "true"
        return response

    context = {"app": app}
    return render(request, "applications/delete_application.html", context)


@login_required
def application_list(request):
    time_filter = request.GET.get('time_filter', 'all')
    user_apps = Application.objects.filter(user=request.user).select_related(
        'company'
    )




    metrics = {
        "total": user_apps.count(),
        "applied": user_apps.filter(
            status=Application.Status.APPLIED
        ).count(),
        "interviewing": user_apps.filter(
            status=Application.Status.INTERVIEWING
        ).count(),
        "offer": user_apps.filter(
            status=Application.Status.OFFER
        ).count(),
        "rejected": user_apps.filter(
            status=Application.Status.REJECTED
        ).count(),

    }

    # Date Filtering
    now = timezone.now()
    if time_filter == 'today':
        today_start = now .replace(hour=0, minute=0, second=0, microsecond=0)
        user_apps = user_apps.filter(applied_date__gte=today_start)
    elif time_filter == '7days':
        user_apps = user_apps.filter(applied_date__gte = now - timedelta(days=7))
    elif time_filter == '30days':
        user_apps = user_apps.filter(applied_date__gte = now - timedelta(days=30))
    elif time_filter == 'this_month':
        user_apps = user_apps.filter(applied_date__year = now.year, applied_date__month = now.month)


    kanban_columns = [
        {
            "status_key": Application.Status.APPLIED,
            "label": "Applied",
            "apps": [
                app
                for app in user_apps
                if app.status == Application.Status.APPLIED
            ],
        },
        {
            "status_key": Application.Status.INTERVIEWING,
            "label": "Interviewing",
            "apps": [
                app
                for app in user_apps
                if app.status == Application.Status.INTERVIEWING
            ],
        },
        {
            "status_key": Application.Status.OFFER,
            "label": "Offer Received",
            "apps": [
                app
                for app in user_apps
                if app.status == Application.Status.OFFER
            ],
        },
        {
            "status_key": Application.Status.REJECTED,
            "label": "Rejected",
            "apps": [
                app
                for app in user_apps
                if app.status == Application.Status.REJECTED
            ],
        },
    ]





    context = {
            "metrics": metrics,
            "kanban_columns": kanban_columns,
            "current_time_filter": time_filter,
        }
    return render_htmx(request, 'applications/partials/_application_content.html', context=context)


@login_required
def analytics_view(request):
    user = request.user
    user_apps = Application.objects.filter(user=user)
    total_apps = user_apps.count()

    # --- 1. Key Metrics Stat Strip ---
    interview_count = user_apps.filter(
        status=Application.Status.INTERVIEWING
    ).count()
    offer_count = user_apps.filter(status=Application.Status.OFFER).count()
    rejected_count = user_apps.filter(status=Application.Status.REJECTED).count()
    responded_count = interview_count + offer_count

    response_rate = (
        round((responded_count / total_apps * 100), 1) if total_apps > 0 else 0
    )
    interview_rate = (
        round((interview_count / total_apps * 100), 1) if total_apps > 0 else 0
    )
    offer_rate = (
        round((offer_count / total_apps * 100), 1) if total_apps > 0 else 0
    )

    avg_salary_val = user_apps.aggregate(Avg("salary_estimate"))[
        "salary_estimate__avg"
    ]
    avg_target = (
        f"${round(float(avg_salary_val) / 1000)}k" if avg_salary_val else "$0k"
    )

    # --- 2. Conversion Funnel ---
    funnel = [
        {
            "label": "Total Applied",
            "count": total_apps,
            "pct": 100 if total_apps > 0 else 0,
            "dot_color": "bg-blue-500",
            "bar_color": "bg-blue-500",
        },
        {
            "label": "In Review / Queue",
            "count": user_apps.filter(status=Application.Status.APPLIED).count(),
            "pct": (
                round(
                    (
                        user_apps.filter(
                            status=Application.Status.APPLIED
                        ).count()
                        / total_apps
                        * 100
                    ),
                    1,
                )
                if total_apps > 0
                else 0
            ),
            "dot_color": "bg-neutral-500",
            "bar_color": "bg-neutral-500",
        },
        {
            "label": "Interview Stages",
            "count": interview_count,
            "pct": (
                round((interview_count / total_apps * 100), 1)
                if total_apps > 0
                else 0
            ),
            "dot_color": "bg-amber-400",
            "bar_color": "bg-amber-400",
        },
        {
            "label": "Offers Secured",
            "count": offer_count,
            "pct": (
                round((offer_count / total_apps * 100), 1)
                if total_apps > 0
                else 0
            ),
            "dot_color": "bg-emerald-500",
            "bar_color": "bg-emerald-500",
        },
    ]

    # --- 3. Top Sources / Platforms Breakdown ---
    platform_map = dict(Application.Platform.choices)
    badge_styles = {
        Application.Platform.LINKEDIN: "bg-blue-50/60 text-blue-700",
        Application.Platform.INDEED: "bg-amber-50/60 text-amber-700",
        Application.Platform.COMPANY_SITE: "bg-emerald-50/60 text-emerald-700",
        Application.Platform.OTHER: "bg-neutral-50 text-neutral-700",
    }

    sources_query = (
        user_apps.values("platform").annotate(count=Count("id")).order_by("-count")
    )

    top_sources = []
    for item in sources_query:
        p_code = item["platform"]
        cnt = item["count"]
        pct = round((cnt / total_apps * 100)) if total_apps > 0 else 0
        top_sources.append({
            "name": platform_map.get(p_code, p_code),
            "count": cnt,
            "pct": pct,
            "badge_class": badge_styles.get(
                p_code, "bg-neutral-50 text-neutral-700"
            ),
        })

    # --- 4. Dynamic Historical Activity Heatmap Logic ---
    today = timezone.localdate()

    valid_apps = user_apps.exclude(applied_date__isnull=True)
    oldest_app_date = valid_apps.aggregate(earliest=Min("applied_date"))["earliest"]

    default_start = today - timedelta(weeks=52)
    start_date = min(oldest_app_date, default_start) if oldest_app_date else default_start

    start_date = start_date - timedelta(days=start_date.weekday())
    end_date = today + timedelta(days=(6 - today.weekday()))

    # Grouping by DateField directly
    app_counts = (
        valid_apps.filter(applied_date__gte=start_date, applied_date__lte=today)
        .values("applied_date")
        .annotate(count=Count("id"))
    )

    counts_map = {
        item["applied_date"].strftime("%Y-%m-%d"): item["count"]
        for item in app_counts
        if item["applied_date"]
    }

    heatmap_weeks = []
    current_week = []
    total_active_days = 0
    total_submissions = 0

    curr_date = start_date
    while curr_date <= end_date:
        date_key = curr_date.strftime("%Y-%m-%d")
        count = counts_map.get(date_key, 0)

        if count > 0:
            total_active_days += 1
            total_submissions += count

        is_future = curr_date > today

        if is_future:
          bg_color = (
              "bg-transparent border-transparent cursor-default"
              " pointer-events-none"
          )
        elif count == 0:
          bg_color = "bg-neutral-100 border-neutral-200"
        elif count == 1:
          bg_color = "bg-blue-200 border-blue-300"
        elif count <= 3:
          bg_color = "bg-blue-400 border-blue-500"
        elif count <= 5:
          bg_color = "bg-blue-600 border-blue-700"
        else:
          bg_color = "bg-blue-800 border-blue-950"

        current_week.append({
            "date": curr_date.strftime("%b %d, %Y"),
            "count": count,
            "bg_color": bg_color,
            "is_today": curr_date == today,
            "is_future": is_future,
        })

        if len(current_week) == 7:
            heatmap_weeks.append(current_week)
            current_week = []

        curr_date += timedelta(days=1)

    context = {
        "total_apps": total_apps,
        "interview_count": interview_count,
        "offer_count": offer_count,
        "rejected_count": rejected_count,
        "response_rate": response_rate,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
        "avg_target": avg_target,
        "funnel": funnel,
        "top_sources": top_sources,
        "heatmap_weeks": heatmap_weeks,
        "total_active_days": total_active_days,
        "total_submissions": total_submissions,
    }

    if request.headers.get("HX-Request"):
        return render(
            request, "applications/partials/_analytics_content.html", context
        )

    return render(request, "applications/analytics.html", context)


@login_required
@require_POST
def update_application_status(request, pk):
    try:
        data = json.loads(request.body)
        new_status = data.get("status")

        valid_statuses = [choice[0] for choice in Application.Status.choices]
        if new_status not in valid_statuses:
            return JsonResponse({"success": False, "error": "Invalid status"}, status=400)

        application = get_object_or_404(Application, pk=pk, user=request.user)
        application.status = new_status
        application.save(update_fields=["status", "updated_at"])

        return JsonResponse({"success": True})
        
    except (json.JSONDecodeError, Exception) as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@login_required
def application_detail_drawer(request, pk):
    application = get_object_or_404(
        Application.objects.select_related("company"), pk=pk, user=request.user
    )
    return render(
        request,
        "applications/partials/_application_drawer.html",
        {"app": application},
    )