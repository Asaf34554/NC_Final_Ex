import time

from scapy.all import *
from scapy.layers.dns import *

dns_port = 53
dns_ip = "127.0.0.1"


def listen_dns():
    # Make sure it is DHCP with the filter options
    sniff(prn=handle_dns, filter='udp and (port 53)')


def handle_dns(p):
    if DNS in p and p[DNS].qr == 0 or DNSQR in p:
        dnsq=IP(dst='8.8.8.8')/\
             UDP(sport=53)/\
             DNS(rd=1,qd=p[DNS].qd)
        response=sr1(dnsq,verbose=0)
        print(response.show())
        print('*************************\n\n')

        response_to_client = IP(src=dns_ip,dst=p[IP].src)/\
                             UDP(dport=p[UDP].sport)/\
                             DNS()
                             # DNS(id=p[DNS].id,qr=1,rd=1,an=DNSRR(rrname=p[DNS].qd.qname.decode('utf-8'),rdata=response[DNS].an.rdata))
        response_to_client[DNS] = response[DNS]
        print(response_to_client.show())
        # response_to_client[DNS].an = response[DNS].an.copy()
        # time.sleep(0.2)
        send(response_to_client , verbose=0)
        # stam = sr1(response_to_client,verbose =0)
        print("closing the dns")
        exit()


if __name__ == '__main__':
    listen_dns()