import socket
import requests
from scapy.all import *
import os
from PIL import Image,ImageSequence
from scapy.layers.inet import IP, TCP

RUDP_MAX_SIZE = 64000
SERVER_ADDRESS = ("127.0.0.2",30493)

memes = [
    ('https://speech.protocommunications.com/wp-content/uploads/2018/03/frustrated-meme.png','frustrated_meme.png'),
    ('https://media.wired.com/photos/5f87340d114b38fa1f8339f9/master/w_1600,c_limit/Ideas_Surprised_Pikachu_HD.jpg','surprised_meme.png'),
    ('https://www.happierhuman.com/wp-content/uploads/2022/06/anger-meme-littlenivi-come-here-you.jpg','angry_meme.png'),
    ('https://i.imgflip.com/639z7.jpg','stoned_meme.png'),
    ('https://cache.lovethispic.com/uploaded_images/blogs/10-Happy-Memes-To-Help-Your-Day-Feel-A-Whole-Lot-Better-50193-3.jpg','happy_meme.png'),
    ('https://scontent.ftlv19-1.fna.fbcdn.net/v/t1.6435-9/46310761_1843365659095168_484399811940843520_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=8bfeb9&_nc_ohc=MPsSPM_c_g0AX8dRueG&_nc_ht=scontent.ftlv19-1.fna&oh=00_AfB0gYkK9MEn3wqhISclfum7Kk-LZrhA-X9QhUnTW8ibng&oe=64340756','bored_meme.png'),
    ('https://pbs.twimg.com/media/DXJnAlSU8AAzPl-?format=jpg&name=900x900','nerd_meme.png')
]



# def get_Object():
#     our_giff = requests.get(url)
#     if  our_giff.status_code == 200:
#         with open("wb") as giff:
#             giff.write(our_giff.content)
#             gif = Image.open('/home/assaf/PycharmProjects/FinalEx/Object.gif')
#
#     else:
#         print("failed to download the gif")


def tcp_listen():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    while(True):
        server_socket.listen()
        client_socket , address = server_socket.accept()
        tcp_connection(client_socket , address)


def tcp_connection(client_socket,address):
    data = b''
    data += client_socket.recv(1024)
    print("after getting the url request")
    index = data.decode('utf-8')
    print(int(index))
    message = memes[int(index)][0]
    print(message)

    client_socket.sendall(message.encode('utf-8'))
    # client_socket.close()


if __name__ == '__main__':
        tcp_listen()

