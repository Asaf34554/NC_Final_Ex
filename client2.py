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
    pkt = RUDP(src_port = CLIENT_ADDRESS[1],flags = "S",seq_num = 0)
    sock.sendto(bytes(pkt),SERVER_ADDRESS)
    ack_syn_received = False
    ack_num=0
    while not ack_syn_received:
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.flags == ['S','A'] and pkt.seq_num == 0:
            ack_num += 1
            ack_syn_received = True

    pkt_new = RUDP(message=msg_num,seq_num=pkt.seq_num + 1, ack_num=ack_num, dst_port=pkt.src_port, flags='A')
    sock.sendto(bytes(pkt_new),SERVER_ADDRESS)
    image_bytes = io.BytesIO()
    expected_seq_num = 1
    while True:
        data, addr = sock.recvfrom(RUDP_MAX_SIZE)
        pkt = RUDP(data)
        if pkt.seq_num == expected_seq_num:
            image_bytes.write(pkt.message)
            expected_seq_num += len(pkt.message)
            ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.ack_num, ack_num=expected_seq_num)
            sock.sendto(bytes(ack_packet), SERVER_ADDRESS)
            if len(pkt.message) < RUDP_MAX_SIZE - 4000:
                break
        else:
            ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.ack_num, ack_num=expected_seq_num)
            sock.sendto(bytes(ack_packet), SERVER_ADDRESS)

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

    ack_packet = RUDP(dst_port=pkt.src_port, flags="A", seq_num=pkt.ack_num, ack_num=pkt.seq_num + 1)
    time.sleep(0.5)
    sock.sendto(bytes(ack_packet), SERVER_ADDRESS)
    return image_bytes.getvalue()


def save_or_show(img):
    global IMG_COUNTER
    print(colored("Do you prefer to save the meme or to show it on the screen?:","red","on_black",
                  attrs=["bold", "underline"]))
    holder = True
    while holder is True:
        rod = input(colored("<1>:Save.\n<2>:Show.\n", "blue","on_black", attrs=["bold", "underline"]))
        # _img_num =0
        if rod == '1' or rod.upper() == "SAVE":
            file_name = input("Enter file name (without extension!): ")
            if isinstance(img,str):
                response = requests.get(img.encode('utf-8'))
                img1 = Image.open(BytesIO(response.content))
                if file_name is None:
                    img1.save(os.path.join(os.path.expanduser("~"), "Desktop", f'meme_{IMG_COUNTER}.jpg'))
                    IMG_COUNTER += 1
                else:
                    img1.save(os.path.join(os.path.expanduser("~"), "Desktop", f'{file_name}.jpg'))
                print(colored("It has been save in the Desktop", "green", "on_white",
                              attrs=["bold", "underline"]))
            else:
                img = Image.open(BytesIO(img))
                if file_name is None:
                    img.save(os.path.join(os.path.expanduser("~"), "Desktop", f'meme_{IMG_COUNTER}.jpg'))
                    IMG_COUNTER += 1
                else:
                    img.save(os.path.join(os.path.expanduser("~"), "Desktop", f'{file_name}.jpg'))
                print(colored("It has been save in the Desktop", "green", "on_white",
                              attrs=["bold", "underline"]))
            holder = False
        elif rod == '2' or rod.upper() == "SHOW":
            if isinstance(img, str):
                get_meme(img)
            elif isinstance(img,bytes):
                img = Image.open(io.BytesIO(img))
                img.show()
            holder = False
        else:
            print(colored("Worng number, please choose again:", "red", "on_white",
                          attrs=["bold", "underline"]))


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
    url_data = b''

    url_data += client_socket.recv(1048)

    client_socket.close()
    return url_data.decode()


if __name__ == '__main__':
    print(colored("Welcome to the Meme Generator App","yellow","on_black",
                  attrs=["bold","underline"]))
    while True:
        proto=input(colored("Choose the Protocol type you want to communicate with:\n<1>:TCP.\n"
                            "<2>:RUDP.\n<9>:Quit App\n","red","on_black",
                            attrs=["bold","underline"]))
        if proto == '1' or proto.upper() == "TCP":
            print(colored("Do you want to choose a meme by yourself or for we to generate a random meme for you?:","red","on_black",attrs=["bold","underline"]))
            opt=input(colored("<1>:Choose from library.\n<2>:Surprise me!.\n","blue","on_black",
                              attrs=["bold","underline"]))
            if opt=='1':
                print(colored("Choose the number of your choice from the Meme-Library:","red","on_black",
                              attrs=["bold","underline"]))
                meme_opt = input(colored("<1>:Frustrated Meme\n<2>:Surprised Meme\n<3>:Angry Meme\n<4>:'Stoned' "
                                         "Meme\n<5>:Happy Meme\n<6>:Bored Meme\n<7>:Nerd Meme\n<8>:Student "
                                         "Meme\n<9>:Student 2 Meme\n<10>:Computer Science Meme\n<11>:Parliament "
                                         "Meme\n<12>:Student 3 Meme\n<13>:Parliament 2 Meme\n<14>:Student 4 Meme\n",
                                         "blue", "on_black"))
                meme_opt=str((int(meme_opt)-1))
                url=connect_tcp(meme_opt)
                save_or_show(url)
            elif opt=='2':
                meme_opt = str(random.randint(0,6))
                url=connect_tcp(meme_opt)
                save_or_show(url)

        elif proto == '2' or proto.upper() == "RUDP":
            print(colored("Do you want to choose a meme by yourself or for we to generate a random meme for you?:","red","on_black",attrs=["bold","underline"]))
            opt=input(colored("<1>:Choose from library.\n<2>:Surprise me!.\n","blue","on_black",
                              attrs=["bold","underline"]))
            if opt=='1':
                print(colored("Choose the number of your choice from the Meme-Library:","red","on_black",
                              attrs=["bold","underline"]))
                meme_opt = input(colored("<1>:Frustrated Meme\n<2>:Surprised Meme\n<3>:Angry Meme\n<4>:'Stoned' "
                                         "Meme\n<5>:Happy Meme\n<6>:Bored Meme\n<7>:Nerd Meme\n<8>:Student "
                                         "Meme\n<9>:Student 2 Meme\n<10>:Computer Science Meme\n<11>:Parliament "
                                         "Meme\n<12>:Student 3 Meme\n<13>:Parliament 2 Meme\n<14>:Student 4 Meme\n",
                                         "blue","on_black"))
                meme_opt = str(int(meme_opt) - 1)
                img_bytes=rudp_connecet(meme_opt)
                save_or_show(img_bytes)
            elif opt=='2':
                meme_opt = str(random.randint(0,6))
                img_bytes=rudp_connecet(meme_opt)
                save_or_show(img_bytes)

        elif proto == '9':
            print(colored("Hope you enjoyed! See you soon :)\n","yellow","on_black",
                          attrs=["bold","underline"]))
            exit()
        else:
            print(colored("Input Error, restarting App!\n","black","on_yellow",
                          attrs=["bold","underline"]))