import os
import django
from datetime import date, timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from store.models import Category, Manufacturer, Product, Review
from orders.models import Order, OrderItem, PromoCode
from info.models import (
    News, Vacancy, Contact, CompanyInfo, CompanyHistory,
    GlossaryTerm, PrivacyPolicy, Partner
)


def _load_file_to_imagefield(instance, field_name, relative_path):
    """Загружает файл из static/ или media/ в ImageField модели."""
    full_path = os.path.join(settings.BASE_DIR, relative_path)
    if not os.path.exists(full_path):
        return False
    with open(full_path, 'rb') as f:
        filename = os.path.basename(relative_path)
        getattr(instance, field_name).save(filename, ContentFile(f.read()), save=True)
    return True


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

    # 4. Товары (10 штук + автоматическая загрузка product.png)
    product_names = [
        "Persil Color Mega Pack 3кг", "Fairy Platinum для посуды 900мл",
        "Domestos Ultra White 750мл", "Ariel Alpine 2.4кг", "Tide Alpine 2кг",
        "Sorti Color 400г", "Sanfor Oxy 750мл", "Vanish Oxi Action 500г",
        "Cif Cream Lemon 500мл", "Mr. Proper Лаванда 1л",
    ]
    products = []
    for i in range(10):
        p, created = Product.objects.get_or_create(
            name=product_names[i],
            defaults={
                'category': categories[i % len(categories)],
                'manufacturer': manufacturers[i % len(manufacturers)],
                'price': 100 + i * 20,
                'unit': 'шт',
                'stock': random.randint(50, 200)
            }
        )
        if not p.photo:
            _load_file_to_imagefield(p, 'photo', 'static/images/product.png')
        products.append(p)
    print("Создано/обновлено 10 товаров с изображениями (product.png).")

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

    # 6. Сотрудники и контакты (10 человек + автоматическая загрузка .png аватарок)
    positions = ["Менеджер", "Продавец", "Директор", "Бухгалтер", "Логист", 
                 "Кладовщик", "Водитель", "Уборщик", "Секретарь", "Юрист"]
    job_descriptions = [
        "Консультирование клиентов, оформление заказов, работа с CRM-системой.",
        "Приём и выкладка товара, консультирование покупателей на торговом зале.",
        "Общее руководство компанией, стратегическое планирование.",
        "Ведение бухгалтерского учёта, составление отчётности.",
        "Организация логистики, планирование маршрутов доставки.",
        "Приёмка, хранение и отгрузка товаров со склада.",
        "Доставка заказов клиентам по городу и области.",
        "Документооборот, приём звонков, организация совещаний.",
        "Юридическое сопровождение деятельности компании.",
        "Разработка рекламных кампаний, ведение соцсетей.",
    ]
    first_names = ["Иван", "Петр", "Сергей", "Анна", "Елена", "Мария", "Ольга", "Дмитрий", "Алексей", "Татьяна"]
    
    for i in range(10):
        emp_username = f"employee{i+1}"
        emp_user, created = CustomUser.objects.get_or_create(username=emp_username)
        if created:
            emp_user.set_password('123')
            emp_user.role = 'employee'
            emp_user.first_name = first_names[i]
            emp_user.last_name = f"Сотрудник_{i+1}"
            emp_user.save()
            
        contact, _ = Contact.objects.update_or_create(
            employee=emp_user,
            defaults={
                'position': positions[i],
                'job_description': job_descriptions[i],
                'phone': f'+375 (29) 111-22-{i+1}3',
                'email': f'emp{i+1}@himtorg.by',
            }
        )
        
        if not contact.photo:
            avatar_num = (i % 8) + 2  # от 2 до 9
            avatar_path = f"static/images/avatar-{avatar_num}.png"
            _load_file_to_imagefield(contact, 'photo', avatar_path)
            
    print("Создано 10 сотрудников, контактов и загружены аватары (.png).")

    # 7. Информация о компании и история успеха (1 запись + история)
    company, created = CompanyInfo.objects.get_or_create(
        defaults={
            'about_text': "Мы — лучший магазин бытовой химии в стране!",
            'requisites': "УНП 123456789, ЗАО 'ХимТорг'",
        }
    )
    if created:
        print("Информация о компании добавлена.")
    else:
        print("Информация о компании уже существует.")

    if not company.logo:
        _load_file_to_imagefield(company, 'logo', 'static/images/logo.png')

    history_events = [
        (2010, "Основание компании «ХимТорг» в г. Минске"),
        (2013, "Открытие первого интернет-магазина"),
        (2016, "Расширение ассортимента до 500 наименований"),
        (2019, "Запуск собственной службы доставки"),
        (2022, "Партнёрство с ведущими мировыми брендами"),
        (2025, "Более 10 000 постоянных клиентов"),
    ]
    
    if company.history.count() == 0:
        for year, event in history_events:
            CompanyHistory.objects.create(company=company, year=year, event=event)
        print("История успеха компании успешно добавлена.")
    else:
        print("История успеха уже существует, пропускаем.")

    # 8. Новости (10 штук)
    for i in range(10):
        news_item, created = News.objects.get_or_create(
            slug=f"novost-{i+1}",
            defaults={
                'title': f"Новость №{i+1}",
                'short_content': f"Краткое описание новости №{i+1} для теста.",
                'full_content': f"Полный текст новости №{i+1} с подробностями о жизни компании.",
            }
        )
    print("Создано 10 новостей.")

    # 9. Вакансии (10 штук)
    vac_titles = [
        "Менеджер по продажам", "Продавец-консультант", "Кладовщик", "Водитель-экспедитор",
        "Бухгалтер", "Логист", "Уборщик помещений", "Грузчик", "Администратор", "Специалист по закупкам"
    ]
    for i, title in enumerate(vac_titles):
        Vacancy.objects.get_or_create(
            title=title,
            defaults={'description': f"Требуется {title.lower()} на полный рабочий день. Опыт работы приветствуется."}
        )
    print("Создано 10 вакансий.")

    # 10. Словарь терминов и понятий (FAQ)
    faq_data = [
        ("Что такое ПАВ?", "ПАВ (поверхностно-активные вещества) — основной компонент моющих средств, который снижает поверхностное натяжение воды и помогает отмывать загрязнения."),
        ("Как выбрать стиральный порошок?", "Для белого белья выбирайте порошки с отбеливающими компонентами, для цветного — с маркировкой Color. Обратите внимание на тип ткани и температуру стирки."),
        ("Безопасны ли ваши средства для детей?", "Да, у нас есть специальная линейка гипоаллергенных средств с маркировкой «Безопасно для детей». Все продукты имеют сертификаты качества."),
        ("Как оформить заказ?", "Добавьте товары в корзину, перейдите к оплате, заполните адрес доставки и выберите способ оплаты. Заказ будет обработан в течение 1 рабочего дня."),
        ("Какие способы оплаты доступны?", "Мы принимаем оплату банковской картой, через ЕРИП и наличными при получении."),
        ("Как использовать промокод?", "Введите промокод в поле на странице оплаты. Скидка будет автоматически применена к сумме заказа."),
        ("Есть ли доставка за пределы Минска?", "Да, мы осуществляем доставку по всей Беларуси. Сроки и стоимость зависят от региона."),
        ("Как вернуть товар?", "Возврат возможен в течение 14 дней при сохранении товарного вида и упаковки. Обратитесь в службу поддержки."),
    ]
    for question, answer in faq_data:
        GlossaryTerm.objects.get_or_create(
            term=question,
            defaults={'definition': answer}
        )
    print("Словарь терминов и понятий (FAQ) создан.")

    # 11. Партнёры (.png логотипы)
    partners_data = [
        ("Henkel", "https://www.henkel.com", "static/images/partner-henkel.png"),
        ("Procter & Gamble", "https://www.pg.com", "static/images/partner-pg.png"),
        ("Unilever", "https://www.unilever.com", "static/images/partner-unilever.png"),
        ("Nefis", "https://www.nefis.ru", "static/images/partner-nefis.png"),
    ]
    for name, url, logo_path in partners_data:
        partner, created = Partner.objects.get_or_create(
            name=name,
            defaults={'website_url': url, 'is_active': True}
        )
        if not partner.logo:
            _load_file_to_imagefield(partner, 'logo', logo_path)
    print("Партнёры созданы и привязаны к .png логотипам.")

    # 12. Промокоды и купоны (действующие и в архиве)
    promos_data = [
        ("SUMMER2026", 15, True, date.today() + timedelta(days=90)),
        ("WELCOME10", 10, True, date.today() + timedelta(days=180)),
        ("CLEAN20", 20, True, date.today() + timedelta(days=30)),
        ("OLD2025", 25, False, date.today() - timedelta(days=30)),  # архивный (is_active=False)
        ("NEWYEAR", 30, False, date.today() - timedelta(days=60)),  # архивный (is_active=False)
    ]
    for code, discount, active, expiry in promos_data:
        PromoCode.objects.get_or_create(
            code=code,
            defaults={
                'discount': discount, 
                'is_active': active, 
                'expiry_date': expiry
            }
        )
    print("Промокоды и купоны созданы.")

    # 13. Заказы (10 штук)
    if Order.objects.count() == 0:
        buyers = list(CustomUser.objects.filter(role='buyer'))
        if buyers:
            for i in range(10):
                buyer = buyers[i % len(buyers)]
                order_date = timezone.now() - timedelta(days=random.randint(0, 180))
                order = Order.objects.create(
                    client=buyer, 
                    delivery_date=date.today() + timedelta(days=random.randint(1, 14))
                )
                order.created_at = order_date
                order.save()
                
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

    # 14. Отзывы покупателей (5 штук)
    review_texts = [
        (5, "Отличный магазин! Быстрая доставка, качественные товары."),
        (4, "Хороший ассортимент порошков и гелей. Рекомендую."),
        (5, "Заказываю регулярно — всегда всё в наличии."),
        (3, "Нормальный сервис, но хотелось бы больше акций."),
        (5, "Товары по отличной цене. Спасибо «ХимТорг»!"),
    ]
    buyers = list(CustomUser.objects.filter(role='buyer'))
    if buyers and products and Review.objects.count() < 5:
        for i, (rating, text) in enumerate(review_texts):
            Review.objects.get_or_create(
                product=products[i % len(products)],
                user=buyers[i % len(buyers)],
                defaults={'text': text, 'rating': rating}
            )
        print("Отзывы покупателей добавлены.")
    else:
        print("Отзывы уже существуют или нет покупателей/товаров.")

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
    print(f"FAQ терминов: {GlossaryTerm.objects.count()}")
    print(f"Партнёров: {Partner.objects.count()}")
    print(f"Промокодов: {PromoCode.objects.count()}")
    print(f"Отзывов: {Review.objects.count()}")
    print(f"Заказов: {Order.objects.count()}")
    print(f"Позиций в заказах: {OrderItem.objects.count()}")
    print(f"Записей в истории успеха: {CompanyHistory.objects.count()}")
    
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