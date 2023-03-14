
import requests
from scapy.all import *


RUDP_MAX_SIZE = 62000
SERVER_ADDRESS = ("127.0.0.10", 30493)


class RUDP(Packet):
    name = "RUDP"
    fields_desc = [
        ShortField("src_port", 30495),
        ShortField("dst_port", 80),
        IntField("seq_num", 0),
        IntField("ack_num", 0),
        FlagsField("flags", 0, 8, ['S', 'A', 'F']),
        ShortField("window", 8192),
        ShortField("checksum", None),
        ShortField("urgent_ptr", 0),
        StrField("message", "")
    ]


memes = [
    ('https://speech.protocommunications.com/wp-content/uploads/2018/03/frustrated-meme.png', 'frustrated_meme'),
    ('https://media.wired.com/photos/5f87340d114b38fa1f8339f9/master/w_1600,c_limit/Ideas_'
     'Surprised_Pikachu_HD.jpg', 'surprised_meme'),
    ('https://m.media-amazon.com/images/I/61k7AtBBAVS._AC_SL1327_.jpg', 'angry_meme'),
    ('https://i.imgflip.com/639z7.jpg', 'stoned_meme'),
    ('https://cache.lovethispic.com/uploaded_images/blogs/10-Happy-Memes-To-Help-Your-Day-Feel-A-Whole-Lot-Better'
     '-50193-3.jpg', 'happy_meme'),
    ('https://scontent.ftlv19-1.fna.fbcdn.net/v/t1.6435-9/46310761_1843365659095168_484399811940843520_n.jpg?_nc_cat'
     '=108&ccb=1-7&_nc_sid=8bfeb9&_nc_ohc=MPsSPM_c_g0AX8dRueG&_nc_ht=scontent.ftlv19-1.fna&oh'
     '=00_AfB0gYkK9MEn3wqhISclfum7Kk-LZrhA-X9QhUnTW8ibng&oe=64340756', 'bored_meme'),
    ('https://pbs.twimg.com/media/DXJnAlSU8AAzPl-?format=jpg&name=900x900', 'nerd_meme'),
    ('https://pbs.twimg.com/media/FW02oQlXwAA64DV?format=jpg&name=900x900', 'student_funny_meme'),
    ('https://images2.study.co.il/upload/%D7%9E%D7%A1%D7%AA%D7%9B%D7%9C%20%D7%A2%D7%9C%20%D7%9E%D7%9E%D7%99%D7%9D%20('
     '2)(1).jpg', 'The_Biggest_Student_lie'),
    ('https://i.redd.it/jrbdgx5j7md51.jpg', 'Student_1'),
    ('https://storage.googleapis.com/meme-king-storage/meme-thumbs/parlament/T2Ep3sGUQTJh6E7P.jpg', 'parliement_1'),
    ('https://i0.wp.com/higa.co.il/wp-content/uploads/2020/10/84334527_1140287689637358_545336876655968256_n-1.jpg'
     '?fit=750%2C908&ssl=1', 'when_the_grade_is_comming'),
    ('https://i.pinimg.com/564x/af/0c/b0/af0cb0442eff94833e9c533c2c3adcb8.jpg', 'parliament_2'),
    ('https://i0.wp.com/higa.co.il/wp-content/uploads/2020/10/116153597_1281131148886344_4075102749694828796_o.jpg'
     '?fit=1030%2C565&ssl=1', 'student_2')
]


def tcp_listen():
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(SERVER_ADDRESS)
    while True:
        tcp_server_socket.listen()
        client_socket, client_address = tcp_server_socket.accept()
        tcp_connection(client_socket)


def tcp_connection(client_socket):
    data = b''
    data += client_socket.recv(1024)
    index = data.decode('utf-8')
    message = memes[int(index)][0]

    client_socket.sendall(message.encode('utf-8'))


def get_image(meme_num):
    return requests.get(memes[int(meme_num)][0]).content


def rudp_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDRESS)
    while True:
        syn_received = False
        pkt = RUDP()
        client_address = None
        while not syn_received:
            data, addr = sock.recvfrom(RUDP_MAX_SIZE)
            pkt = RUDP(data)
            if pkt.flags == 'S':
                syn_received = True
                client_address = addr
        seq_num = 0
        ack_num = pkt.seq_num + 1
        syn_ack_packet = RUDP(dst_port=pkt.src_port, src_port=SERVER_ADDRESS[1], flags=['S', 'A'], seq_num=seq_num,
                              ack_num=ack_num)
        sock.sendto(bytes(syn_ack_packet), client_address)
        ack_image_received = False
        while not ack_image_received:
            data, addr = sock.recvfrom(RUDP_MAX_SIZE)
            pkt = RUDP(data)
            if pkt.flags == 'A' and pkt.message is not None:
                ack_num += len(data)
                ack_image_received = True
        image_to_send = get_image(pkt.message)
        chunks = [image_to_send[i:i + RUDP_MAX_SIZE - 4000] for i in range(0, len(image_to_send), RUDP_MAX_SIZE - 4000)]

        seq_num = pkt.ack_num
        for i, chunk in enumerate(chunks):
            pkt = RUDP(dst_port=pkt.dst_port, seq_num=seq_num, ack_num=ack_num, message=chunk)
            sock.sendto(bytes(pkt), client_address)
            ack_received = False
            while not ack_received:
                data, addr = sock.recvfrom(RUDP_MAX_SIZE - 4000)
                pkt = RUDP(data)
                if pkt.flags == 'A' and pkt.ack_num == seq_num + len(chunk):
                    ack_received = True
            seq_num += len(chunk)

        fin_requested = False
        while not fin_requested:
            data, addr = sock.recvfrom(RUDP_MAX_SIZE)
            pkt = RUDP(data)
            if pkt.flags == "F":
                fin_requested = True
        fin_packet = RUDP(dst_port=client_address[1], flags=['F', 'A'], seq_num=seq_num, ack_num=ack_num)
        sock.sendto(bytes(fin_packet), client_address)
        fin_ack = False
        while not fin_ack:
            data, addr = sock.recvfrom(RUDP_MAX_SIZE)
            pkt = RUDP(data)
            if pkt.flags == 'A':
                fin_ack = True


if __name__ == "__main__":
    rudp_thread = threading.Thread(target=rudp_connection)
    rudp_thread.start()

    tcp_thread = threading.Thread(target=tcp_listen)
    tcp_thread.start()

    rudp_thread.join()
    tcp_thread.join()
