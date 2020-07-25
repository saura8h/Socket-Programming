import socket
import sys
import subprocess

LIMIT_LENGTH = 200                          # limit total length of control message including file name

# Command line checks
if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} <Port Number>")

listenPort = int(sys.argv[1])                                           # listen to incoming connections on port (eg: 1234)

serverSideSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # create a server side socket
serverSideSock.bind(('', listenPort))                                   # bind the socket to the port
serverSideSock.listen(1)                                                # start listening on the socket

def recvAll(sock, numBytes):
    """
    From a specified socket, receive a specified number of bytes.
    Return the total number of bytes received.
    """
    recvBuff = "".encode()                  # receive buffer; convert string to bytes
    tmpBuff  = "".encode()                  # temporary buffer; convert string to bytes

    while len(recvBuff) < numBytes:         # receive complete data
        tmpBuff = sock.recv(numBytes)       # attempt to receive bytes

        if not tmpBuff:                     # client has closed the socket
            break

        recvBuff += tmpBuff                 # add the received bytes to the buffer

    return recvBuff


def sendAll(sock, anyData):
    """
    From a specified socket, send specified number of bytes.
    """
    numSent = 0
    while len(anyData) > numSent:
        numSent += sock.send(anyData[numSent:])


# Accept connections forever
while True:
    print("Waiting for connections...")
    clientControlSock, addr = serverSideSock.accept()
    print("Accepted connection from client: ", addr,"\n")
    clientSideSockIP = addr[0]

    while True:
        controlMessage = recvAll(clientControlSock, LIMIT_LENGTH)
        input_string = controlMessage.strip()
        serverDataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if input_string == b'quit':
            print("Receive 'quit' control message from client - SUCCESS!\n")
            break;

        elif input_string[5:8] == b'get':
            file_name = input_string[9:]
            clientSideSockPort = int(input_string[0:5])
            print("Trying to connect to the client socket ", clientSideSockIP, " on port: ", clientSideSockPort, "\n")
            serverDataSock.connect((clientSideSockIP, clientSideSockPort))      # connect to the client

            try:
                fileObj = open(file_name, "rb")
                fileData = fileObj.read()
                dataSize = len(fileData)
                bytesSent = 0
                sendAll(clientControlSock,"FILE FOUND".encode())

                while bytesSent < dataSize:                         # Keep sending until all is sent
                    if bytesSent + 65536 < dataSize:                # Read 65536 bytes of data
                        fileDataChunk = fileData[bytesSent:bytesSent+65536]
                    else:
                        fileDataChunk = fileData[bytesSent:]
                    bytesSent += 65536

                    dataSizeChunk = str(len(fileDataChunk))         # get the size of the data read and convert it to string
                    while len(dataSizeChunk) < 10:                  # prepend 0's to the size string until the size is 10 bytes << need for last chunk
                        dataSizeChunk = "0" + dataSizeChunk

                    fileDataChunk = dataSizeChunk.encode() + fileDataChunk      # prepend the size of the data to the file data.
                    sendAll(serverDataSock, fileDataChunk)

                fileObj.close()
                controlMessage = clientControlSock.recv(10)
                bytesTransfered = int(controlMessage.decode())

                if dataSize == bytesTransfered:
                    print("File '", file_name.decode().strip(), "' successfully sent to client!\n")
                else:
                    print("File '", file_name.decode().strip(), "' not sent to client...\n")

            except FileNotFoundError:
                print("File '", file_name.decode().strip(), "' not found! - FAILURE\n")
                sendAll(clientControlSock,"FILE NOT FOUND".encode())   # file not found
            serverDataSock.close()


        elif input_string[5:8] == b'put':
            file_name = input_string[9:]
            clientSideSockPort = int(input_string[0:5])
            print("Trying to connect to the client socket ", clientSideSockIP, " on port: ", clientSideSockPort, "\n")
            serverDataSock.connect((clientSideSockIP, clientSideSockPort))          # connect to the client
            controlMessage = clientControlSock.recv(14)                             # check whether file is present or not
            input_string = controlMessage.strip()

            if input_string == b'FILE NOT FOUND':
                print("File not found! - FAILURE\n")
                continue

            bytesReceived = 0
            while True:
                
                chunkData = ""                                      # The buffer to all data received from the the client.
                chunkSizeBuff = ""                                  # The buffer containing the chunk size
                chunkSizeBuff = recvAll(serverDataSock, 10)         # Receive the first 10 bytes indicating the size of the chunk
                chunkSize = int(chunkSizeBuff)                      # Get the chunk size
                bytesReceived += chunkSize                          # append chunk size to bytes received

                if chunkSize == 0:
                    print("File does not exist from client!\n")
                    break

                chunkData = recvAll(serverDataSock, chunkSize)      # Get chunk data

                if bytesReceived <= 65536:                          # first chunk
                    file = open(file_name, 'wb')                    # create file and write
                else:
                    file = open(file_name, 'ab')                    # append

                file.write(chunkData)
                file.close()

                if chunkSize < 65536:                               # check if it is last chunk
                    break;
                
            serverDataSock.close()
            sendAll(clientControlSock,str(bytesReceived).encode())
            controlMessage = clientControlSock.recv(10)
            testInt = int(controlMessage.decode())

            if testInt == bytesReceived:
                print("File '", file_name.decode().strip(), "' successfully received from client!\n")
            else:
                print("File '", file_name.decode().strip(), "' not received from client...\n")


        elif input_string[5:7] == b'ls':
            clientSideSockPort = int(input_string[0:5])
            print("Trying to connect to the client socket ", clientSideSockIP, " on port: ", clientSideSockPort, "\n")
            serverDataSock.connect((clientSideSockIP, clientSideSockPort))  # connect to the client
            fileData = subprocess.check_output(["ls -l"], shell=True)
            dataSize = len(fileData)
            bytesSent = 0

            while bytesSent < dataSize:
                if bytesSent + 65536 < dataSize:
                    fileDataChunk = fileData[bytesSent:bytesSent+65536]
                else:
                    fileDataChunk = fileData[bytesSent:]

                bytesSent += 65536
                dataSizeChunk = str(len(fileDataChunk))

                while len(dataSizeChunk) < 10:                              # prepend 0's to the size string until its size is 10 bytes
                    dataSizeChunk = "0" + dataSizeChunk

                fileDataChunk = dataSizeChunk.encode() + fileDataChunk      # prepend the size of the data to the file data
                sendAll(serverDataSock, fileDataChunk)

            sendAll(clientControlSock,str(dataSize).encode())               # check if client received data completely
            controlMessage = recvAll(clientControlSock, 7)
            input_string = controlMessage.strip()
            if input_string == b'SUCCESS':
                print("ls command output sent successfully!!\n")
            else:
                print("ls command output error...\n")

            serverDataSock.close()
        else:
            break

    clientControlSock.close()
    print("Connection closed from client: ", addr, "\n")
    break
