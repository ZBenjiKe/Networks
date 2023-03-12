import requests
from socket import *
import os
import time

img_urls_files = [
    '''
    fill in urls - from files
    '''
]

img_urls_website = [
    '''
    option to download project images from github repo
    '''
    'https://images.unsplash.com/photo-1538991383142-36c4edeaffde',
    'https://images.unsplash.com/photo-1430990480609-2bf7c02a6b1a'
]

'''
def downloadImage(img_url):
    img_bytes = requests.get(img_url).content
    img_name = img_url.split('/')[3]
    img_name = f'{img_name}.jpg'
    with open(img_name, 'wb') as img_file:
    img_file.write(img_bytes)
    print(f'{img_name} was downloaded')

'''


def sendImagesOverTCP():
    SERVER_ADDRESS = ('', 30577)
    # serverSocket = socket.socket()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(SERVER_ADDRESS)
    serverSocket.listen(1)
    print("The DASH server is ready for connections.")

    clientSocket, addrClient = serverSocket.accept()
    print("Recieved connection from client ", addrClient)

    message = "Hello from DASH!\nThere are 25 video frames available for this video.\nPlease select the video quality you would like:\n720, 480 or 360\n"
    clientSocket.send(bytes(message.encode()))
    quality = clientSocket.recv(1024).decode()

    img_dir = os.getcwd() + "/Pictures"
    frameCount = 1

    while (frameCount <= 25):
        start = time.perf_counter()
        imageFile = img_dir + f'/{quality}' + f"/{frameCount}.png"
        with open(imageFile, "rb") as imageFile:
            imageStr = imageFile.read()
        clientSocket.sendall(imageStr)
        clientSocket.send("Finished".encode())
        frameCount += 1
        ack = clientSocket.recv(1024)
        finish = time.perf_counter()
        new_quality = verifyTCPQuality(start, finish, quality)
        quality = new_quality
    print("Finished sending frames to client.")

    time.sleep(3)
    serverSocket.close()


def verifyTCPQuality(start, finish, quality):
    if (finish - start) > 1:
        if quality == "720":
            quality = "480"
            print("quality changed from 720 to 480")
        elif quality == "480":
            quality = "360"
            print("quality changed from 480 to 360")
    elif (finish - start) < 0.5:
        if quality == "360":
            quality = "480"
            print("quality changed from 360 to 480")
        elif quality == "480":
            quality = "720"
            print("quality changed from 480 to 720")
    return quality

#
# def receive_syn_message():
#     # Receive SYN message from the client
#     syn_message, address = serverSocket.recvfrom(BUFFER_SIZE)
#     print('Received SYN message from client:', syn_message.decode())
#     return syn_message, address
#
#
# def send_syn_ack_message(syn_message, address):
#     # Send SYN-ACK message to the client
#     global sequence_number
#     syn_ack_message = 'SYN-ACK:{}:{}'.format(syn_message.decode(), sequence_number)
#     serverSocket.sendto(syn_ack_message.encode(), address)
#     print('Sent SYN-ACK message to client:', syn_ack_message)
#
#
# def receive_ack_message(clientAddress):
#     # Receive ACK message from the client
#     global expected_sequence_number
#     ack_message, address = serverSocket.recvfrom(BUFFER_SIZE)
#     if ack_message.decode().startswith('ACK:') & clientAddress == address:
#         ack_sequence_number = int(ack_message.decode().split(':')[1])
#         if ack_sequence_number == expected_sequence_number:
#             print('Received ACK message from client:', ack_message.decode())
#             expected_sequence_number += 1
#             return True
#     return False
#

def sendImagesOverRUDP():
    SERVER_ADDRESS = ('', 30577)
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(SERVER_ADDRESS)
    print("The DASH server is ready for connections.")
    serverSocket.settimeout(30)

    # Define a buffer size for receiving data
    BUFFER_SIZE = 1024

    buffer, client_address = serverSocket.recvfrom(BUFFER_SIZE)
    print("Received request from client:", buffer.decode(), client_address)

    message = "Hello from DASH!\nThere are 25 video frames available for this video.\nPlease select the video quality you would like:\n720, 480 or 360\n"
    serverSocket.sendto(message.encode(), client_address)
    quality, client_address = serverSocket.recvfrom(BUFFER_SIZE)
    quality = quality.decode()

    img_dir = os.getcwd() + "/Pictures"
    frameCount = 1

    while frameCount <= 25:
        start = time.perf_counter()
        imageFile = img_dir + f'/{quality}' + f"/{frameCount}.png"
        sendImage(imageFile, frameCount, client_address, serverSocket)
        finish = time.perf_counter()
        new_quality = verifyUDPQuality(start, finish, quality)
        quality = new_quality
        frameCount += 1

    print("Finished sending frames to client.")
    time.sleep(3)
    serverSocket.close()


def sendImage(imageFile, frameCount, client_address, serverSocket):
    global resend_sequence
    with open(imageFile, "rb") as img:
        while True:
            image_data = img.read(1000)
            if not image_data:
                break

            # Define the sequence number and expected sequence number
            window = 4
            sequence_number = 0
            expected_ack_number = 0
            unACKed = 0

            # Construct the data message
            segment = f"Data:{frameCount}:{sequence_number}:{len(image_data)}".encode() + image_data

            # Send the data message
            serverSocket.sendto(segment, client_address)
            print(f"Sent data message to client: Frame {frameCount}, Seq {sequence_number}")
            # Define a buffer size for receiving data
            BUFFER_SIZE = 1024
            # Wait for acknowledgement
            ack_received = False
            nack_received = False
            while not ack_received or not nack_received:
                try:
                    serverSocket.settimeout(timeout)
                    ack, _ = serverSocket.recvfrom(BUFFER_SIZE)
                    if ack.decode() == f"Ack:{sequence_number}":
                        ack_received = True
                    if int(ack.decode("utf-8").split(":")[0]) == "Send":
                        nack_received = True
                        resend_sequence = int(ack.decode("utf-8").split(":")[1])
                    expected_sequence_number += 1
                    sequence_number += 1

                except socket.timeout:
                    print(f"Timeout occurred while waiting for ACK of sequence number {sequence_number}")
                    congestion_window = max(1, congestion_window // 2)  # divide congestion window by 2 on timeout
                    sequence_number = expected_sequence_number  # reset sequence number to last successfully transmitted frame

            if nack_received == True:
                resend(resend_sequence)
            sequence_number = 1
            expected_sequence_number = 1
            congestion_window = 1
            flow_control_window = 1024  # maximum amount of data to send in one go
            threshold = 16
            timeout = 5  # in seconds

            # Send termination message
        serverSocket.sendto(b"Finished", client_address)

        # Perform congestion control
        if congestion_window < flow_control_window:
            congestion_window += 1
        if congestion_window >= threshold:
            k = (congestion_window - threshold) / congestion_window
            congestion_window = round(congestion_window * (k * k * k) + congestion_window)
        else:
            congestion_window += 1


def verifyUDPQuality(start, finish, quality):
    if (finish - start) > 1:
        if quality == "720":
            quality = "480"
            print("quality changed from 720 to 480")
        elif quality == "480":
            quality = "360"
            print("quality changed from 480 to 360")
    elif (finish - start) < 0.5:
        if quality == "360":
            quality = "480"
            print("quality changed from 360 to 480")
        elif quality == "480":
            quality = "720"
            print("quality changed from 480 to 720")
    return quality


def main():
    # sendImagesOverTCP()
    sendImagesOverRUDP()


if __name__ == '__main__':
    main()
