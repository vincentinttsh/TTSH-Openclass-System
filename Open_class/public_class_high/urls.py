from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('create/', views.create.as_view()),
    path('attend/<int:no>/<str:password>/', views.attend.as_view()),
    path('myclass', views.myclass.as_view()),
    path('myobservation', views.myobservation.as_view()),
    path('design/<int:no>', views.design_table.as_view()),
    path('preparation/<int:no>',views.preparation.as_view()),
    path('observation/<int:no>',views.observation.as_view()),
    path('observation/all/<int:no>',views.observation_all.as_view()),
    path('observation/person/<int:no>',views.observation_person.as_view()),
    path('briefing/<int:no>',views.briefing.as_view()),
]