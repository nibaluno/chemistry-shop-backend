from django.contrib import admin
from .models import Order, OrderItem, PromoCode


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'created_at', 'status', 'delivery_date')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(PromoCode)
admin.site.register(OrderItem)