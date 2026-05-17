import pytest
from django.urls import reverse
from .models import Product, Category, Manufacturer

# 1. ТЕСТИРОВАНИЕ МОДЕЛЕЙ
@pytest.mark.django_db
def test_product_creation():
    """Тест создания товара"""
    man = Manufacturer.objects.create(name="Henkel", country="Германия")
    cat = Category.objects.create(name="Порошки", slug="poroshki")
    product = Product.objects.create(
        name="Test Powder", 
        category=cat, 
        manufacturer=man, 
        price=100.00, 
        unit='шт', 
        stock=10
    )
    assert product.name == "Test Powder"
    assert product.price == 100.00

# 2. ТЕСТИРОВАНИЕ CRUD ТОВАРОВ (Админ доступ)
@pytest.mark.django_db
def test_product_crud(client, admin_user):
    """Тестируем создание и удаление товара через view"""
    client.force_login(admin_user)
    man = Manufacturer.objects.create(name="Test", country="Test")
    cat = Category.objects.create(name="Test", slug="test")
    
    # Create
    client.post(reverse('product_create'), {
        'name': 'New Product',
        'price': 200,
        'stock': 5,
        'unit': 'шт',
        'category': cat.id,
        'manufacturer': man.id
    })
    assert Product.objects.filter(name='New Product').exists()
    
    # Delete
    prod = Product.objects.get(name='New Product')
    client.post(reverse('product_delete', args=[prod.id]))
    assert Product.objects.count() == 0

# 3. ПАРАМЕТРИЗОВАННЫЙ ТЕСТ ФИЛЬТРАЦИИ И ПОИСКА
@pytest.mark.django_db
@pytest.mark.parametrize("search_query, expected_count", [
    ("Порошок", 1), # Товар с таким именем есть
    ("Гель", 0),    # Товаров с таким именем нет
])
def test_product_search(client, search_query, expected_count):
    """
    Параметризованный тест поиска. 
    Проверяет фильтрацию в product_list_view.
    """
    man = Manufacturer.objects.create(name="Test", country="Test")
    cat = Category.objects.create(name="Test", slug="test")
    Product.objects.create(name="Порошок", price=100, category=cat, manufacturer=man, unit='шт')
    
    response = client.get(reverse('product_list'), {'search': search_query})
    assert len(response.context['products']) == expected_count

# 4. ТЕСТ ДОСТУПА К ДЕТАЛЯМ ТОВАРА
@pytest.mark.django_db
def test_product_detail_view(client):
    man = Manufacturer.objects.create(name="Test", country="Test")
    cat = Category.objects.create(name="Test", slug="test")
    prod = Product.objects.create(name="Detail", price=10, category=cat, manufacturer=man, unit='шт')
    
    response = client.get(reverse('product_detail', args=[prod.pk]))
    assert response.status_code == 200
    assert "Detail" in str(response.content)


@pytest.mark.django_db
def test_product_list_view_filters(client):
    """Тест поиска и сортировки в catalog"""
    man = Manufacturer.objects.create(name="Henkel", country="Германия")
    cat = Category.objects.create(name="Порошки", slug="poroshki")
    Product.objects.create(name="Ариэль", price=100, category=cat, manufacturer=man, unit='шт')
    Product.objects.create(name="Тайд", price=200, category=cat, manufacturer=man, unit='шт')

    # Тест поиска
    response = client.get(reverse('product_list'), {'search': 'Ариэль'})
    assert len(response.context['products']) == 1
    
    # Тест сортировки
    response = client.get(reverse('product_list'), {'sort': 'price_desc'})
    assert response.context['products'][0].name == 'Тайд'