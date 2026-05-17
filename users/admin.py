from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'city')
    list_filter = ('role', 'city', 'is_staff', 'is_superuser')
    search_fields = ('username', 'phone', 'email', 'city')

    fieldsets = UserAdmin.fieldsets + (
        ('Информация профиля', {
            'fields': ('role', 'phone', 'birth_date', 'address', 'city', 'avatar', 'timezone'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Информация профиля', {
            'fields': ('role', 'phone', 'birth_date', 'city'),
        }),
    )