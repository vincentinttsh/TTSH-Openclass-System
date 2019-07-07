from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('class/secondary/', include('public_class_secondary.urls')),
    path('class/high/', include('public_class_high.urls')),
    path('account/', include('account.urls')),
    path('auth/', include('social_django.urls'), name='social'),
]
