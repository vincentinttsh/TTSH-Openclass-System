from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('create/', views.create.as_view()),
    path('attend/<int:no>/<str:password>/', views.attend.as_view()),
    path('myclass/', views.myclass.as_view()),
    path('myobservation/', views.myobservation.as_view()),
    path('design/create/<int:no>/', views.design_table_create.as_view()),
    path('design/view/<int:no>/', views.design_table_view.as_view()),
    path('preparation/create/<int:no>/',views.preparation_create.as_view()),
    path('preparation/view/<int:no>/',views.preparation_view.as_view()),
    path('observation/create/<int:no>/',views.observation_create.as_view()),
    path('observation/all/view/<int:no>/',views.observation_all_view.as_view()),
    path('observation/one/view/<int:no>/',views.observation_one_view.as_view()),
    path('briefing/create/<int:no>/',views.briefing_create.as_view()),
    path('briefing/view/<int:no>/',views.briefing_view.as_view()),
]