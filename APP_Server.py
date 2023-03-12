import socket
import time

import requests
from scapy.all import *
import os
from PIL import Image,ImageSequence
from scapy.layers.inet import IP, TCP, UDP

RUDP_MAX_SIZE = 62000
SERVER_ADDRESS = ("127.0.0.10",30493)


class RUDP(Packet):
    name = "RUDP"
    fields_desc = [
        ShortField("src_port", 80),
        ShortField("dst_port", 80),
        IntField("seq_num", 0),
        IntField("ack_num", 0),
        FlagsField("flags", 0, 8, ['S', 'A', 'F']),
        ShortField("window", 8192),
        ShortField("checksum", None),
        ShortField("urgent_ptr", 0),
        StrField("payload", "")
    ]


memes = [
    ('https://speech.protocommunications.com/wp-content/uploads/2018/03/frustrated-meme.png','frustrated_meme.png'),
    ('https://media.wired.com/photos/5f87340d114b38fa1f8339f9/master/w_1600,c_limit/Ideas_Surprised_Pikachu_HD.jpg','surprised_meme.png'),
    ('https://m.media-amazon.com/images/I/61k7AtBBAVS._AC_SL1327_.jpg','angry_meme.png'),
    ('https://i.imgflip.com/639z7.jpg','stoned_meme.png'),
    ('https://cache.lovethispic.com/uploaded_images/blogs/10-Happy-Memes-To-Help-Your-Day-Feel-A-Whole-Lot-Better-50193-3.jpg','happy_meme.png'),
    ('https://scontent.ftlv19-1.fna.fbcdn.net/v/t1.6435-9/46310761_1843365659095168_484399811940843520_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=8bfeb9&_nc_ohc=MPsSPM_c_g0AX8dRueG&_nc_ht=scontent.ftlv19-1.fna&oh=00_AfB0gYkK9MEn3wqhISclfum7Kk-LZrhA-X9QhUnTW8ibng&oe=64340756','bored_meme.png'),
    ('https://pbs.twimg.com/media/DXJnAlSU8AAzPl-?format=jpg&name=900x900','nerd_meme.png')
]


def tcp_listen():
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(SERVER_ADDRESS)
    while True:
        tcp_server_socket.listen()
        client_socket , client_address = tcp_server_socket.accept()
        tcp_connection(client_socket , client_address)


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


def get_image(meme_num):
    return requests.get(memes[int(meme_num)][0])

    # if our_meme.status_code == 200:
    #     image = Image.open('/home/assaf/PycharmProjects/FinalEx/Object.g')
    #      return image
    # else:
    #     print("failed to download the image")


def rudp_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDRESS)
    sock.settimeout(1.5)

    # Wait for SYN packet from client
    syn_received = False
    pkt = RUDP()
    client_address = None
    while not syn_received:
        time.sleep(0.3)
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == 'S':
            syn_received = True
            client_address = addr


    # Send SYN-ACK packet to client
    seq_num = 0
    ack_num = pkt.seq_num + 1
    syn_ack_packet = RUDP(dst_port=pkt.src_port,src_port=SERVER_ADDRESS[1], flags=['S','A'], seq_num=seq_num, ack_num=ack_num)
    time.sleep(0.2)
    sock.sendto(bytes(syn_ack_packet),client_address)
    print(syn_ack_packet.show())
    # Wait for ACK packet from client
    ack_image_received = False
    while not ack_image_received:
        # time.sleep(0.1)
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == 'A' :
            ack_num += len(data)
            ack_image_received = True
    seq_num = pkt.ack_num
    image_to_send = get_image(pkt.payload)
    img_size = len(image_to_send.content)
    chunk_size = RUDP_MAX_SIZE - 4000
    start_idx = 0
    end_idx = chunk_size
    while start_idx < img_size:
        # Send packet with image data
        pkt = RUDP(dst_port=pkt.dst_port, seq_num=start_idx+seq_num, ack_num=ack_num, payload=image_to_send[start_idx:end_idx])
        sock.sendto(bytes(pkt),client_address)

        # Wait for ACK packet from client
        ack_received = False
        while not ack_received:
            data, addr = sock.recvfrom(RUDP_MAX_SIZE)
            pkt = RUDP(data)
            if pkt.flags == 'A' and pkt.ack_num == end_idx:
                ack_received = True

        # Update indexes for next chunk
        start_idx = end_idx
        end_idx += chunk_size

    # Wait for FIN request packet from client
    fin_requested = False
    while not fin_requested:
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == "F":
            fin_requested = True

    # Send FIN packet to client
    fin_packet = RUDP(dst_port=client_address[1], flags="FA", seq_num=start_idx, ack_num=ack_num)
    sock.sendto(bytes(fin_packet),client_address)
    fin_ack = False
    while not fin_ack:
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == 'A':
            fin_received = True


if __name__ == '__main__':
    # tcp_listen()
    rudp_connection()


