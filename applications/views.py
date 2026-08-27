import json
import mimetypes
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse, JsonResponse
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
        Application.objects.select_related("company", "platform"), pk=pk, user=request.user
    )
    return render(
        request,
        "applications/partials/_application_drawer.html",
        {"app": application},
    )



@login_required
def view_resume(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.user != request.user and not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Permission denied"}, status=400)
    if not application.resume_file:
        return JsonResponse({"success": False, "error": "No resume file found"}, status=404)

    content_type, _ = mimetypes.guess_type(application.resume_file.name)

    return FileResponse(
        application.resume_file.open("rb"),
        content_type=content_type or 'application/pdf',
        as_attachment=False,

    )


@login_required
def view_cover_letter(request, pk):
    application = get_object_or_404(Application, pk=pk)


    if application.user != request.user and not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Permission denied"}, status=400)
    if not application.cover_letter_file:
        return JsonResponse({"success": False, "error": "No cover letter file found"}, status=404)

    content_typpe, _ = mimetypes.guess_type(application.cover_letter_file.name)


    return FileResponse(
        application.cover_letter_file.open("rb"),
        content_type=content_typpe or 'application/pdf',
        as_attachment=False,
    )
