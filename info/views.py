import calendar
import zoneinfo
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.utils import timezone 
from .models import News, CompanyInfo, GlossaryTerm, Contact, Vacancy, PrivacyPolicy
from store.models import Review
import logging 
from django.contrib.auth.decorators import user_passes_test


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import News, CompanyInfo, GlossaryTerm, Contact, Vacancy, PrivacyPolicy, Partner
from store.models import Review, Product


logger = logging.getLogger(__name__)

#«Главная: ... каталог услуг/ товаров/ продуктов и т.д., 
# наименование и краткая информация о последней опубликованной статье 
# (статьи должны быть в базе данных), список компаний партнеров 
# + их логотипы со ссылками на сайты компаний – выбрать произвольно 
# и добавить таблицу в базу данных»

def home_view(request):
    latest_news = News.objects.order_by('-date_published').first()
    products = Product.objects.all()[:6]
    partners = Partner.objects.filter(is_active=True)
    company = CompanyInfo.objects.first()

    now_utc = timezone.now()
    tz_name = request.user.timezone if request.user.is_authenticated else 'Europe/Minsk'
    
  
    try:
        now_local = now_utc.astimezone(zoneinfo.ZoneInfo(tz_name))
    except:
        now_local = now_utc 
    

    cal = calendar.TextCalendar(firstweekday=0)
    month_cal = cal.formatmonth(now_local.year, now_local.month)
    
    return render(request, 'info/home.html', {
        'latest_news': latest_news,
        'products': products,
        'partners': partners,
        'company': company,
        'now_utc': now_utc,
        'now_local': now_local,
        'month_cal': month_cal,
        'tz_name' : tz_name
    })


def about_view(request):
    company = CompanyInfo.objects.first()
    return render(request, 'info/about.html', {'company': company})

#«Контакты(таблица в базе данных): 
# Фото сотрудников с описанием выполняемых работ, телефонами, почтой и т.д.»
def contacts_view(request):
    contacts = Contact.objects.all()
    return render(request, 'info/contacts.html', {'contacts': contacts})

#«Вакансии(таблица в базе данных): список вакансий с описанием»
def vacancies_view(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'info/vacancies.html', {'vacancies': vacancies})

#«Политика конфиденциальности: в соответствии с тематикой разработанного сайта»
def privacy_view(request):
    policy = PrivacyPolicy.objects.first()
    return render(request, 'info/privacy.html', {'policy': policy})


#Отзывы(таблица в базе данных): 
# список отзывов с указанием имени(логин оставившего отзыв),
#  оценки, текста, даты. Кнопка добавить отзыв
#  с переходом к окну регистрации или в личный 
# кабинет залогиненного пользователя. 
# При нажатии кнопки открытие формы с полем для текста 
# отзыва и выбора оценки, кнопкой «Отправить», 
# которая сохраняет отзыв в базе. 

def reviews_view(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/users/login/?next=/reviews/%3Fadd%3D1%23review-form')

        product_id = request.POST.get('product')
        text = request.POST.get('text', '').strip()
        rating = request.POST.get('rating')

        if product_id and text and rating:
            try:
                product = Product.objects.get(pk=product_id)
                Review.objects.create(
                    product=product,
                    user=request.user,
                    text=text,
                    rating=int(rating),
                )
                messages.success(request, 'Отзыв успешно сохранён в базе данных.')
                logger.info(f"Пользователь {request.user} оставил отзыв на странице /reviews/")
            except (Product.DoesNotExist, ValueError):
                messages.error(request, 'Не удалось сохранить отзыв. Проверьте данные.')
        else:
            messages.error(request, 'Заполните все поля: товар, оценка и текст отзыва.')
        return redirect('/reviews/#review-form')

    reviews = Review.objects.select_related('user', 'product').order_by('-date_added')
    products = Product.objects.all().order_by('name')
    open_form = request.GET.get('add') == '1'

    return render(request, 'info/reviews.html', {
        'reviews': reviews,
        'products': products,
        'open_form': open_form,
    })


#«Новости(таблица в базе данных): список статей в соответствии с тематикой сайта 
# с заголовком, кратким содержанием (одно предложение), картинкой и кнопкой 
# «Читать далее» при нажатии на которую открывается вся статья»
def news_list_view(request):
    news_list = News.objects.all()
    return render(request, 'info/news_list.html', {'news_list': news_list})

#«Словарь 
# терминов и понятий(таблица в базе данных):
#  список часто-задаваемых вопросов с датой добавления на сайт,
#  при нажатии на которые открывается развернутый ответ»
def news_detail_view(request, year, slug):
    news_item = get_object_or_404(News, slug=slug, date_published__year=year)
    
    return render(request, 'info/news_detail.html', {'news_item': news_item})

def is_admin(user):
    """
    Проверяет, является ли пользователь администратором.
    Возвращает True или False.
    Эту функцию использует декоратор @user_passes_test.
    """
    return user.is_authenticated and user.is_superuser

def glossary_index(request):
    terms = GlossaryTerm.objects.all()
    return render(request, "info/glossary.html", {"terms": terms})

@user_passes_test(is_admin, login_url='/login/')
def glossary_create(request):
    if request.method == "POST":
        term_obj = GlossaryTerm()
        term_obj.term = request.POST.get("term")
        term_obj.definition = request.POST.get("definition")
        term_obj.save()
        logger.info(f"Создан новый термин: {term_obj.term}") 
    return HttpResponseRedirect("/glossary/")

@user_passes_test(is_admin, login_url='/login/')
def glossary_edit(request, id):
    try:
        term_obj = GlossaryTerm.objects.get(id=id)
        if request.method == "POST":
            term_obj.term = request.POST.get("term")
            term_obj.definition = request.POST.get("definition")
            term_obj.save()
            logger.info(f"Отредактирован термин: {term_obj.term}")
            return HttpResponseRedirect("/glossary/")
        else:
            return render(request, "info/glossary_edit.html", {"term_obj": term_obj})
    except GlossaryTerm.DoesNotExist:
        logger.warning(f"Попытка редактирования несуществующего термина с id={id}")
        return HttpResponseNotFound("<h2>Термин не найден</h2>")
     

@user_passes_test(is_admin, login_url='/login/')
def glossary_delete(request, id):
    try:
        term_obj = GlossaryTerm.objects.get(id=id)
        term_obj.delete()
        logger.info(f"Удален термин с id={id}")
        return HttpResponseRedirect("/glossary/")
    except GlossaryTerm.DoesNotExist:
        logger.warning(f"Попытка удаления несуществующего термина с id={id}")
        return HttpResponseNotFound("<h2>Термин не найден</h2>")