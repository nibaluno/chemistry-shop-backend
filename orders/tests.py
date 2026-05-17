import pytest
from django.urls import reverse
from .models import PromoCode, Order, OrderItem
from store.models import Product, Category, Manufacturer
from users.models import CustomUser
from datetime import date

@pytest.mark.django_db
def test_order_item_auto_price():
    """Проверяем, что цена автоматически подтягивается из товара (метод save)"""
    man = Manufacturer.objects.create(name="TestMan", country="Test")
    cat = Category.objects.create(name="TestCat", slug="test-cat")
    prod = Product.objects.create(name="Товар", price=500, category=cat, manufacturer=man, unit='шт')
    user = CustomUser.objects.create_user(username="testuser")
    order = Order.objects.create(client=user, delivery_date=date.today())
    
    item = OrderItem.objects.create(order=order, product=prod, quantity=1)
    
    assert item.price_at_purchase == 500

@pytest.mark.django_db
def test_promo_crud(client, admin_user):
    """Проверка создания, редактирования и удаления промокода"""
    client.force_login(admin_user)
    
    
    client.post(reverse('promocode_create'), {
        'code': 'SAVE10', 'discount': 10, 'expiry_date': '2025-12-31'
    })
    assert PromoCode.objects.filter(code='SAVE10').exists()
    
    promo = PromoCode.objects.get(code='SAVE10')
    client.post(reverse('promocode_edit', args=[promo.id]), {
        'code': 'SAVE20', 'discount': 20, 'expiry_date': '2025-12-31', 'is_active': 'on'
    })
    promo.refresh_from_db()
    assert promo.discount == 20
    
    client.post(reverse('promocode_delete', args=[promo.id]))
    assert PromoCode.objects.count() == 0

@pytest.mark.django_db
def test_admin_dashboard_access(client, admin_user, buyer_user):
    client.force_login(admin_user)
    response = client.get(reverse('admin_dashboard'))
    assert response.status_code == 200
    
    client.force_login(buyer_user)
    response = client.get(reverse('admin_dashboard'))
    assert response.status_code == 404 


@pytest.mark.django_db
def test_home_view(client):
    """Тест главной страницы"""
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'month_cal' in response.context 