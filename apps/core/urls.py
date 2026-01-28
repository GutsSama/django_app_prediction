from django.urls import path
from .views import AccueilView

urlpatterns = [
    path('', AccueilView.as_view(), name='accueil'),
]