import requests
from socket import *

img_urls_files = [
    '''
    fill in urls - from files
    '''
]

img_urls _website = [
'https://images.unsplash.com/photo-1538991383142-36c4edeaffde',
'https://images.unsplash.com/photo-1430990480609-2bf7c02a6b1a',
'https://images.unsplash.com/photo-1506038634487-60a69ae4b7b1',
'https://images.unsplash.com/photo-1509514026798-53d40bf1aa09',
'https://images.unsplash.com/photo-1533228876829-65c94e7b5025',
'https://images.unsplash.com/photo-1453060590797-2d5f419b54cb',
'https://images.unsplash.com/photo-1496692052106-d37cb66ab80c',
'https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22'
]


def downloadImage(img_url):
    img_bytes = requests.get(img_url).content
    img_name = img_url.split('/')[3]
    img_name = f'{img_name}.jpg'
    with open(img_name, 'wb') as img_file:
    img_file.write(img_bytes)
    print(f'{img_name} was downloaded')


def timer():
    start = time.perf_counter()
    downloadImage(img_url)
    finish = time.perf_counter()


def main():

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
                  "\t720 ......... 1\n" \
                  "\t480 ......... 2\n" \
                  "\t360 ......... 3\n"
        connectionSocket.send(bytes(message.encode()))
        initQuality = connectionSocket.recv(4096).decode()
        quality = initQuality
        frameCount = 0
        filePaths = []
        with open(filePaths[chosenQuality]):
            while(frameCount <= 25):
                with open(path)

    connectionSocket.close()


if __name__ == '__main__':
    main()