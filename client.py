import socket
import os
import sys

LIMIT_LENGTH = 200                          # limit total length of control message including file name

# Command line checks
if len(sys.argv) != 3:
    print(f"Usage: python3 {sys.argv[0]} <Server Name> <Port Number>")

serverName = sys.argv[1]
serverAddr = socket.gethostbyname(serverName)
serverPort = int(sys.argv[2])

serverControlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # create a TCP socket
serverControlSock.connect((serverAddr, serverPort))                         # connect to the server


def sendAll(sock, anyData):
    """
    From a specified socket, send specified number of bytes.
    """
    numSent = 0
    while len(anyData) > numSent:
        numSent += sock.send(anyData[numSent:])


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


def transformControlMessage(anyControlMesasge):
    """
    Append SPACE to the string until its size is < LIMIT_LENGTH.
    """
    while len(anyControlMesasge) < LIMIT_LENGTH:
        anyControlMesasge = anyControlMesasge + " "

    return anyControlMesasge.encode()


while True:
    command = input("ftp> ")
    clientSideSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSideSock.bind(('', 0))                                # Bind the socket to port 0
    clientSideSockPort = clientSideSock.getsockname()[1]        # Retrieve the ephemeral port number
    clientSideSock.listen(1)                                    # Start listening on the socket (client side)

    if command == "quit":
        sendAll(serverControlSock,transformControlMessage(command))
        break


    elif command[0:3] == "get":
        command = str(clientSideSockPort) + command
        sendAll(serverControlSock, transformControlMessage(command))

        serverDataSock, addr = clientSideSock.accept()          # Accept connections
        saveFileName = command[9:].strip()                      # Get filename

        controlMessage = serverControlSock.recv(20)             # check whether file is present or not
        testString = controlMessage.strip()
        if testString == b'FILE NOT FOUND':
            print("File not found!\n")
            continue

        bytesReceived = 0
        while True:
            chunkData = ""                                      # The buffer of chunk data received from the the server.
            chunkSizeBuff = ""                                  # The buffer containing the chunk size
            chunkSizeBuff = recvAll(serverDataSock, 10)         # Receive the first 10 bytes indicating the size of the chunk
            chunkSize = int(chunkSizeBuff)                      # Get the chunk size
            bytesReceived += chunkSize
            chunkData = recvAll(serverDataSock, chunkSize)      # Get the chunk data

            if bytesReceived <= 65536:                          # first chunk
                file = open(saveFileName, 'wb')                 # create file and write
            else:
                file = open(saveFileName, 'ab')                 # append

            file.write(chunkData)
            file.close()

            if chunkSize < 65536:                               # check if file is sent
                break;

        clientSideSock.close()
        sendAll(serverControlSock,str(bytesReceived).encode())
        print("Filename is ", saveFileName)
        print("Number of bytes received are ", bytesReceived, "bytes\n")


    elif command[0:3] == "put":
        nameFileGet = command[4:]
        command = str(clientSideSockPort) + command
        sendAll(serverControlSock, transformControlMessage(command))
        serverDataSock, addr = clientSideSock.accept()      # Accept connections

        try:
            fileObj = open(nameFileGet, "rb")
            fileData = fileObj.read()
            dataSize = len(fileData)
            bytesSent = 0
            sendAll(serverControlSock,"FILE FOUND    ".encode())
            
            while bytesSent < dataSize:                     # Keep sending until all is sent
                if bytesSent + 65536 < dataSize:            # Read 65536 bytes of data
                    fileDataChunk = fileData[bytesSent:bytesSent+65536]
                else:
                    fileDataChunk = fileData[bytesSent:]
                bytesSent += 65536

                dataSizeChunk = str(len(fileDataChunk))     # Get the size of the data and convert it to string

                while len(dataSizeChunk) < 10:              # Prepend 0's to the string until the size is 10 bytes
                    dataSizeChunk = "0" + dataSizeChunk

                fileDataChunk = dataSizeChunk.encode() + fileDataChunk  # Prepend the size of the data to the file data.
                sendAll(serverDataSock, fileDataChunk)

            fileObj.close()
            saveFileName = command[9:].strip()
            controlMessage = serverControlSock.recv(10)
            bytesTransfered = int(controlMessage.decode())
            print("Filename is ", saveFileName)
            print("Number of bytes transferred are ", bytesTransfered, "bytes\n")
            sendAll(serverControlSock,str(dataSize).encode())

        except FileNotFoundError:
            print("File '", nameFileGet, "' not found!")
            sendAll(serverControlSock,"FILE NOT FOUND".encode())
        clientSideSock.close()


    elif command == "ls":
        command = str(clientSideSockPort) + command
        sendAll(serverControlSock, transformControlMessage(command))
        serverDataSock, addr = clientSideSock.accept()          # Accept connections
        bytesReceived = 0

        while True:                      
            chunkData = ""                                      # The buffer of chunk data received from the the server.
            chunkSizeBuff = ""                                  # The buffer containing the chunk size
            chunkSizeBuff = recvAll(serverDataSock, 10)         # Receive the first 10 bytes indicating the size of the chunk
            chunkSize = int(chunkSizeBuff)                      # Get the chunk size
            bytesReceived += chunkSize

            if chunkSize == 0:                                  # no file in server
                break

            chunkData = recvAll(serverDataSock, chunkSize)
            print(chunkData.decode())

            if chunkSize < 65536:
                break;

        clientSideSock.close()
        controlMessage = serverControlSock.recv(10)             # assume that file is not larger than 9.9GB
        testInt = int(controlMessage.decode())

        if testInt == bytesReceived:
            sendAll(serverControlSock,"SUCCESS".encode())
        else:
            sendAll(serverControlSock,"FAILURE".encode())
    else:
        print("Only 'get, put, ls, quit' commands are supported")

serverControlSock.close()
