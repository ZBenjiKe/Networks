from socket import *
from scapy.all import *
import time
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.dns import DNSQR, DNS
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

sequence_list = []
'''''''''''''''''''''''''''''''''
    Connect with UDP to DHCP
'''''''''''''''''''''''''''''''''


def discover():
    first = Ether(dst="ff:ff:ff:ff:ff:ff") / \
            IP(src='0.0.0.0', dst='255.255.255.255') / \
            UDP(sport=68, dport=67) / \
            BOOTP(chaddr="74:e5:f9:0c:ea:ef", xid=0x12345678) / \
            DHCP(options=[("message-type", "discover"), "end"])  # Had a problem with xid generate i left it that way
    sendp(first)
    print("Discover sent!")
    sniff(filter="udp and port 67", prn=request, count=1)
    return dns_ip


def request(packet):
    global dns_ip
    client_ip = packet[BOOTP].yiaddr
    dns_ip = packet[DHCP].options[3][1]
    if client_ip == "0.0.0.0":
        print("IP address didn't assigned")
        return
    print("Client IP:", client_ip)
    print("DNS:", dns_ip)
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / \
              IP(src="0.0.0.0", dst="255.255.255.255") / \
              UDP(sport=68, dport=67) / \
              BOOTP(chaddr="74:e5:f9:0c:ea:ef", yiaddr=client_ip, xid=packet[BOOTP].xid) / \
              DHCP(options=[("message-type", "request"), "end"])
    time.sleep(1)
    sendp(request)
    print("Request sent!")
    # sniff(filter="udp and port 67", count=1)


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

    while (frameCount <= 25):
        data = b''
        while b"Finished" not in data:
            data += clientSocket.recv(1024)
            packet_str = data.decode("utf-8")  # Convert bytes to string
            sequence_number = int(packet_str.split(",")[1].split(" ")[-1])
            sequence_list.append(sequence_number)
            if (len(sequence_list)<sequence_number):
                resend = extractUndelivered(sequence_list)
                # Construct the request message
                request = f"Send:{resend}:please".encode()
                # Send the data message
                clientSocket.sendto(request, DASH_ADDRESS)
                data += clientSocket.recv(1024)
        data = data[:-8]

        image_copy = open(f'Copies/{frameCount}.png', "wb")
        image_copy.write(data)
        image_copy.close()
        frameCount += 1
        clientSocket.send("ACK".encode())

    print("Finished receiving video frames.")

    clientSocket.close()

def extractUndelivered(sequence_list):
    for i, num in enumerate(sequence_list):
        if i == 0:
            continue
        if num != sequence_list[i-1]+1:
            return num-1
    return None  # If no number is missing, return None

def streamFromDashRUDP(app_ip, app_port):
    DASH_ADDRESS = (app_ip, app_port)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    clientSocket.sendto("Please stream frames over UDP".encode(), DASH_ADDRESS)

    # Choose picture quality to receive
    options, DASH_ADDRESS = clientSocket.recvfrom(4096)
    chosenQuality = input(options.decode())
    while chosenQuality != "720" and chosenQuality != "480" and chosenQuality != "360":
        chosenQuality = input('Please enter a valid choice')
    clientSocket.sendto(chosenQuality.encode(), DASH_ADDRESS)

    # Receive video files
    time.sleep(1)

    frameCount = 1

    while (frameCount <= 25):
        data = b''
        while b"Finished" not in data:
            data, DASH_ADDRESS = clientSocket.recvfrom(1024)
            clientSocket.sendto("ACK".encode(), DASH_ADDRESS)
        data = data[:-8]

        image_copy = open(f'Copies/{frameCount}.png', "wb")
        image_copy.write(data)
        image_copy.close()
        frameCount += 1

    print("Finished receiving video frames.")

    clientSocket.close()


def main():
    dhcp_ip = '127.0.0.1'
    dhcp_port = 67
    # dns_ip = '0.0.0.0'
    dns_port = 53
    app_ip = '0.0.0.0'
    app_port = 30577
    app_domain = "www.dashserver.com"

    # dns_ip = discover()
    # if dns_ip != "0.0.0.0":
    #    app_ip = getDashIP(dns_ip, dns_port, app_domain)
    # if app_ip != "0.0.0.0":
    # streamFromDashTCP(app_ip, app_port)
    # streamFromDashRUDP(app_ip, app_port)
    streamFromDashRUDP('127.0.0.1', app_port)


if __name__ == '__main__':
    main()
