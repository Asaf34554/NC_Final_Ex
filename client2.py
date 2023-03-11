import random
from io import BytesIO
import socket
import requests
from scapy.all import *
from scapy.layers.inet import IP, TCP
from PIL import Image,ImageSequence

CLIENT_ADDRESS = ('127.0.0.20',20454)
SERVER_ADDRESS = ("127.0.0.2",30493)


def get_meme(url):
    our_meme = requests.get(url)
    image_meme = our_meme.content
    image = Image.open(BytesIO(image_meme))
    image.show()


def connect_tcp():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.bind(CLIENT_ADDRESS)
    client_socket.connect(SERVER_ADDRESS)
    # message = str(random.randint(0,6))
    message = "2"
    client_socket.sendall(message.encode('utf-8'))
    print("After sending the request url")
    url_data = b''

    url_data += client_socket.recv(1048)

    print(f"after the while\n{url_data.decode()}")
    get_meme(url_data.decode())

    client_socket.close()

# def redirect():
#

if __name__ == '__main__':
    connect_tcp()