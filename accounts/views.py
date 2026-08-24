from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('applications:application_list')

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        # 1. LOGIN LOGIC
        if action_type == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('applications:application_list')
            else:
                messages.error(request, 'Invalid username or password.')

        # 2. REGISTER LOGIC
        elif action_type == 'register':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                login(request, user)
                return redirect('applications:application_list')

    return render(request, 'accounts/auth.html')

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")

            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Refresh"] = "true"
                return response

            return redirect("accounts:profile_settings")
        else:
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "accounts/partials/_profile_settings_drawer.html",
                    {"form": form, "user": user},
                    status=422, 
                )
    else:
        form = ProfileUpdateForm(instance=user)

    context = {
        "form": form,
        "user": user,
    }

    if request.headers.get("HX-Request"):
        return render(request, "accounts/partials/_profile_settings_drawer.html", context)

    return render(request, "accounts/index.html", context)



@login_required
def change_password(request):

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            profile_form = ProfileUpdateForm(instance=user)
            response = render(request, "accounts/partials/_profile_settings_drawer.html", {"form": profile_form, "user": user})
            response["HX-Trigger"] = "passwordChanged"
            return response
    else:
        form = PasswordChangeForm(user=request.user)



    return render(request, "accounts/partials/_password_change_drawer.html", {"form": form})