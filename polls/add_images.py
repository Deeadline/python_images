from django.shortcuts import render, redirect
from polls.utils.image_utils import *


# Dodawanie paczki zdjęć, obliczanie rgb dla kazdego zdjęcia i zapisywanie tych danych do pojedynczego dokumentu.
def add_images(request):
    if request.method == 'POST':
        multiple_images = request.FILES.getlist('multiple_images')  # bierzemy wszystkie pliki
        images_count = len(multiple_images)  # przypisujemy sobie ile mamy plikow do wgrania
        for i in range(images_count):  # dla kazdego obrazka
            print('multiple_images[{0}]:{1}'.format(i, multiple_images[i]))
            rgb = rgb_calculate(multiple_images[i])  # obliczamy sobie rgb
            server.save(rgb)  # zapisujemy sobie nasz dokument
            server.put_attachment(rgb, multiple_images[i], 'image.png',
                                  'image/png')  # i dodajemy do niego jeszcze nasze zdjecie
        return redirect('add_images')
    return render(request, 'add_images.html')
