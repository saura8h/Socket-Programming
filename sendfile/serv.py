"""
This file implements a server for receiving a file sent using the sendfile()
method. The server receives a file and prints it's contents.
"""
import socket

server_port = 1234                              # listening port
welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a welcome socket
welcome_socket.bind(('', server_port))          # bind socket to port
welcome_socket.listen(1)                        # start socket for listening
print("The server is ready to receive")

def recvAll(sock, numBytes):
    """
    From a specified socket, receive a specified number of bytes.
    Return the total number of bytes received.
    """
    receive_buffer = "".encode()                # convert string to bytes
    temp_buffer    = "".encode()                # convert string to bytes

    while len(receive_buffer) < numBytes:       # receiving complete data
        temp_buffer =  sock.recv(numBytes)      # Attempt to receive bytes

        if not temp_buffer:                     # client has closed the socket
            break

        receive_buffer += temp_buffer           # add received bytes to buffer

    return receive_buffer

# ensure all data is received
while True:

    print("Waiting for connections...")
    clientSock, addr = welcome_socket.accept()  # accept connections

    print("Accepted connection from client: ", addr)
    print("\n")

    file_buffer = ""
    receive_buffer = ""
    file_size = 0
    file_size_buffer = ""

    file_size_buffer = recvAll(clientSock, 10)      # receive the first 10 bytes indicating file size
    file_size = int(file_size_buffer)
    print("The file size is ", file_size)
    file_buffer = recvAll(clientSock, file_size)    # file data
    print("The file data is: ")
    print(file_buffer.decode())

    clientSock.close()                              # close server
