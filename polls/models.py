from django.db import models


class ImageUpload(models.Model):
    description = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='images')
