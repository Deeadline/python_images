import io
import json
from django.shortcuts import render, redirect
from couchdb import Server
from PIL import Image
from .forms import *

server = Server('http://images_db_user:pass@127.0.0.1:5984/')  # replace test:test with your login:password


def home(request):
    return render(request, 'home.html')


# Dodajemy po kolei obrazki do CouchDB (potrzebne do generowania duzego obrazka
def add_images(request):
    if request.method == 'POST':
        images_db = server['images']
        images_doc = images_db['image']
        multiple_img = request.FILES.getlist('photos_multiple')
        for i in range(len(multiple_img)):
            images_db.put_attachment(images_doc, multiple_img[i], 'image' + str(i), 'image/png')
            images_db.commit()
        return redirect('home')
    form = ImageForm()
    return render(request, 'add_images.html', {'form': form})


# Dodajemy tutaj jeden obrazek do naszego CouchDB (ten ktory bedziemy generowac z mniejszych obrazkow)
def add_image(request):
    if request.method == 'POST':
        images_db = server['images']
        images_doc = images_db['image']
        image = request.FILES.get('photo')
        images_db.put_attachment(images_doc, image, 'converted_image', 'image/png')
        images_db.commit()
        return redirect('home')
    else:
        form = ImageForm()
    return render(request, 'add_image.html', {'form': form})


# Wyswietlamy nasz duzy obrazek stworzony z mniejszych.
# xd
def display_image(request):
    if request.method == 'GET':
        images_db = server['images']
        images_doc = images_db['image']
        attachments_db = json.dumps(images_doc['_attachments'])
        attachments_as_json = json.loads(attachments_db)
        attachments = []
        attachments2 = []
        big_file = images_db.get_attachment(images_doc, 'converted_image')
        img_coll_arr = []
        # bierzemy wszystkie klucze rozne od converted_image i pobieramy zalaczniki
        for (k, v) in attachments_as_json.items():
            if k != 'converted_image':
                attachments.append(images_db.get_attachment(images_doc, k))
                attachments2.append(images_db.get_attachment(images_doc, k))
        complete_image = [[0 for x in range(70)] for y in range(70)]

        for i in range(len(attachments)):  # ile obrazkow wgralismy
            with Image.open(attachments[i]) as img:
                width, height = img.size
                r, g, b = 0, 0, 0
                rgb_im = img.convert('RGB')
                for w in range(1, width):
                    for h in range(1, height):
                        tr, tg, tb = rgb_im.getpixel((w, h))
                        r, g, b = r + tr, g + tg, b + tb
                area = width * height
                r, g, b = r / area, g / area, b / area
                img_coll_arr.append((r, g, b))

        with Image.open(big_file) as big:
            rgb_im = big.convert('RGB')
            for i in range(70):
                for j in range(70):
                    r, g, b = 0, 0, 0
                    for ix in range(1, 70):
                        for iy in range(1, 70):
                            tr, tg, tb = rgb_im.getpixel((70 * i + ix, 70 * j + iy))
                            r, g, b = r + tr, g + tg, b + tb
                    r, g, b = r / 4900, g / 4900, b / 4900
                    index = 0
                    minimum_from_images = compare_images((r, g, b), img_coll_arr[0])
                    for ix in range(32):
                        temp_min = compare_images((r, g, b), img_coll_arr[ix])
                        if temp_min < minimum_from_images:
                            minimum_from_images = temp_min
                            index = ix
                    complete_image[i][j] = index

        images = []
        for i in range(len(attachments)):  # tutaj ile obrazkow wgralismy (zeby zrobic kafelki)
            image = Image.open(attachments2[i])
            image.thumbnail((70, 70))  # wielkosc kazdego
            images.append(image)

        new_image = Image.new('RGB', (4900, 4900), 'BLACK')  # rozmiar pliku wyjściowego

        for i in range(70):  # podajemy rozmiary obrazków tych małych (kafelki)
            for j in range(70):
                new_image.paste(images[complete_image[i][j]], (i * 70, j * 70 + j))
        image_io = io.BytesIO()
        new_image.save(image_io, 'PNG')
        images_db.put_attachment(images_doc, image_io.getvalue(), 'new_image', 'image/png')
        return render(request, 'display_image.html', {'image': 'http://localhost:5984/images/image/new_image'})


def compare_images(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
