from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps 
from .models import User
# Create your views here.

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('403') 
        return _wrapped_view
    return decorator


def home(request):
    return render(request, 'index.html')


def forbidenpage(request):
    return render(request, '401.html')


def loginuser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')


            if '@' in login_input:
                try:
                    # Get the user by email
                    user = User.objects.get(email=login_input)
                    username = user.username
                except User.DoesNotExist:
                    messages.error(request, "Invalid email or password.")
                    return render(request, 'login.html', {'form': form})
            else:
                username = login_input  # Treat as username

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if user.role == "ADMIN":
                    return redirect('admin-home')
                elif user.role == "Money Collector":
                    return redirect('money-collector-home')
                else:
                    return redirect('403')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.er# This logs out the userror(request, "Invalid form submission.")
    else:
        form = LoginForm()  
    return render(request, 'login.html', {'form': form})

@login_required
def logoutuser(request):
    logout(request)  # This logs out the user
    return redirect('home')

@role_required(['ADMIN'])
def adminhome(request):
    return render(request, 'adminn/index.html')


@role_required(['Money Collector'])
def mcollectorhome(request):
    return render(request, 'mcollector/index.html')


def empty(request):
    return render(request, 'adminn/empty.html')






