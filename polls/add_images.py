from django.shortcuts import render, redirect
from polls.utils.image_utils import *


# Dodawanie paczki zdjęć, obliczanie rgb dla kazdego zdjęcia i zapisywanie tych danych do pojedynczego dokumentu.
def add_images(request):
    if request.method == 'POST':
        multiple_images = request.FILES.getlist('multiple_images')  # bierzemy wszystkie pliki
        images_count = len(multiple_images)  # przypisujemy sobie ile mamy plikow do wgrania
        for i in range(images_count):  # dla kazdego obrazka
            file_name = 'image{0}'.format(i)
            rgb, img = rgb_calculate(multiple_images[i], file_name)  # obliczamy sobie rgb
            server.save(rgb)  # zapisujemy sobie nasz dokument
            server.put_attachment(rgb, img, 'image.png',
                                  'image/png')  # i dodajemy do niego jeszcze nasze zdjecie
            server.commit()
        return redirect('add_images')
    return render(request, 'add_images.html')
