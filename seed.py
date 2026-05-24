import os
import django
from datetime import date, timedelta
from django.utils import timezone
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from store.models import Category, Manufacturer, Product
from orders.models import Order, OrderItem
from info.models import News, Vacancy, Contact, CompanyInfo

def run_seed():
    print("Начинаем наполнение базы данных...")

    # 1. Создание суперпользователя (1 запись)
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

    # 2. Категории (10 штук)
    categories = []
    cat_names = ["Порошки", "Гели", "Мыло", "Шампуни", "Кондиционеры", 
                 "Средства для мытья посуды", "Чистящие средства", "Освежители воздуха", 
                 "Отбеливатели", "Пятновыводители"]
    for i, name in enumerate(cat_names[:10], 1):
        cat, _ = Category.objects.get_or_create(
            slug=f"cat-{i}",
            defaults={'name': name}
        )
        categories.append(cat)
    print(f"Создано {len(categories)} категорий.")

    # 3. Производители (10 штук)
    manufacturers = []
    man_data = [
        ("Henkel", "Германия"),
        ("Procter & Gamble", "США"),
        ("Unilever", "Великобритания"),
        ("Nefis", "Россия"),
        ("Amway", "США"),
        ("Clorox", "США"),
        ("Reckitt", "Великобритания"),
        ("SC Johnson", "США"),
        ("Church & Dwight", "США"),
        ("Kao", "Япония"),
    ]
    for name, country in man_data:
        man, _ = Manufacturer.objects.get_or_create(name=name, defaults={'country': country})
        manufacturers.append(man)
    print(f"Создано {len(manufacturers)} производителей.")

    # 4. Товары (10 штук)
    if Product.objects.count() == 0:
        products = []
        for i in range(10):
            p = Product.objects.create(
                name=f"Товар №{i+1}",
                category=categories[i % len(categories)],
                manufacturer=manufacturers[i % len(manufacturers)],
                price=100 + i * 20,
                unit='шт',
                stock=random.randint(50, 200)
            )
            products.append(p)
        print("Создано 10 товаров.")
    else:
        products = list(Product.objects.all())

    # 5. Покупатели (10 человек)
    cities = ["Минск", "Брест", "Гродно", "Витебск", "Гомель", "Могилев", "Гродно", "Бобруйск", "Пинск", "Орша"]
    for i in range(10):
        username = f"buyer{i+1}"
        user, created = CustomUser.objects.get_or_create(username=username)
        if created:
            user.set_password('123')
            user.role = 'buyer'
            user.city = cities[i % len(cities)]
            user.first_name = "Клиент"
            user.last_name = f"Тестовый_{i+1}"
            birth_year = date.today().year - random.randint(18, 65)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            user.birth_date = date(birth_year, birth_month, birth_day)
            user.save()
    print("Создано 10 покупателей.")

    # 6. Сотрудники и контакты (10 человек)
    positions = ["Менеджер", "Продавец", "Директор", "Бухгалтер", "Логист", 
                 "Кладовщик", "Водитель", "Уборщик", "Секретарь", "Юрист"]
    for i in range(10):
        emp_username = f"employee{i+1}"
        emp_user, created = CustomUser.objects.get_or_create(username=emp_username)
        if created:
            emp_user.set_password('123')
            emp_user.role = 'employee'
            emp_user.first_name = ["Иван", "Петр", "Сергей", "Анна", "Елена", 
                                   "Мария", "Ольга", "Дмитрий", "Алексей", "Татьяна"][i]
            emp_user.last_name = f"Сотрудник_{i+1}"
            emp_user.save()
            
            Contact.objects.get_or_create(
                employee=emp_user,
                defaults={
                    'position': positions[i],
                    'phone': f'+375 (29) 111-22-{i}3',
                    'email': f'emp{i+1}@company.com',
                    'photo': 'contacts/default.jpg'
                }
            )
    print("Создано 10 сотрудников и их контактные карточки.")

    # 7. Информация о компании (1 запись)
    if not CompanyInfo.objects.exists():
        CompanyInfo.objects.create(
            about_text="Мы — лучший магазин бытовой химии в стране!",
            requisites="УНП 123456789, ЗАО 'ХимТорг'",
            logo='company/logo.jpg'
        )
        print("Информация о компании добавлена.")

    # 8. Новости (10 штук)
    for i in range(10):
        news_item, created = News.objects.get_or_create(
            slug=f"novost-{i+1}",
            defaults={
                'title': f"Новость №{i+1}",
                'short_content': f"Краткое описание новости №{i+1} для теста.",
                'full_content': f"Полный текст новости №{i+1} с подробностями о жизни компании.",
                'image': f'news/{i+1}.jpg'
            }
        )
    print("Создано 10 новостей.")

    # 9. Вакансии (10 штук)
    vac_titles = [
        "Менеджер по продажам", "Продавец-консультант", "Кладовщик", "Водитель-экспедитор",
        "Бухгалтер", "Логист", "Уборщик помещений", "Грузчик", "Администратор", "Специалист по закупкам"
    ]
    for i in range(10):
        Vacancy.objects.get_or_create(
            title=vac_titles[i],
            defaults={'description': f"Требуется {vac_titles[i].lower()} на полный рабочий день. Опыт работы приветствуется."}
        )
    print("Создано 10 вакансий.")

    # 10. Заказы (10 штук)
    if Order.objects.count() == 0:
        buyers = list(CustomUser.objects.filter(role='buyer'))
        if buyers:
            # Создаём 10 заказов с разными датами
            for i in range(10):
                buyer = buyers[i % len(buyers)]
                order_date = timezone.now() - timedelta(days=random.randint(0, 180))
                order = Order.objects.create(
                    client=buyer, 
                    delivery_date=date.today() + timedelta(days=random.randint(1, 14))
                )
                order.created_at = order_date
                order.save()
                
                # Добавляем в заказ от 1 до 5 случайных товаров
                num_items = random.randint(1, 5)
                selected_products = random.sample(products, min(num_items, len(products)))
                
                for p in selected_products:
                    quantity = random.randint(1, 10)
                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        quantity=quantity,
                        price_at_purchase=p.price
                    )
            
            print("Создано 10 заказов со случайными товарами.")
        else:
            print("Нет покупателей для создания заказов.")
    else:
        print("Заказы уже существуют, пропускаем создание.")

    # ИТОГОВАЯ СТАТИСТИКА
    print("\n" + "="*50)
    print("СТАТИСТИКА ПОСЛЕ ЗАПОЛНЕНИЯ:")
    print("="*50)
    print(f"Категорий: {Category.objects.count()}")
    print(f"Производителей: {Manufacturer.objects.count()}")
    print(f"Товаров: {Product.objects.count()}")
    print(f"Покупателей: {CustomUser.objects.filter(role='buyer').count()}")
    print(f"Сотрудников: {CustomUser.objects.filter(role='employee').count()}")
    print(f"Контактов: {Contact.objects.count()}")
    print(f"Новостей: {News.objects.count()}")
    print(f"Вакансий: {Vacancy.objects.count()}")
    print(f"Заказов: {Order.objects.count()}")
    print(f"Позиций в заказах: {OrderItem.objects.count()}")
    
    # Выручка по товарам
    total_revenue = 0
    print("\n📊 ВЫРУЧКА ПО ТОВАРАМ:")
    for p in Product.objects.all():
        revenue = sum(item.quantity * item.price_at_purchase for item in p.orderitem_set.all())
        if revenue > 0:
            total_revenue += revenue
            print(f"  {p.name}: продано {p.orderitem_set.count()} позиций, выручка {revenue:.2f} руб.")
    
    print(f"\n💰 ОБЩАЯ ВЫРУЧКА: {total_revenue:.2f} руб.")
    
    print("\n✅ База наполнена успешно!")

if __name__ == '__main__':
    run_seed()