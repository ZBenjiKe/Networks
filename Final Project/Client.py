from socket import *
from scapy.all import*
import time
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.dns import DNSQR, DNS
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether


'''''''''''''''''''''''''''''''''
    Connect with UDP to DHCP
'''''''''''''''''''''''''''''''''

def discover():
    first = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                    IP(src='0.0.0.0', dst='255.255.255.255') / \
                    UDP(sport=68, dport=67) / \
                    BOOTP(chaddr="74:e5:f9:0c:ea:ef", xid=0x12345678) / \
                    DHCP(options=[("message-type", "discover"), "end"]) #Had a problem with xid generate i left it that way
    sendp(first)
    print("Discover sent!")
    sniff(filter="udp and port 67", prn=request, count=1)

def request(packet):
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
 #   sniff(filter="udp and port 67", count=1)


'''''''''''''''''''''''''''''''''
    Connect with UDP to DNS
'''''''''''''''''''''''''''''''''

def getDashIP(dns_ip, dns_port, app_domain):

    clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
    serverName = 'localhost'
    serverPort = 14000
    DNS_ADDRESS = (dns_ip, dns_port)

    request = DNS(rd=1, qd=DNSQR(qname=app_domain))
    clientSocket.sendto(bytes(request), DNS_ADDRESS)
    print("DNS request sent.")
    time.sleep(2)

    data, address = clientSocket.recvfrom(2048)
    print("DNS response received.")

    response = DNS(data)
    app_ip = str(response.an.rdata)
    print("DASH server IP is:", app_ip)

    clientSocket.close()

    return app_ip

'''''''''''''''''''''''''''''''''
          TCP - DASH
'''''''''''''''''''''''''''''''''

def streamFromDashTCP(app_ip, app_port):

    DASH_ADDRESS = (app_ip, app_port)
    clientSocket = socket.socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(DASH_ADDRESS)

    '''
    Make sure process port is 20908
    '''

    # Choose picture quality to receive
    options = clientSocket.recv(4096).decode()
    chosenQuality = input(options)
    while chosenQuality != "720" and chosenQuality != "480" and chosenQuality != "360":
        chosenQuality = input('Please enter a valid choice')
    clientSocket.send(chosenQuality.encode())
    
    # Receive video files
    time.sleep(1)

    frameCount = 1

    while(frameCount <= 25):
        data = b''
        while b"Finished" not in data:
            data += clientSocket.recv(1024)
        data = data[:-8]

        image_copy = open(f'Copies/{frameCount}.png', "wb")
        image_copy.write(data)
        image_copy.close()
        frameCount += 1
        clientSocket.send("ACK".encode())

    print("Finished receiving video frames.")

    clientSocket.close()


def main():
    dhcp_ip = '127.0.0.1'
    dhcp_port = 67
    dns_ip = '127.0.0.1'
    dns_port = 53
    app_ip = '0.0.0.0'
    app_port = 30577
    app_domain = "www.dashserver.com"

    discover()
    if dns_ip != "0.0.0.0":
        app_ip = getDashIP(dns_ip, dns_port, app_domain)
    if app_ip != "0.0.0.0":
        streamFromDashTCP(app_ip, app_port)
    


if __name__ == '__main__':
    main()