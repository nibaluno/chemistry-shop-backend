from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from .models import Product, Category, Manufacturer, Review
import logging

logger = logging.getLogger(__name__) 

def product_list_view(request):
    products = Product.objects.all()
    

    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    
  
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
            
    return render(request, 'store/catalog.html', {'products': products})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


def product_create(request):
    if not request.user.is_superuser:
        logger.warning(f"Попытка доступа к созданию товара: {request.user}") 
        return HttpResponseNotFound("Доступ запрещен")
    
    if request.method == "POST":
        p = Product()
        p.name = request.POST.get("name")
        p.price = request.POST.get("price")
        p.stock = request.POST.get("stock")
        p.unit = request.POST.get("unit")
        p.category = Category.objects.get(id=request.POST.get("category"))
        p.manufacturer = Manufacturer.objects.get(id=request.POST.get("manufacturer"))
        p.save()
        logger.info(f"Товар {p.name} создан администратором {request.user}") 
        return redirect('product_list')
    
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    return render(request, 'store/product_form.html', {
        'categories': categories, 
        'manufacturers': manufacturers
    })

def product_edit(request, id):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    
    product = get_object_or_404(Product, id=id)
    
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.unit = request.POST.get("unit")
        product.save()
        logger.info(f"Товар {product.name} отредактирован админом {request.user}") # ЛОГ
        return redirect('product_detail', pk=product.id)
    
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    return render(request, 'store/product_form.html', {
        'product': product,
        'categories': categories,
        'manufacturers': manufacturers
    })

def product_delete(request, id):
    if not request.user.is_superuser:
        return HttpResponseNotFound("Доступ запрещен")
    product = get_object_or_404(Product, id=id)
    product.delete()
    logger.info(f"Товар удален админом {request.user}") # ЛОГ
    return redirect('product_list')

def add_review(request, product_id):
    if request.method == "POST" and request.user.is_authenticated:
        r = Review()
        r.product = Product.objects.get(id=product_id)
        r.user = request.user
        r.text = request.POST.get("text")
        r.rating = request.POST.get("rating")
        r.save()
        logger.info(f"Пользователь {request.user} оставил отзыв к товару") # ЛОГ
    return redirect('product_detail', pk=product_id)


def all_reviews_view(request):
    reviews = Review.objects.all().order_by('-date_added')
    return render(request, 'store/reviews.html', {'reviews': reviews})