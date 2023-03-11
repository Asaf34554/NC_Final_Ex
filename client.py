import random
import time

from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.dns import *

ethernet_src = get_if_hwaddr("enp0s3")
my_new_ip = None


def dhcp_connect():

    discover = Ether(dst='ff:ff:ff:ff:ff:ff') /\
            IP(src="0.0.0.0",dst='255.255.255.255') /\
            UDP(sport=68, dport=67) /\
            BOOTP(chaddr=ethernet_src) /\
            DHCP(options=[('message-type', 'discover'), 'end'])
    sendp(discover, iface="enp0s3")
    offer = sniff(filter="udp and (port 68 and port 67)", count=1)[0]
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
    ack = sniff(filter="udp and (port 68 and port 67)", count=1)[0]
    print("AFTER GETING THE ACK")
    if ack:
        assigned_ip = ack[BOOTP].yiaddr
        print(f"Got the ack\nthe new ip is:{assigned_ip} ")
        lease_time = ack[DHCP].options[0][1]
        # time.sleep(2)
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


def dns_query(my_ip):
    addorip = get_req()
    client_q = IP(src=my_ip,dst="10.168.1.60")/\
               UDP(sport=random.randint(111,999),dport=53)/\
               DNS(rd=1,qd=DNSQR(qname=addorip))
    cli_port=client_q[UDP].sport
    send(client_q)
    # time.sleep(0.5)
    ans = sniff(filter=f"udp and port {cli_port}", count=1)[0]
    if ans:
        # print(ans.show())
        # print("SHEAF BEN ZONA LO YAGID SHTA LO YODEA")
        print(f"Received response from DNS server:-->{ans[DNSRR].rdata}----Domain:-->{ans[DNSRR].rrname}")
        return ans[DNSRR].rdata
    else:
        print("Couldn't get response from DNS server")


if __name__ == '__main__':
    my_new_ip = dhcp_connect()
    dns_resp = dns_query(my_new_ip)
    dhcp_release()
