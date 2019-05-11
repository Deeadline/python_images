from django.shortcuts import render
from polls.utils.image_utils import *
from polls.utils.couchdb_server import *
from .forms import ShowImageForm


def show_image(request):
    if request.method == 'POST':
        form = ShowImageForm(request.POST)
        if form.is_valid():
            width, height = int(form.cleaned_data['width']), int(form.cleaned_data['height'])
            images_doc = server['big_image']
            # zmieniamy rozmiar naszego duzego obrazka
            old_width, old_height, new_image_name = resize_image(images_doc, 'big_image', width, height)

            complete_image = [[0 for _ in range(old_width)] for _ in range(old_height)]
            new_image = server.get_attachment(images_doc, new_image_name)

            complete_image = big_rgb_calculate(new_image, complete_image, width, height,
                                               old_width, old_height)

            view = server.view('images_db/rgb')

            images = get_images_from_view(view, width, height, complete_image)
            ia = Image.new('RGB', (old_width * width, old_height * height))
            for i in range(0, old_width):
                for j in range(0, old_height):
                    ia.paste(images[complete_image[i][j]], (i * width, j * height + j))

            image_io = io.BytesIO()
            ia.save(image_io, 'PNG')
            server.put_attachment(images_doc, image_io.getvalue(), 'mosaic', 'image/png')
            return render(request, 'show_image.html',
                          {'image': 'http://localhost:5984/images/big_image/mosaic', 'has_content': True})
    else:
        form = ShowImageForm()
        return render(request, 'show_image.html', {'has_content': False, 'form': form})
