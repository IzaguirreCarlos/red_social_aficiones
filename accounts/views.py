from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings

from .forms import UserRegisterForm


def _persist_session(request):
    """Asegura que la cookie de sesión persista 30 días aunque el navegador
    cierre, sin depender del comportamiento por defecto del cliente."""
    request.session.set_expiry(getattr(settings, 'SESSION_COOKIE_AGE', 60 * 60 * 24 * 30))


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)         # auto-login tras registro
            _persist_session(request)    # cookie persistente
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('posts:feed')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            _persist_session(request)
            return redirect('posts:feed')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
