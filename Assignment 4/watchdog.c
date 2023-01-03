/* TCP Server */

/* Included Libraries */
#include <stdio.h>
#include <stdlib.h> 
#include <errno.h> 
#include <string.h> 
#include <sys/types.h> 
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <fcntl.h>
#include <signal.h>

/* Macros */
#define WATCHDOG_PORT 3000

int main() {

    printf("hello partb\n");

    // Create socket for receiving files. This socket acts as a TCP server socket.
    int wdSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (wdSocket == -1){
        printf("Socket not created: %d", errno);
        exit(0);
    }

    // If the socket is closed, wait 30-120 seconds before final removal in case of reuse.
    int enableReuse = 1;
    int reuseStatus = setsockopt(wdSocket, SOL_SOCKET, SO_REUSEADDR, &enableReuse, sizeof(int));
    if (reuseStatus == -1) {
        printf("setsockopt() failed with error code : %d", errno);
        close(wdSocket);
        exit(0);
    }

    // Create internet socket-address object, named serverAddress. Will accept connections from all IPs.
    struct sockaddr_in serverAddress;
    memset(&serverAddress, 0, sizeof(serverAddress));
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(WATCHDOG_PORT);

    // Bind the socket to the Receiver's given internet address.
    int bindStatus = bind(wdSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress));
    if (bindStatus == -1){
        printf("Bind failed with error code : %d" , errno);
        close(wdSocket);
        exit(0);
    }

    // Put socket in listening mode, waiting for connections.
    int listenStatus = listen(wdSocket, 5);
    if (listenStatus == -1){
        printf("Listen failed with error code : %d" , errno);
        close(wdSocket);
        exit(0);
    }

    // Create internet socket-address object, named clientAddress, for connections made with Receiver.
    struct sockaddr_in clientAddress;
    socklen_t clientAddressLen = sizeof(clientAddress);
    memset(&clientAddress, 0, clientAddressLen);

    // Accept a connection from a client
    int clientSocket = accept(wdSocket, (struct sockaddr *)&clientAddress, &clientAddressLen);
    if (clientSocket == -1) {
        printf("listen failed with error code : %d" ,errno);
        close(clientSocket);
        exit(0);
    }
    
    int wdReady = 1;
    send(clientSocket, &wdReady, 1, 0);

    char destIP[16];
    bzero(destIP, 16);
    int recvStatus = recv(clientSocket, destIP, 16, 0);
    if(recvStatus < 1) {
        printf("Destination IP wasn't received correctly");
        close(clientSocket);
        return -1;
    }

    char pingStatus[5];
    int timer = 0;
    int flag = 1;

    while(flag){
        recv(clientSocket, pingStatus, sizeof(pingStatus), 0);
        if(strcmp("ping", pingStatus) == 0) {
            printf("Started timer\n");
            fcntl(clientSocket, F_SETFL, O_NONBLOCK);
            while (timer < 10) {
                timer++;
                recv(clientSocket, pingStatus, sizeof(pingStatus), 0);
                if(strcmp("pong", pingStatus) == 0){
                    timer = 0;
                    fcntl(clientSocket, F_SETFL, O_NONBLOCK);
                    break;
                }
                sleep(1);
            }
            printf("Exit timer\n");
            if(timer == 10){
                printf("Timeout");
                flag = 0;
            }
        }
    }
    printf("Server %s cannot be reached.\n", destIP);

    char exitCode[8] = "Timeout";
    fcntl(clientSocket, F_SETFL, O_NONBLOCK);
    send(clientSocket, exitCode, sizeof(exitCode), 0);

    close(clientSocket);
    close(wdSocket);
    return 0;
}