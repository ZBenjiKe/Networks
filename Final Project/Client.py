from socket import *

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