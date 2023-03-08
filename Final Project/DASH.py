from socket import *

SERVER_ADDRESS = ('', 30577)
# serverSocket = socket.socket()
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(SERVER_ADDRESS)
serverSocket.listen(1)
print("The server is ready to receive.")

while True:
    connectionSocket, addrClient = serverSocket.accept()
    print("Recieved connection from client ",addrClient)
    message = "Hello!\nThere are 25 video frames available for this video. Please select the video quality you would like:\n"\
              "1080 ......... 1" \
              "720  ......... 2" \
              "480  ......... 3" \
              "360  ......... 4" \
              "240  ......... 5"
    connectionSocket.send(bytes(message.encode()))
    initQuality = connectionSocket.recv(4096).decode()
    quality = initQuality
    frameCount = 0
    filePaths = []
    with open(filePaths[chosenQuality]):
        while(frameCount <= 25):
            with open(path)

connectionSocket.close()