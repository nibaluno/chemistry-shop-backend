import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import CustomUser, validate_age_18


@pytest.mark.parametrize("birth_date, should_fail", [
    (date.today() - timedelta(days=365*20), False), 
    (date.today() - timedelta(days=365*17), True),  
])
def test_validate_age_18(birth_date, should_fail):
    if should_fail:
        with pytest.raises(ValidationError):
            validate_age_18(birth_date)
    else:
        validate_age_18(birth_date)

@pytest.mark.django_db
def test_user_flow(client):
    """Тест регистрации и входа в систему"""
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='password123',
        role='buyer'
    )
    assert CustomUser.objects.filter(username='testuser').exists()
    
    login_success = client.login(username='testuser', password='password123')
    assert login_success is True 
    
    response = client.get(reverse('profile'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_client_list_access(client, admin_user, buyer_user):
    client.force_login(admin_user)
    response = client.get(reverse('client_list'))
    assert response.status_code == 200
    
    client.force_login(buyer_user)
    response = client.get(reverse('client_list'))
    assert response.status_code == 403

@pytest.mark.django_db
def test_login_logout(client):
    """Тест входа и выхода"""
    CustomUser.objects.create_user(username='user1', password='pw')
    
    client.login(username='user1', password='pw')
    response = client.post(reverse('logout'))
    assert response.status_code == 302

@pytest.mark.django_db
def test_login_logout_views(client):
    """Тест входа и выхода через функции views"""
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    
    client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
    response = client.post(reverse('logout'))
    assert response.status_code == 302