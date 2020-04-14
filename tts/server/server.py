import os
import socket
import re

from synthesizer import Synthesizer
from utils.generic_utils import load_config

app_path = os.path.dirname(os.path.abspath("__file__"))
model_path = os.path.join(app_path, "checkpoint/")
server_path = os.path.join(app_path, "server/")

config = load_config(os.path.join(server_path, "conf.json"))
synthesizer = Synthesizer()
synthesizer.load_model(model_path, config.model_name,
                       config.model_config, config.use_cuda)

"""
open socket for TCP connection with Django
Docker has a problem with forwarding UDP packet to the right interface
"""
server_addr = ("", 
               int(os.environ.get("TTS_SERVICE_SERVICE_PORT")))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(server_addr)
sock.listen(5)

audio_path = os.path.join(server_path, "audio/")

cache = {}
for filename in os.listdir(audio_path):
    cache[filename] = True

while True:
    # establish connection
    print(f"waiting for connection...")
    conn, client_addr = sock.accept()

    # connected
    try:
        print(f"connection from {client_addr}")
        while True:
            data = conn.recv(int(os.environ.get("BUFFER_SIZE")))
            # receiving data
            if data:
                try:
                    word, flag = data.decode().split(":")
                except ValueError:
                    word = data.decode()
                    flag = None
                
                print(f"received input: {word} flag: {flag}")

                # check cache
                if f"{word}.wav" in cache:
                    print("in cache, ignore")
                    conn.send(str.encode("Exists"))
                    continue

                # regex pattern to skip special chars
                if re.findall('[^0-9A-Za-z- ]', word):
                    print(f"special charater(s) detected, ignore")
                    conn.send(str.encode("Special Char Error!"))
                    continue

                # synthesizing and add to cache
                synthesizer.tts(word, audio_path+f"{word}.wav")
                cache[f"{word}.wav"] = True
                conn.send(str.encode("Added"))

            # transmission completed
            else:
                print(f"Transmission from {client_addr} has finished.")
                break
    finally:
        conn.close()
