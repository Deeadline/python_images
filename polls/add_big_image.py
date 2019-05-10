from django.shortcuts import render, redirect
from polls.utils.couchdb_server import *


def add_big_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        images_doc = server['big_image']
        server.put_attachment(images_doc, image, 'big_image.png', 'image/png')
        server.commit()
        return redirect('home')
    return render(request, 'add_image.html')
