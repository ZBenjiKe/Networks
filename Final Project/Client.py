from socket import *
from scapy.all import*
import time
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.dns import DNSQR, DNS
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
    global client_ip, dns_ip
    client_ip = packet[BOOTP].yiaddr
    dns_ip = packet[DHCP].options[3][1]
    if client_ip == "0.0.0.0":
        print("IP address didn't assigned")
        return
    print ("Client IP:", client_ip)
    print("DNS:", dns_ip)
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    IP(src="0.0.0.0", dst="255.255.255.255") / \
                    UDP(sport=68, dport=67) / \
                    BOOTP(chaddr="74:e5:f9:0c:ea:ef", yiaddr=client_ip, xid=packet[BOOTP].xid) / \
                    DHCP(options=[("message-type", "request"), "end"])
    time.sleep(1)
    sendp(request)
    print("Request sent!")
    sniff(filter="udp and port 67", count=1, iface="wlp3s0")


'''''''''''''''''''''''''''''''''
    Connect with UDP to DHCP
'''''''''''''''''''''''''''''''''
'''
Tuvia
clientSocket = socket(AF_INET, SOCK_DGRAM)
#IP gain as ^client_ip^
discover()
if client_ip != "0.0.0.0":
    dns()
'''

'''''''''''''''''''''''''''''''''
         DNS - Functions
'''''''''''''''''''''''''''''''''


'''''''''''''''''''''''''''''''''
    Connect with UDP to DNS
'''''''''''''''''''''''''''''''''

# DNS query to find IP for DASH server
clientSocket = socket(AF_INET, SOCK_DGRAM)

serverName = 'localhost'
serverPort = 14000

dns_address = ('localhost', 53)

request = DNS(rd=1, qd=DNSQR(qname='www.dashserver.com'))
clientSocket.sendto(request.encode(), dns_address)
data, address = clientSocket.recvfrom(2048)
response = DNS(data)

print(response.summary()) #Remove for handing in

dash_address = None

for answer in response[DNS].an:
    if answer.type == 1: # Type "A"
        dash_address = answer.rdata
        break

clientSocket.close()

'''''''''''''''''''''''''''''''''
          TCP - DASH
'''''''''''''''''''''''''''''''''

'''
Make sure process port is 20908
'''

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
