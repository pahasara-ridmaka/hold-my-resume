import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from applications.models import Application, Platform


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
    badge_styles = {
        "linkedin": "bg-blue-50/60 text-blue-700",
        "indeed": "bg-amber-50/60 text-amber-700",
        "company website": "bg-emerald-50/60 text-emerald-700",
    }
    default_badge = "bg-neutral-50 text-neutral-700"

    sources_query = (
        user_apps.values("platform__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    top_sources = []
    for item in sources_query:
        p_name = item["platform__name"] or "Other / Direct"
        cnt = item["count"]
        pct = round(cnt / total_apps * 100) if total_apps > 0 else 0
        
        badge_class = badge_styles.get(p_name.lower(), default_badge)

        top_sources.append({
            "name": p_name,
            "count": cnt,
            "pct": pct,
            "badge_class": badge_class,
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
        "funnel": funnel,
        "top_sources": top_sources,
        "heatmap_weeks": heatmap_weeks,
        "total_active_days": total_active_days,
        "total_submissions": total_submissions,
    }

    if request.headers.get("HX-Request"):
        return render(
            request, "analytics/partials/_analytics_content.html", context
        )

    return render(request, "analytics/index.html", context)



@login_required
def export_analytics_csv(request):
    user = request.user
    user_apps = Application.objects.filter(user=user)

    # Aggregation
    metrics = user_apps.aggregate(
        total=Count("id"),
        interview=Count("id", filter=Q(status=Application.Status.INTERVIEWING)),
        offer=Count("id", filter=Q(status=Application.Status.OFFER)),
        applied=Count("id", filter=Q(status=Application.Status.APPLIED)),
    )

    total_apps = metrics["total"]
    interview_count = metrics["interview"]
    offer_count = metrics["offer"]
    in_review = metrics["applied"]
    responded_count = interview_count + offer_count

    response_rate = round((responded_count / total_apps * 100), 1) if total_apps > 0 else 0
    interview_rate = round((interview_count / total_apps * 100), 1) if total_apps > 0 else 0
    offer_rate = round((offer_count / total_apps * 100), 1) if total_apps > 0 else 0
    in_review_pct = round((in_review / total_apps * 100), 1) if total_apps > 0 else 0

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    filename = f"job_search_report_{timezone.localdate().strftime('%Y%m%d')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    def write_row_6col(col1="", col2="", col3="", col4="", col5="", col6=""):
        writer.writerow([col1, col2, col3, col4, col5, col6])

    # 1. Summary Header
    write_row_6col("=== JOB SEARCH ANALYTICS REPORT ===")
    write_row_6col("Generated For:", user.get_full_name() or user.username)
    write_row_6col("Generated Date:", timezone.localdate().strftime("%Y-%m-%d"))
    write_row_6col()

    # 2. Key Metrics
    write_row_6col("--- KEY METRICS ---")
    write_row_6col("Metric", "Value")
    write_row_6col("Total Applications", total_apps)
    write_row_6col("Response Rate", f"{response_rate}%")
    write_row_6col("Interview Rate", f"{interview_rate}% ({interview_count} active)")
    write_row_6col("Offer Rate", f"{offer_rate}% ({offer_count} secured)")
    write_row_6col()

    # 3. Conversion Funnel
    write_row_6col("--- CONVERSION FUNNEL ---")
    write_row_6col("Stage", "Count", "Percentage")
    write_row_6col("Total Applied", total_apps, "100%")
    write_row_6col("In Review / Queue", in_review, f"{in_review_pct}%")
    write_row_6col("Interview Stages", interview_count, f"{interview_rate}%")
    write_row_6col("Offers Secured", offer_count, f"{offer_rate}%")
    write_row_6col()

    # 4. Detailed Applications Table
    write_row_6col("--- DETAILED APPLICATIONS LOG ---")
    writer.writerow([
        "ID",
        "Company Name",
        "Role / Position",
        "Platform",
        "Applied Date",
        "Status",
    ])

    for app in user_apps.order_by("-applied_date"):
        # Company name fallback
        company = getattr(app, 'company', None) or "N/A"
        # Role fallback
        position = getattr(app, 'job_title', None) or "N/A"
        # Platform display fallback
        platform = (
            app.get_platform_display()
            if hasattr(app, "get_platform_display")
            else getattr(app, "platform", None) or "N/A"
        )
        # Date fallback
        applied_date = (
            app.applied_date.strftime("%Y-%m-%d")
            if getattr(app, "applied_date", None)
            else "N/A"
        )
        # Status display fallback
        status = (
            app.get_status_display()
            if hasattr(app, "get_status_display")
            else getattr(app, "status", None) or "N/A"
        )

        writer.writerow([
            app.id,
            company,
            position,
            platform,
            applied_date,
            status,
        ])

    return response