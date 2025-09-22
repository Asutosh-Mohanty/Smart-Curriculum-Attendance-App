from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


@login_required
def dashboard(request):
    user = request.user
    
    # Determine user role and redirect to appropriate dashboard
    if hasattr(user, 'student'):
        return redirect('students:dashboard')
    elif hasattr(user, 'teacher'):
        return redirect('teachers:dashboard')
    elif user.is_staff:
        return redirect('admins:dashboard')
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('core:login')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:login')