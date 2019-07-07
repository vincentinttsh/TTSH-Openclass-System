from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('create/', views.create),
    path('login/', views.login),
    path('logout/', auth_views.LogoutView.as_view()),
]