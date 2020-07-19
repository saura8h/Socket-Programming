"""
This file illustrates how to send a file using an application-level protocol
where the first 10 bytes of the message (from client to server) contains the
file size and the rest contain the file data.
"""

import socket
import os
import sys

# command line argument check
if len(sys.argv) < 2:
    print("USAGE python " + sys.argv[0] + " <FILE NAME>")

serverAddr = "localhost"
serverPort = 1234

file_name = sys.argv[1]
file_obj  = open(file_name, "r")

conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # create a TCP socket
conn_sock.connect((serverAddr, serverPort))                      # connect to server

bytes_sent = 0
file_data  = None

# ensure all data is sent
while True:

    file_data = file_obj.read(65536)                    # read 65536 bytes of data

    if file_data:                                       # EOF not reached
        data_size_str = str(len(file_data))

        while len(data_size_str) < 10:                  # prepend 0's of size 10 bytes
            data_size_str = "0" + data_size_str

        file_data = data_size_str + file_data           # 10 byte header + actual data

        while len(file_data) > bytes_sent:              # send data
            bytes_sent += conn_sock.send(file_data[bytes_sent:].encode())

    else:                                               # EOF reached
        break

print("Sent ", bytes_sent, " bytes.")

# close the socket and the file
conn_sock.close()
file_obj.close()
