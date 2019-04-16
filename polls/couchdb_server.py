from couchdb import Server, Database


class CouchDb:
    server: Server

    def __init__(self, url='http://images_db_user:pass@127.0.0.1:5984/'):
        self.server = Server(url)

    def save(self):
        self.server['images'].commit()

    def get_images_attachments(self):
        images_db = self.server['images']
        images_doc = images_db['image']
        return images_doc['_attachments']

    def put_attachment(self, image, title, content_type='image/png'):
        images_db = self.server['images']
        images_doc = images_db['image']
        images_db.put_attachment(images_doc, image, title, content_type)

    def get_attachment(self, title):
        images_db = self.server['images']
        images_doc = images_db['image']
        return images_db.get_attachment(images_doc, title)
