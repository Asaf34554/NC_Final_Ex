from scapy.all import *
import time

mac = get_if_hwaddr("enp0s3")
conf.iface = 'enp0s3'
# SERVER_IP = "10.0.2.15"
_ip_list = {
    "192.168.1.2": False,
    "192.168.1.3": False,
    "192.168.1.4": False,
    "192.168.1.5": False,
    "192.168.1.6": False
}


def listen_dhcp():
    # Make sure it is DHCP with the filter options
    sniff(prn=handle_dhcp, filter='udp and (port 68)', iface="enp0s3")


def handle_dhcp(p):

    if DHCP in p and p[DHCP].options[0][1] == 1:
        print("DHCP Discover")
        ip = ""
        for i, used in _ip_list.items():
            if not used:
                ip = i
                _ip_list[i] = True
                print(f"ip is:{ip}")
                break
            else:
                print(f"ip :{ip} is used")
        if ip is not None:
            # Build the DHCP offer packet with the IP address
            client_mac = p[Ether].src
            client_ip = p[IP].src
            offer = Ether( dst="ff:ff:ff:ff:ff:ff") / \
                    IP() / \
                    UDP(sport=67, dport=68) / \
                    BOOTP(op=2, yiaddr=ip, chaddr=client_mac) / \
                    DHCP(options=[("message-type", "offer"),
                                  ("lease_time", 43200),
                                  ("subnet_mask", "255.255.255.0"),
                                  "end"])
            time.sleep(0.2)
            sendp(offer, iface="enp0s3")

    if DHCP in p and p[DHCP].options[0][1] == 3:
        print("DHCP Request")
        ack = Ether(src=mac, dst=p[Ether].src) / \
                IP(dst=p[IP].src) / \
                UDP(sport=67, dport=68) / \
                BOOTP(op=2, yiaddr=p[IP].src, chaddr=p[Ether].src) / \
                DHCP(options=[("message-type", "ack"),
                              ("lease_time", 43200),
                              ("subnet_mask", "255.255.255.0"),
                              "end"])
        time.sleep(0.2)
        sendp(ack, iface="enp0s3")
        print("after sending the ack")

    if DHCP in p and p[DHCP].options[0][1] == 7:
        print("DHCP Release")
        rel_ip = p[IP].src

        for i, used in _ip_list.items():
            if i == rel_ip:
                _ip_list[i] = False
                print(f"Released ip:{i}")
                break
            else:
                print(f"the ip we dont dell is {i}")


if __name__ == '__main__':
    listen_dhcp()
