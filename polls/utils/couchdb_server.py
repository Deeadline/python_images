from couchdb import Server

main_connection = Server('http://test:test@127.0.0.1:5984/')
server = main_connection['images']
