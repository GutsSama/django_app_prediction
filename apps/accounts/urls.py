from django import views
from django.urls import path
from apps.accounts.views import SignupView, CustomLoginView, ProfileView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('create-appointment/<int:conseiller_id>/', views.create_appointment, name='create_appointment'),
]




