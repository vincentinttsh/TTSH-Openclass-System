from django.urls import path
from . import views

urlpatterns = [
    path('privacy', views.privacy),
    path('terms', views.terms),
    path('about', views.about),
]