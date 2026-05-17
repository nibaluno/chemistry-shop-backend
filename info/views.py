import calendar
import zoneinfo
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.utils import timezone 
from .models import News, CompanyInfo, GlossaryTerm, Contact, Vacancy, PrivacyPolicy
from store.models import Review
import logging 


logger = logging.getLogger(__name__)


def home_view(request):
    latest_news = News.objects.order_by('-date_published').first()
    

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
        'now_utc': now_utc,
        'now_local': now_local,
        'month_cal': month_cal,
    })


def about_view(request):
    company = CompanyInfo.objects.first()
    return render(request, 'info/about.html', {'company': company})

def contacts_view(request):
    contacts = Contact.objects.all()
    return render(request, 'info/contacts.html', {'contacts': contacts})

def vacancies_view(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'info/vacancies.html', {'vacancies': vacancies})

def privacy_view(request):
    policy = PrivacyPolicy.objects.first()
    return render(request, 'info/privacy.html', {'policy': policy})

def reviews_view(request):
    reviews = Review.objects.all()
    return render(request, 'info/reviews.html', {'reviews': reviews})


def news_list_view(request):
    news_list = News.objects.all()
    return render(request, 'info/news_list.html', {'news_list': news_list})

def news_detail_view(request, year, slug):
    news_item = get_object_or_404(News, slug=slug, date_published__year=year)
    
    return render(request, 'info/news_detail.html', {'news_item': news_item})



def glossary_index(request):
    terms = GlossaryTerm.objects.all()
    return render(request, "info/glossary.html", {"terms": terms})

def glossary_create(request):
    if request.method == "POST":
        term_obj = GlossaryTerm()
        # Достаем данные из POST-запроса вручную!
        term_obj.term = request.POST.get("term")
        term_obj.definition = request.POST.get("definition")
        term_obj.save()
        logger.info(f"Создан новый термин: {term_obj.term}") # ЛОГ
    return HttpResponseRedirect("/glossary/")

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
     
def glossary_delete(request, id):
    try:
        term_obj = GlossaryTerm.objects.get(id=id)
        term_obj.delete()
        logger.info(f"Удален термин с id={id}")
        return HttpResponseRedirect("/glossary/")
    except GlossaryTerm.DoesNotExist:
        logger.warning(f"Попытка удаления несуществующего термина с id={id}")
        return HttpResponseNotFound("<h2>Термин не найден</h2>")