from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AccountUser

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_conseiller'),
        }),
    )
    list_display = ['username', 'email', 'is_staff', 'is_conseiller']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AccountUser)