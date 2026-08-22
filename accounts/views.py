from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('applications:list')

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        # 1. LOGIN LOGIC
        if action_type == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('applications:list')
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
                return redirect('applications:list')

    return render(request, 'accounts/auth.html')