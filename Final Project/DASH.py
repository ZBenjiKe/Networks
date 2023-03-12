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
    print("Recieved connection from client ",addrClient)

    message = "Hello!\nThere are 25 video frames available for this video.\nPlease select the video quality you would like:\n720, 480 or 360\n"
    clientSocket.send(bytes(message.encode()))
    quality = clientSocket.recv(1024).decode()

    img_dir = os.getcwd()+"/Pictures"
    frameCount = 1

    while(frameCount <= 25):
        start = time.perf_counter()
        imageFile = img_dir+f'/{quality}'+f"/{frameCount}.png"
        with open(imageFile, "rb") as imageFile:
            imageStr = imageFile.read()
        clientSocket.sendall(imageStr)
        clientSocket.send("Finished".encode())
        frameCount += 1
        ack = clientSocket.recv(1024)
        finish = time.perf_counter()
        new_quality = verifyQuality(start, finish, quality)
        quality = new_quality
    print("Finished sending frames to client.")
    
    time.sleep(3)
    serverSocket.close()


def verifyQuality(start, finish, quality):
    if (finish - start) > 1 :
        if quality == "720":
            quality = "480"
            print("quality changed from 720 to 480")
        elif quality == "480":
            quality = "360"
            print("quality changed from 480 to 360")
    elif (finish - start) < 0.5 :
        if quality == "360":
            quality = "480"
            print("quality changed from 360 to 480")
        elif quality == "480":
            quality = "720"
            print("quality changed from 480 to 720")
    return quality


def main():
    sendImagesOverTCP()

if __name__ == '__main__':
    main()