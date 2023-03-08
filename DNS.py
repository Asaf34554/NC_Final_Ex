from scapy.all import *
import time
import dns.resolver
dns_port = 53


def listen_dns():
    # Make sure it is DHCP with the filter options
    sniff(prn=handle_dns, filter='port 53', iface="enp0s3")


def handle_dns(p):
    if DNS in p and p[DNS].rd == 1 or p.haslayer(DNSQR):

        qry_name = p[DNSQR].qname.decode()
        qry_type = p[DNSQR].qtype
        print(f"Received DNS Query:{qry_name} ({qry_type})")



