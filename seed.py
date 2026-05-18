import os
import django
from datetime import date, timedelta
from django.utils import timezone

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from store.models import Category, Manufacturer, Product
from orders.models import Order, OrderItem
from info.models import News, Vacancy, Contact, CompanyInfo

def run_seed():
    print("Начинаем наполнение базы данных...")

    if not CustomUser.objects.filter(username='kate').exists():
        CustomUser.objects.create_superuser(
            username='kate', 
            password='123', 
            email='kate@admin.com',
            role='employee'
        )
        print("Суперпользователь 'kate' создан.")
    else:
        print("Суперпользователь 'kate' уже существует.")

    cat1, _ = Category.objects.get_or_create(slug="poroshki", defaults={'name': "Порошки"})
    cat2, _ = Category.objects.get_or_create(slug="geli", defaults={'name': "Гели"})
    man, _ = Manufacturer.objects.get_or_create(name="Henkel", defaults={'country': "Германия"})

   
    if Product.objects.count() == 0:
        products = []
        for i in range(15):
            p = Product.objects.create(
                name=f"Товар №{i+1}",
                category=cat1 if i % 2 == 0 else cat2,
                manufacturer=man,
                price=100 + i*10,
                unit='шт',
                stock=100
            )
            products.append(p)
        print("Создано 15 товаров.")
    else:
        products = list(Product.objects.all())


    cities = ["Минск", "Брест", "Гродно", "Витебск", "Гомель", "Могилев"]
    for i in range(12):
        username = f"buyer{i}"
        user, created = CustomUser.objects.get_or_create(username=username)
        if created:
            user.set_password('123')
            user.role = 'buyer'
            user.city = cities[i % len(cities)]
            user.first_name = "Клиент"
            user.last_name = f"Тестовый_{i+1}"
            user.save()
    print("Создано 12 покупателей.")


    positions = ["Менеджер", "Продавец", "Директор"]
    for i in range(3):
        emp_username = f"employee{i}"
        emp_user, created = CustomUser.objects.get_or_create(username=emp_username)
        if created:
            emp_user.set_password('123')
            emp_user.role = 'employee'
            emp_user.first_name = "Иван"
            emp_user.last_name = f"Сотрудник_{i+1}"
            emp_user.save()
            
            Contact.objects.get_or_create(
                employee=emp_user,
                defaults={
                    'position': positions[i],
                    'phone': f'+375 (29) 111-22-3{i}',
                    'email': f'emp{i}@company.com',
                    'photo': 'contacts/-9.jpg' 
                }
            )
    print("Создано 3 сотрудника и их контактные карточки.")

    if not CompanyInfo.objects.exists():
        CompanyInfo.objects.create(
            about_text="Мы — лучший магазин бытовой химии в стране!",
            requisites="УНП 123456789, ЗАО 'ХимТорг'",
           
            logo='company/f9876904d16fa734c312715150f40317.jpg' 
        )
        print("Информация о компании добавлена.")


    for i in range(3):
        News.objects.get_or_create(
            slug=f"novost-{i+1}",
            defaults={
                'title': f"Новость №{i+1}",
                'short_content': "Краткое описание новости для теста.",
                'full_content': "Полный текст новости с подробностями."
            }
        )
    print("Создано 3 новости.")


    for i in range(3):
        Vacancy.objects.get_or_create(
            title=f"Вакансия №{i+1}",
            defaults={'description': "Требуется сотрудник на полный рабочий день."}
        )
    print("Создано 3 вакансии.")


    if Order.objects.count() == 0:
        buyer = CustomUser.objects.filter(role='buyer').first()
        for i in range(6):
            order_date = timezone.now() - timedelta(days=i * 30)
            order = Order.objects.create(client=buyer, delivery_date=date.today() + timedelta(days=5))
            
  
            order.created_at = order_date
            order.save()
            
        
        import random # добавьте импорт в начало
        for p in products[:3]:
            random_price = p.price * (0.8 + random.random() * 0.4) 
            OrderItem.objects.create(
                order=order, 
                product=p, 
                quantity=random.randint(1, 5), # Разное количество
                price_at_purchase=random_price
            )
        print("Заказы за 6 месяцев созданы.")
    else:
        print("Заказы уже существуют (пропуск, чтобы избежать дублирования в аналитике).")
    
    print("База наполнена успешно!")

if __name__ == '__main__':
    run_seed()