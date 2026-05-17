from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import CustomUser
from .forms import CustomUserCreationForm
from services.api_services import get_cat_fact, get_random_joke
import logging 

logger = logging.getLogger(__name__) 

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"Зарегистрирован новый пользователь") 
            return redirect('login')
        else:
            logger.warning(f"Ошибка регистрации: {form.errors}") 
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"Пользователь {user.username} успешно вошел в систему.") 
            return redirect('profile')
        else:
            logger.warning(f"Неудачная попытка входа: {request.POST.get('username')}") 
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        logger.info(f"Пользователь вышел из системы.") 
        return redirect('login')
    return redirect('home')

@login_required
def profile_view(request):
    cat_fact = get_cat_fact()
    random_joke = get_random_joke()
    return render(request, 'users/profile.html', {
        'cat_fact': cat_fact,
        'random_joke': random_joke
    })

@login_required
def client_list_view(request):
    if request.user.role != 'employee' and not request.user.is_superuser:
        logger.warning(f"Несанкционированный доступ к списку клиентов: {request.user}") 
        return HttpResponseForbidden("Доступ запрещен. Только для сотрудников.")
    
    clients = CustomUser.objects.filter(role='buyer')
    return render(request, 'users/client_list.html', {'clients': clients})

@login_required
def client_detail_view(request, pk):
    if request.user.role != 'employee' and not request.user.is_superuser:
        logger.warning(f"Несанкционированный доступ к деталям клиента: {request.user}")
        return HttpResponseForbidden("Доступ запрещен. Только для сотрудников.")
    
    client_user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'users/client_detail.html', {'client_user': client_user})