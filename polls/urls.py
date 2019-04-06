from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('add_images/', add_images, name='add_images'),
    path('add_image/', add_image, name='add_image'),
    path('display_image/', display_image, name='display_image'),
]
