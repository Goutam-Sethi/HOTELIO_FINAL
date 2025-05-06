from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser, Property, Booking

class AppUserAdmin(UserAdmin):
    model = AppUser
    list_display = ('email', 'name', 'phone', 'is_staff', 'is_superuser')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2'),
        }),
    )

admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Property)
admin.site.register(Booking)