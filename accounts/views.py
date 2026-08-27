from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, UserRegistrationForm


def home_view(request):

    return redirect('applications:application_list') if request.user.is_authenticated else redirect('accounts:login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect(['applications:application_list'])

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('applications:application_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('applications:application_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('applications:application_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})




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