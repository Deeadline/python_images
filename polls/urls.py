from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_images/', views.add_images, name='add_images'),
    path('add_image/', views.add_image, name='add_image'),
    path('display_image/', views.display_image, name='display_image'),
]
