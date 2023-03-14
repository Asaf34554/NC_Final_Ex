import time
from scapy.all import *
from scapy.layers.dns import *

dns_port = 53
dns_ip = "10.168.1.60"


def listen_dns():
    sniff(prn=handle_dns, filter='udp and (port 53) and dst host 10.168.1.60', iface="enp0s3")


def handle_dns(p):
    if DNS in p and p[DNS].qr == 0 or DNSQR in p:

        dnsq=IP(dst='8.8.8.8')/\
             UDP(sport=dns_port)/\
             DNS(rd=1,qd=p[DNS].qd)
        response=sr1(dnsq,verbose=0)
        if response:
            response[IP].src=dns_ip
            response[IP].dst = p[IP].src
            response[UDP].dport = p[UDP].sport
            response[UDP].src = 53
            send(response,verbose=0)
            print(f"Sent DNS response to client: {response[IP].dst}\nDomain:{response[DNSRR].rrname}\nAddress:{response[DNSRR].rdata}\n")
        else:
            print("Error occurred in getting resolver response, closing the dns.")
            exit()


if __name__ == '__main__':
    listen_dns()