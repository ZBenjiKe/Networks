from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP
from socket import *

app_domain = "www.dashserver.com"

def DNS_Reply():
    dnsRequest, clientAddress = serverSocket.recvfrom(2048)
    print("Got request from client.")

    # Define the DNS query we want to respond to
    query = DNS(rd=1, qd=DNSQR(qname=app_domain))

    # Define the fake DNS response we want to send
    response = DNSRR(rrname=app_domain, type="A", ttl=60, rdata="127.0.0.1")

    # Construct the IP header
    ip = IP(dst=clientAddress[0], src="127.0.0.1")

    # Construct the UDP header
    udp = UDP(sport=53, dport=clientAddress[1])

    # Construct the DNS packet by concatenating the query and response
    dns_packet = query / response

    # Send the fake DNS response
    response = ip / udp / dns_packet

    # send(ip/udp/dns_packet)

    serverSocket.sendto(response.encode(), clientAddress)

    serverSocket.close()

if __name__ == '__main__':
    serverPort = 53
    SERVER_ADDRESS = ('', serverPort)
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(SERVER_ADDRESS)
    while True:
       print("The DNS server is ready to receive requests.")
       DNS_Reply()