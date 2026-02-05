from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from urllib3 import request
from django.contrib import messages

from .models import CustomUser,AccountUser, CounselorProfile, Appointment

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_conseiller'),
        }),
    )
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_conseiller', 'is_active']

    def save_model(self, request, obj, form, change):
        if obj.email:
            obj.username = obj.email
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AccountUser)

class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'description')
    search_fields = ('user__username', 'user__email')

    def save_model(self, request, obj, form, change):
        if not obj.user.is_conseiller:
            messages.error(request, f"Impossible : l'utilisateur '{obj.user.username}' n'a pas le statut 'conseiller' (is_conseiller=False).")
            return 
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Optionnel : filtrer la liste des users dans le formulaire admin
        if 'user' in form.base_fields:
            form.base_fields['user'].queryset = CustomUser.objects.filter(is_conseiller=True)
        return form

admin.site.register(CounselorProfile, CounselorProfileAdmin)

# Admin pour Appointment
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'conseiller', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('client__username', 'conseiller__user__username')

admin.site.register(Appointment, AppointmentAdmin)