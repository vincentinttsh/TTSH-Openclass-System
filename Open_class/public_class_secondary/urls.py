from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('create/', views.create),
    path('attend/<int:no>/<str:password>/', views.attend),
    path('myclass', views.myclass),
    path('myobservation', views.myobservation),
    path('design/<int:no>', views.design_table),
    path('preparation/<int:no>',views.preparation),
    path('observation/<int:no>',views.observation),
    path('briefing/<int:no>',views.briefing),
]