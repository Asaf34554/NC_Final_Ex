
from scapy.all import *
import time

ethernet_src = get_if_hwaddr("enp0s3")


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
        time.sleep(10)
        return assigned_ip
    else:
        print("Error no dhcp ack receive")
        exit()


def dhcp_release(ip):
    rel = Ether(src=ethernet_src, dst='ff:ff:ff:ff:ff:ff') / \
          IP(src=ip, dst='255.255.255.255') / \
          UDP(sport=68, dport=67) / \
          BOOTP(chaddr=ethernet_src) / \
          DHCP(options=[("message-type", "release"),
                        ("requested_addr", ip),
                        "end"])
    sendp(rel, iface="enp0s3")
    print("AFTER SENDING THE RELEASE")


if __name__ == '__main__':
    client_ip = dhcp_connect()
    dhcp_release(client_ip)
