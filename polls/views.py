from django.http import HttpResponse
from django.shortcuts import render, redirect
from couchdb import Server
import json
from PIL import Image
from .forms import *

server = Server('http://test:test@127.0.0.1:5984/')  # replace test:test with your login:password


def home(request):
    return render(request, 'home.html')


# Dodajemy po kolei obrazki do CouchDB (potrzebne do generowania duzego obrazka0
def add_images(request):
    if request.method == 'POST':
        images_db = server['images']
        images_doc = images_db['image']
        multiple_img = request.FILES.getlist('photos_multiple')
        count = len(multiple_img)
        for i in range(count):
            images_db.put_attachment(images_doc, multiple_img[i], 'image' + str(i), 'image/png')
            images_db.commit()
        return redirect('home')
    else:
        form = ImageForm()
    return render(request, 'add_images.html', {'form': form})


# Dodajemy tutaj jeden obrazek do naszego CouchDB (ten ktory bedziemy generowac z mniejszych obrazkow)
def add_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        images_db = server['images']
        images_doc = images_db['image']
        images_db.put_attachment(images_doc, form['image'].value(), 'converted_image', 'image/png')
        images_db.commit()
        return redirect('home')
    else:
        form = ImageForm()
    return render(request, 'add_image.html', {'form': form})


# Wyswietlamy nasz duzy obrazek stworzony z mniejszych.
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
        complete_image = [[0 for x in range(8)] for y in range(8)]

        for i in range(8):
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
            for i in range(8):
                for j in range(8):
                    r, g, b = 0, 0, 0
                    for ix in range(1, 32):
                        for iy in range(1, 32):
                            tr, tg, tb = rgb_im.getpixel((32 * i + ix, 32 * j + iy))
                            r, g, b = r + tr, g + tg, b + tb
                    r, g, b = r / 1024, g / 1024, b / 1024
                    index = 0
                    minimum_from_images = compare_images((r, g, b), img_coll_arr[0])
                    for ix in range(8):
                        temp_min = compare_images((r, g, b), img_coll_arr[ix])
                        if temp_min < minimum_from_images:
                            minimum_from_images = temp_min
                            index = ix
                    complete_image[i][j] = index

        images = []
        for i in range(8):
            image = Image.open(attachments2[i])
            image.thumbnail((32, 32))
            images.append(image)

        new_image = Image.new('RGB', (256, 256), 'BLACK')

        for i in range(8):
            for j in range(8):
                new_image.paste(images[complete_image[i][j]], (i * 32, j * 32 + j))
        response = HttpResponse(content_type="image/png")
        new_image.save(response, 'PNG')
        return response


def compare_images(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
