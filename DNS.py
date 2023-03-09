import time

from scapy.all import *
from scapy.layers.dns import *

dns_port = 53
dns_ip = "10.168.1.60"


def listen_dns():
    # Make sure it is DHCP with the filter options
    sniff(prn=handle_dns, filter='udp and (port 53)', iface="enp0s3")


def handle_dns(p):
    if DNS in p and p[DNS].qr == 0 or DNSQR in p:

        dnsq=IP(dst='8.8.8.8')/\
             UDP(sport=dns_port)/\
             DNS(rd=1,qd=p[DNS].qd)
        response=sr1(dnsq,verbose=0)
        print(response[DNSRR].rdata)
        if response:
            response[IP].src=dns_ip
            response[IP].dst = p[IP].src
            response[UDP].dport = p[UDP].sport

            # response_to_client = IP(src=dns_ip,dst=p[IP].src)/\
            #                      UDP(dport=p[UDP].sport)/\
            #                      DNS()
            #
            # response_to_client[DNS]= response[DNS].copy()
            print(response.show())
            # response_to_client[DNS].an = response[DNS].an.copy()
            send(response,verbose=0)
            print("closing the dns")
            exit()


if __name__ == '__main__':
    listen_dns()