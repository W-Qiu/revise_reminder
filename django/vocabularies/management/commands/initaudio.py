from django.core.management.base import BaseCommand

from vocabularies.models import Vocab

import os
import socket

server_addr = (os.environ.get("TTS_SERVICE_SERVICE_HOST"),
               int(os.environ.get("TTS_SERVICE_SERVICE_PORT")))
sock = socket.create_connection(server_addr)

class Command(BaseCommand):
    help = "Initialize all audio files for every word in the DB."

    def handle(self, *args, **options):
        print("Initializing audio files based on vocabs")
        for query in Vocab.objects.all():
            sock.send(str.encode(query.word))
            response = sock.recv(1024)
            print(f"{query.word} - {response.decode()}")
        
        sock.close()
