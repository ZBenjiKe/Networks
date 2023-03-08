from socket import *
from scapy.all import*
import time
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

'''''''''''''''''''''''''''''''''
         DHCP - Functions
'''''''''''''''''''''''''''''''''
def discover():
    first = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    IP(src='0.0.0.0', dst='255.255.255.255') / \
                    UDP(sport=68, dport=67) / \
                    BOOTP(chaddr="74:e5:f9:0c:ea:ef", xid=0x12345678) / \
                    DHCP(options=[("message-type", "discover"), "end"]) #Had a problem with xid generate i left it that way
    sendp(first)
    print("Discover sent!")
    sniff(filter="udp and port 67", prn=request, count=1, iface="wlp3s0")


def request(packet):
    global client_ip
    client_ip = packet[BOOTP].yiaddr
    if client_ip == "0.0.0.0":
        print("IP address didn't assigned")
        return
    print ("Client IP:", client_ip)

    request = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    IP(src="0.0.0.0", dst="255.255.255.255") / \
                    UDP(sport=68, dport=67) / \
                    BOOTP(chaddr="74:e5:f9:0c:ea:ef", yiaddr=client_ip, xid=packet[BOOTP].xid) / \
                    DHCP(options=[("message-type", "request"), "end"])
    time.sleep(1)
    sendp(request)
    print("Request sent!")
    sniff(filter="udp and port 67", count=1, iface="wlp3s0")

#IP gain as ^client_ip^
discover()
'''''''''''''''''''''''''''''''''
        UDP - DHCP, DNS
'''''''''''''''''''''''''''''''''

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

'''
DHCP config
Make sure dns resolver is dns server from project
Make sure process port is 20908
'''

'''
# DNS query to find IP for DASH server
ans = sr1(IP(dst="8.8.8.8")/UDP(sport=RandShort(), dport=53)/DNS(rd=1,qd=DNSQR(qname="dashserver.com",qtype="A")))
ans.an.rdata
'''

clientSocket.close()


'''''''''''''''''''''''''''''''''
          TCP - DASH
'''''''''''''''''''''''''''''''''

#SERVER_ADDRESS = ('localhost', 13000)
clientSocket = socket(AF_INET, SOCK_STREAM)

serverName = 'localhost'
serverPort = 30577
SERVER_ADDRESS = (serverName, serverPort)
clientSocket.connect(SERVER_ADDRESS)

options = clientSocket.recv(4096).decode()
chosenQuality = input(options)
while chosenQuality < 1 or chosenQuality > 5:
    chosenQuality = input('Please enter a valid choice')
clientSocket.send(chosenQuality.encode())

# Receive video files
while():
    frame = clientSocket.recv(4096).decode()
clientSocket.close()
