import pytest
from django.urls import reverse
from django.utils import timezone
from .models import News, GlossaryTerm, Vacancy


@pytest.mark.django_db
def test_glossary_term_creation():
    """Тест создания объекта GlossaryTerm"""
    term = GlossaryTerm.objects.create(term="API", definition="Application Programming Interface")
    assert term.term == "API"
    assert term.definition == "Application Programming Interface"
    assert term.date_added is not None

@pytest.mark.django_db
def test_news_creation():
    """Тест создания новости"""
    news = News.objects.create(
        title="Тестовая новость",
        slug="test-news",
        short_content="Кратко",
        full_content="Подробно",
        date_published=timezone.now()
    )
    assert news.slug == "test-news"




@pytest.fixture
def create_test_data(db):
    """Фикстура для создания данных перед тестами URL"""
    GlossaryTerm.objects.create(term="TestTerm", definition="TestDef")
    Vacancy.objects.create(title="Менеджер", description="Требуется менеджер", is_active=True)


@pytest.mark.django_db
@pytest.mark.parametrize("url_name, expected_status", [
    ('home', 200),
    ('about', 200),
    ('contacts', 200),
    ('vacancies', 200),
    ('privacy', 200),
    ('glossary', 200),
    ('reviews_info', 200),
    ('news_list', 200),
])
def test_public_urls_status_codes(client, create_test_data, url_name, expected_status):
    """
    Параметризованный тест.
    Проверяет, что все публичные страницы отдают HTTP 200 (ОК).
    Это заменяет 8 отдельных функций тестирования.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == expected_status



@pytest.mark.django_db
def test_glossary_create_post(client):
    """Тест: функция glossary_create (Create)"""
    url = reverse('glossary_create')
    response = client.post(url, {
        'term': 'Django',
        'definition': 'Веб-фреймворк на Python'
    })
    
    assert response.status_code == 302
    assert response.url == '/glossary/'
    
    assert GlossaryTerm.objects.filter(term='Django').exists()


@pytest.mark.django_db
def test_glossary_edit_post(client):
    """Тест: функция glossary_edit (Update)"""
    term = GlossaryTerm.objects.create(term="Old", definition="Old text")
    
    url = reverse('glossary_edit', args=[term.id])
    response = client.post(url, {
        'term': 'New',
        'definition': 'New text'
    })
    
    assert response.status_code == 302
    
    term.refresh_from_db()
    assert term.term == 'New'
    assert term.definition == 'New text'


@pytest.mark.django_db
def test_glossary_delete_post(client):
    """Тест: функция glossary_delete (Delete)"""
    term = GlossaryTerm.objects.create(term="To Delete", definition="Text")
    
    url = reverse('glossary_delete', args=[term.id])
    response = client.post(url)
    
    assert response.status_code == 302
    assert GlossaryTerm.objects.filter(id=term.id).count() == 0


@pytest.mark.django_db
def test_news_detail_url(client):
    """Тест регулярного выражения в news_detail"""
    news = News.objects.create(
        title="Важная новость",
        slug="vazhnaya-novost",
        short_content="Кратко",
        full_content="Подробно"
    )
    
    year = news.date_published.strftime('%Y')
    url = reverse('news_detail', kwargs={'year': year, 'slug': news.slug})
    
    response = client.get(url)
    assert response.status_code == 200
    assert "Важная новость" in str(response.content.decode('utf-8'))
