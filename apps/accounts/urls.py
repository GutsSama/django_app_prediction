from django import views
from django.urls import path
from apps.accounts.views import SignupView, CustomLoginView, ProfileView, AppointmentView, CounselorAppointmentsView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('appointments/', AppointmentView.as_view(), name='appointments'),
    path('my-appointments/', CounselorAppointmentsView.as_view(), name='counselor_appointments'),
]




