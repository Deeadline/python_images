import io
import json
import base64
from django.shortcuts import render, redirect
from .couchdb_server import CouchDb
from PIL import Image
from .forms import *

db = CouchDb()  # replace test:test with your login:password


def home(request):
    return render(request, 'home.html')


# Dodajemy po kolei obrazki do CouchDB (potrzebne do generowania duzego obrazka
def add_images(request):
    if request.method == 'POST':
        multiple_img = request.FILES.getlist('photos_multiple')
        for i in range(len(multiple_img)):
            db.put_attachment(multiple_img[i], 'image' + str(i), 'image/png')
            db.save()
        return redirect('home')
    form = ImageForm()
    return render(request, 'add_images.html', {'form': form})


# Dodajemy tutaj jeden obrazek do naszego CouchDB (ten ktory bedziemy generowac z mniejszych obrazkow)
def add_image(request):
    if request.method == 'POST':
        image = request.FILES.get('photo')
        db.put_attachment(image, 'converted_image', 'image/png')
        db.save()
        return redirect('home')
    else:
        form = ImageForm()
    return render(request, 'add_image.html', {'form': form})


# Wyswietlamy nasz duzy obrazek stworzony z mniejszych.
# xd
def display_image(request):
    if request.method == 'GET':

        attachments_db = json.dumps(db.get_images_attachments())
        attachments_as_json = json.loads(attachments_db)
        attachments = []
        attachments2 = []
        big_file = db.get_attachment('converted_image')
        img_coll_arr = []
        # bierzemy wszystkie klucze rozne od converted_image i pobieramy zalaczniki
        for (k, v) in attachments_as_json.items():
            if k != 'converted_image':
                attachments.append(db.get_attachment(k))
                attachments2.append(db.get_attachment(k))
        complete_image = []
        img_width, img_height = 0, 0

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
            width, height = big.size
            img_width = width
            img_height = height
            area = width * height
            complete_image2 = [[0 for x in range(width)] for y in range(height)]
            for i in range(width):
                for j in range(height):
                    r, g, b = 0, 0, 0
                    for ix in range(1, width):
                        for iy in range(1, height):
                            tr, tg, tb = rgb_im.getpixel((width * i + ix, height * j + iy))
                            r, g, b = r + tr, g + tg, b + tb
                    r, g, b = r / area, g / area, b / area
                    index = 0
                    minimum_from_images = compare_images((r, g, b), img_coll_arr[0])
                    for ix in range(len(attachments)):
                        temp_min = compare_images((r, g, b), img_coll_arr[ix])
                        if temp_min < minimum_from_images:
                            minimum_from_images = temp_min
                            index = ix
                    complete_image2[i][j] = index
            complete_image = complete_image2

        images = []
        for i in range(len(attachments)):  # tutaj ile obrazkow wgralismy (zeby zrobic kafelki)
            image = Image.open(attachments2[i])
            image.thumbnail(
                (img_width, img_height))  # wielkosc kazdego obrazka ktory  bedzie wstawiony do nowego mozaikowego
            images.append(image)
        # wielkosc obrazka źródłowego żeby nie było na sztywno
        # przekazac parametrem z frontendu(html) rozmiar koncowego zdjęcia i rozmiar małych zdjec
        # widok
        new_image = Image.new('RGB', (4900, 4900), 'BLACK')  # rozmiar pliku wyjściowego

        for i in range(img_width):  # podajemy rozmiary obrazków tych małych (kafelki)
            for j in range(img_height):
                new_image.paste(images[complete_image[i][j]], (i * img_width, j * img_height + j))
        image_io = io.BytesIO()
        new_image.save(image_io, 'PNG')
        db.put_attachment(image_io.getvalue(), 'new_image', 'image/png')
        # response = db.get_attachment('new_image')
        # src = "data:image/png;base64,{0}".format(base64.b64encode(response.content))
        return render(request, 'display_image.html',
                      {'image': 'http://images_db_user:pass@localhost:5984/images/image/new_image'})  #


def compare_images(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
