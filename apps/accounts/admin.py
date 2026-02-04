from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,AccountUser, CounselorProfile, Appointment

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

class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'description')  # Affiche l'utilisateur et la description
    search_fields = ('user__username', 'user__email')

admin.site.register(CounselorProfile, CounselorProfileAdmin)

# Admin pour Appointment
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'conseiller', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('client__username', 'conseiller__user__username')

admin.site.register(Appointment, AppointmentAdmin)