import random
import time

from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.dns import *

ethernet_src = get_if_hwaddr("enp0s3")
my_new_ip = None

def dhcp_connect():

    discover = Ether(dst='ff:ff:ff:ff:ff:ff') /\
            IP(dst='255.255.255.255') /\
            UDP(sport=68, dport=67) /\
            BOOTP(chaddr=ethernet_src) /\
            DHCP(options=[('message-type', 'discover'), 'end'])
    sendp(discover, iface="enp0s3")
    offer = sniff(filter="udp and (port 67)", count=1)[0]
    if offer is None:
        print("Error no dhcp offer receive")
        exit()
    else:
        print("GOT The Offer")
        yiaddr = offer[BOOTP].yiaddr
        siaddr = offer[IP].src

    req = Ether(src=ethernet_src, dst='ff:ff:ff:ff:ff:ff') /\
            IP(src=yiaddr, dst='255.255.255.255') /\
            UDP(sport=68, dport=67) /\
            BOOTP(chaddr=ethernet_src) /\
            DHCP(options=[("message-type", "request"),
                          ("requested_addr",yiaddr),
                          ("server_id",siaddr),
                          "end"])
    sendp(req, iface="enp0s3")
    print("AFTER SENDING THE REQUEST")
    ack = sniff(filter="udp and (port 67)", count=1)[0]
    print("AFTER GETING THE ACK")
    if ack:
        assigned_ip = ack[BOOTP].yiaddr
        print(f"Got the ack\nthe new ip is:{assigned_ip} ")
        lease_time = ack[DHCP].options[0][1]
        time.sleep(2)
        return assigned_ip
    else:
        print("Error no dhcp ack receive")
        exit()


def dhcp_release():
    rel = Ether(src=ethernet_src, dst='ff:ff:ff:ff:ff:ff') / \
          IP(src=my_new_ip, dst='255.255.255.255') / \
          UDP(sport=68, dport=67) / \
          BOOTP(chaddr=ethernet_src) / \
          DHCP(options=[("message-type", "release"),
                        ("requested_addr", my_new_ip),
                        "end"])
    sendp(rel, iface="enp0s3")
    print("AFTER SENDING THE RELEASE")


def get_req():
    ans=input("Enter the required domain/ip:")
    return ans


def dns_query():
    op=0
    addorip = get_req()
    if(addorip[0]).isdigit():
        op=1
    print(f"{addorip}  ,{op}")
    client_q = IP(src=my_new_ip,dst="192.168.1.60")/\
        UDP(dport=53)/\
        DNS(qr=0,rd=1,qd=DNSQR(qname=addorip,qtype='A'), opcode=op)
    ans = sr1(client_q,iface="enp0s3")
    print(ans.show())


if __name__ == '__main__':
    my_new_ip = dhcp_connect()
    dns_query()

    dhcp_release()
