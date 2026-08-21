import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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



def application_list(request):
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
        }
    return render_htmx(request, 'applications/partials/_application_content.html', context=context)


def dashboard(request):
    context = {'stats': ...}
    return render_htmx(request, 'applications/partials/_dashboard_content.html', context=context)


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