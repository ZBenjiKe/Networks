from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP
from socket import *

serverPort = 53
SERVER_ADDRESS = ('', serverPort)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(SERVER_ADDRESS)
print("The DNS server is ready to receive requests.")

while True:
    dnsRequest, clientAddress = serverSocket.recvfrom(2048)
    print("Got request from client.")

    # Define the DNS query we want to respond to
    query = DNS(rd=1, qd=DNSQR(qname="dashserver.com"))

    # Define the fake DNS response we want to send
    response = DNSRR(rrname="dashserver.com", type="A", ttl=60, rdata="127.0.0.1")

    # Construct the IP header
    ip = IP(dst=clientAddress[0], src="127.0.0.1")

    # Construct the UDP header
    udp = UDP(sport=53, dport=clientAddress[1])

    # Construct the DNS packet by concatenating the query and response
    dns_packet = query/response

    # Send the fake DNS response
    response = ip/udp/dns_packet

   # send(ip/udp/dns_packet)

    serverSocket.sendto(str(response), clientAddress)

serverSocket.close()