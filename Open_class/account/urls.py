from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('create/', views.Create.as_view()),
    path('login/', views.login),
    path('parttimelogin/', auth_views.LoginView.as_view()),
    path('logout/', auth_views.LogoutView.as_view()),
]