import time

from scapy.all import *
from scapy.layers.dns import *

dns_port = 53
conf.ip= "192.168.1.60"

def listen_dns():
    # Make sure it is DHCP with the filter options
    sniff(prn=handle_dns, filter='udp and (port 53)', iface="enp0s3")


def handle_dns(p):
    if DNS in p and p[DNS].qr == 0 or p.haslayer(DNSQR):
        print("entered handledns")
        qry_name = p[DNSQR].qname
        qry_type = p[DNSQR].qtype
        print(f"Received DNS Query:{qry_name} ({qry_type})")
        dns_q = IP(src= "192.168.1.60",dst="8.8.8.8")/\
            UDP(sport = dns_port)/\
            DNS(rd=1,qd=DNSQR(qname=qry_name,qtype=qry_type),opcode=p[DNS].opcode)
        response = sr1(dns_q,verbose=False)
        print("after response from DNS google")
        # print(f"ans is:{response[DNS].an}")
        if response is None:
            print("error couldn't find desired Adrress")
        else:
            print("after the else")
            dns_r = response
            dns_r[IP].dst=p[IP].src
            dns_r[UDP].dport = p[UDP].sport
            sendp(dns_r, iface="enp0s3")
            # dns_r = IP(dst=p[IP].src)/\
            # UDP(sport = dns_port,dport = p[UDP].sport)/\
            # DNS(qd=response[UDP].qd,qr=1,an=response[DNS].an)
            # sendp(dns_r,iface="enp0s3")
            # print(f"The response sent successfully\nThe adress is: {response[DNS].an}")
    print("going out")

if __name__ == '__main__':
    listen_dns()