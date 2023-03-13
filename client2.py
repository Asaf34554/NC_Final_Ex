import time

from io import BytesIO
import socket
import requests
from scapy.all import *
from scapy.layers.inet import IP, TCP
from PIL import Image
from termcolor import colored

global IMG_COUNTER
IMG_COUNTER = 0
CLIENT_ADDRESS = ('127.0.0.2',20454)
SERVER_ADDRESS = ("127.0.0.10",30493)
RUDP_MAX_SIZE = 62000


class RUDP(Packet):
    name = "RUDP"
    fields_desc = [
        ShortField("src_port", 20454),
        ShortField("dst_port", 80),
        IntField("seq_num", 0),
        IntField("ack_num", 0),
        FlagsField("flags", 0, 8, ['S', 'A', 'F']),
        ShortField("window", 8192),
        ShortField("checksum", None),
        ShortField("urgent_ptr", 0),
        StrField("message", "")
    ]


def rudp_connecet(msg_num):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(CLIENT_ADDRESS)
    # sock.settimeout(1.5)
    pkt = RUDP(src_port = CLIENT_ADDRESS[1],flags = "S",seq_num = 0)
    sock.sendto(bytes(pkt),SERVER_ADDRESS)
    ack_syn_received = False
    ack_num=0
    while not ack_syn_received:
        # time.sleep(0.2)
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == ['S','A'] and pkt.seq_num == 0:
            ack_num += 1
            ack_syn_received = True
    print(pkt.show())

    pkt_new = RUDP(message=msg_num,seq_num=pkt.seq_num + 1, ack_num=ack_num, dst_port=pkt.src_port, flags='A')
    print(pkt_new.show())
    sock.sendto(bytes(pkt_new),SERVER_ADDRESS)
    image_bytes = io.BytesIO()
    expected_seq_num = 1
    while True:
        # Wait for packet from server
        # time.sleep(0.3)
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)

        # Check packet sequence number
        if pkt.seq_num == expected_seq_num:
            # Write payload to image buffer
            image_bytes.write(pkt.message)
            expected_seq_num += len(pkt.message)

            # Send ACK packet to server
            ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.ack_num, ack_num=expected_seq_num)
            sock.sendto(bytes(ack_packet), SERVER_ADDRESS)

            # Check for end of image
            # print(pkt.message)
            if len(pkt.message) < RUDP_MAX_SIZE - 4000:
                break
        else:
            # Send ACK packet to server for last correctly received packet
            ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.ack_num, ack_num=expected_seq_num)
            sock.sendto(bytes(ack_packet), SERVER_ADDRESS)
    # img_open = Image.open(image_bytes)
    # img_open.show()
    # time.sleep(0.3)
    ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.seq_num + len(pkt.message),ack_num=expected_seq_num)
    sock.sendto(bytes(ack_packet), SERVER_ADDRESS)

    fin_request_packet = RUDP(dst_port=pkt.src_port, flags="F", seq_num=pkt.seq_num + len(pkt.message),ack_num=expected_seq_num)
    sock.sendto(bytes(fin_request_packet), SERVER_ADDRESS)

    fin_received = False
    while not fin_received:
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == ['F','A']:
            fin_received = True

    # Send ACK packet to server
    ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.ack_num, ack_num=pkt.seq_num + 1)
    time.sleep(0.5)
    sock.sendto(bytes(ack_packet), SERVER_ADDRESS)

    # Return image data as bytes
    return image_bytes.getvalue()


def Save_or_Show(img):
    global IMG_COUNTER
    print(colored("Do you prefer to save the meme or to show it on the screen?:","red","on_black", attrs=["bold", "underline"]))
    rod = input(colored("<1>:Save.\n<2>:Show.\n", "blue","on_black", attrs=["bold", "underline"]))
    # _img_num =0
    if rod == '1' or rod.upper() == "SAVE":
        if isinstance(img,str):
            response = requests.get(img.encode('utf-8'))
            img1 = Image.open(BytesIO(response.content))
            img1.save(f'/home/meme_{IMG_COUNTER}.jpg')
        else:
            img.save(f'/home/meme_{IMG_COUNTER}.jpg')
        IMG_COUNTER +=1
    elif rod == '2' or rod.upper() == "SHOW":
        if isinstance(img, str):
            get_meme(img)
        elif isinstance(img,bytes):
            img = Image.open(io.BytesIO(img))
            img.show()
        else:
            print("Wrong format")


def get_meme(url):
    our_meme = requests.get(url)
    image_meme = our_meme.content
    image = Image.open(BytesIO(image_meme))
    image.show()


def connect_tcp(msg_num):
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.bind(CLIENT_ADDRESS)
    client_socket.connect(SERVER_ADDRESS)

    client_socket.sendall(msg_num.encode('utf-8'))
    # print("After sending the request url")
    url_data = b''

    url_data += client_socket.recv(1048)

    print(f"after the while\n{url_data.decode()}")
    client_socket.close()
    return url_data.decode()


if __name__ == '__main__':
    #

    print(colored("Welcome to the Meme Generator App","yellow","on_black",attrs=["bold","underline"]))
    while True:
        proto=input(colored("Choose the Protocol type you want to communicate with:\n<1>:TCP.\n<2>:RUDP.\n<9>:Quit App\n","red","on_black",attrs=["bold","underline"]))
        if proto == '1' or proto.upper() == "TCP":
            print(colored("Do you want to choose a meme by yourself or for we to generate a random meme for you?:","red","on_black",attrs=["bold","underline"]))
            opt=input(colored("<1>:Choose from library.\n<2>:Surprise me!.\n","blue","on_black",attrs=["bold","underline"]))
            if opt=='1':
                print(colored("Choose the number of your choice from the Meme-Library:","red","on_black",attrs=["bold","underline"]))
                meme_opt = input(colored("<1>:Frustrated Meme\n<2>:Surprised Meme\n<3>:Angry Meme\n<4>:'Stoned' "
                                         "Meme\n<5>:Happy Meme\n<6>:Bored Meme\n<7>:Nerd Meme\n","blue","on_black"))
                meme_opt=str((int(meme_opt)-1))
                url=connect_tcp(meme_opt)
                Save_or_Show(url)
            elif opt=='2':
                meme_opt = str(random.randint(0,6))
                url=connect_tcp(meme_opt)
                Save_or_Show(url)

        elif proto == '2' or proto.upper() == "RUDP":
            print(colored("Do you want to choose a meme by yourself or for we to generate a random meme for you?:","red","on_black",attrs=["bold","underline"]))
            opt=input(colored("<1>:Choose from library.\n<2>:Surprise me!.\n","blue","on_black",attrs=["bold","underline"]))
            if opt=='1':
                print(colored("Choose the number of your choice from the Meme-Library:","red","on_black",attrs=["bold","underline"]))
                meme_opt = input(colored("<1>:Frustrated Meme\n<2>:Surprised Meme\n<3>:Angry Meme\n<4>:'Stoned' "
                                         "Meme\n<5>:Happy Meme\n<6>:Bored Meme\n<7>:Nerd Meme\n","blue","on_black"))
                meme_opt = str(int(meme_opt) - 1)
                img_bytes=rudp_connecet(meme_opt)
                # img = Image.open(io.BytesIO(img_bytes))
                Save_or_Show(img_bytes)
            elif opt=='2':
                meme_opt = str(random.randint(0,6))
                img_bytes=rudp_connecet(meme_opt)
                # img = Image.open(io.BytesIO(img_bytes))
                Save_or_Show(img_bytes)

        elif proto == '9':
            print(colored("Hope you enjoyed! See you soon :)\n","yellow","on_black",attrs=["bold","underline"]))
            exit()
        else:
            print(colored("Input Error, restarting App!\n","black","on_yellow",attrs=["bold","underline"]))