from django.urls import path

from .show_image import *
from .add_images import *
from .add_big_image import *
from .home import *

urlpatterns = [
    path('', home, name='home'),
    path('add_images/', add_images, name='add_images'),
    path('add_image/', add_big_image, name='add_big_image'),
    path('show/', show_image, name='show_image'),
]
