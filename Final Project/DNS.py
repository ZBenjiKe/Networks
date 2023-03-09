from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, UDP
from socket import *
import time

app_domain = "www.dashserver.com"

def DNS_Reply():
    dnsQuery, clientAddress = dns_socket.recvfrom(2048)
    print("Got request from client.")
    print(dnsQuery.show())

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

    print(str(response))

    dns_socket.sendto(bytes(response), clientAddress)
    
    print("Sent response.")
    time.sleep(1)
    dns_socket.close()

if __name__ == '__main__':
    dns_port = 53
    SERVER_ADDRESS = ('localhost', dns_port)
    dns_socket = socket(AF_INET, SOCK_DGRAM)
    dns_socket.bind(SERVER_ADDRESS)
    print("The DNS server is ready to receive requests.")
    DNS_Reply()
