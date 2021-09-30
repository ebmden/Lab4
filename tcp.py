"""
- CS2911 - 011
- Fall 2021
- Lab 4 - Receiving Messages
- Names:
  - Lucas Gral
  - Eden Basso

A simple TCP server/client pair.

The application protocol is a simple format: For each file uploaded, the client first sends four (big-endian) bytes indicating the number of lines as an unsigned binary number.

The client then sends each of the lines, terminated only by '\\n' (an ASCII LF byte).

The server responds with 'A' when it accepts the file.

Then the client can send the next file.


Introduction: (Describe the lab in your own words) - LG




Summary: (Summarize your experience with the lab, what you learned, what you liked, what you disliked, and any suggestions you have for improvement) - EB




"""

# import the 'socket' module -- not using 'from socket import *' in order to selectively use items with 'socket.' prefix
import socket
import struct
import time
import sys
import os

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = 'localhost'  # empty by default

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = 'localhost'


def main():
    """
    Allows user to either send or receive bytes
    """
    # Get chosen operation from the user.
    action = input('Select "(1-TS) tcpsend", or "(2-TR) tcpreceive":')
    # Execute the chosen operation.
    if action in ['1', 'TS', 'ts', 'tcpsend']:
        tcp_send(OTHER_HOST, TCP_PORT)
    elif action in ['2', 'TR', 'tr', 'tcpreceive']:
        tcp_receive(TCP_PORT)
    else:
        print('Unknown action: "{0}"'.format(action))


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket

    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    while num_lines != 0:
        print('Now enter all the lines of your message')
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        tcp_socket.sendall(b'\x00\x00')
        time.sleep(1)  # Just to mess with your servers. :-)
        tcp_socket.sendall(b'\x00' + bytes((num_lines,)))

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input('')
            tcp_socket.sendall(line.encode() + b'\n')

        print('Done sending. Awaiting reply.')
        response = tcp_socket.recv(1)
        if response == b'A':  # Note: == in Python is like .equals in Java
            print('File accepted.')
        else:
            print('Unexpected response:', response)

        num_lines = int(input('Enter the number of lines you want to send (0 to exit):'))

    tcp_socket.sendall(b'\x00\x00')
    time.sleep(1)  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b'\x00\x00')
    response = tcp_socket.recv(1)
    if response == b'Q':  # Reminder: == in Python is like .equals in Java
        print('Server closing connection, as expected.')
    else:
        print('Unexpected response:', response)

    tcp_socket.close()


def tcp_receive(listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.

    :param int listen_port: Port number on the server to listen on
    :author: Lucas Gral
    """

    print('tcp_receive (server): listen_port={0}'.format(listen_port))

    listen_socket = create_listen_socket(listen_port)
    data_socket = create_data_socket(listen_socket)
    # print adress of data socket, maybe create_data_socket should return a tuple (data_socket, client_IP)

    receive_data(data_socket, 1) #TODO: test once everything else is implemented (delete these TODO comments if they stop you from pushing to the repo)

    listen_socket.close()
    data_socket.close()


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.

    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.

    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


def create_listen_socket(listen_port):
    """
    Creates the socket that listens for any connections.

    :param listen_port: The port to listen on
    :return: the listening socket
    :rtype: socket.pyi
    :author: Lucas Gral
    """
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((LISTEN_ON_INTERFACE, listen_port))
    listen_socket.listen(1) #accept 1 connection
    #listenSocket.accept() is done in create_data_socket()
    return listen_socket


def create_data_socket(listen_socket):
    """
    Creates a client data socket and connects it to the server

    :param socket.pyi listen_socket: socket that listens for a signal
    :return: the socket that receives data
    :rtype: socket.pyi
    :author: Eden Basso
    """
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((OTHER_HOST, TCP_PORT))
    (data_socket, sender_address) = listen_socket.accept()
    return data_socket


def receive_data(data_socket, file_number):
    """
    Recursive function that receives data from the socket connection until an empty line is received.
    Receiving lines is handled by receive_lines
    Saving the results to a file is handled by write_lines_to_file

    :param data_socket: the socket to receive from and send to
    :param file_number: the Nth recursion of this function for the filename; should start at 1
    :author: Lucas Gral
    """
    num_lines = receive_num_lines(data_socket)
    lines = receive_lines(data_socket, num_lines)
    write_lines_to_file(lines, file_number)
    if num_lines > 0:
        #RESPOND 'A'
        data_socket.sendall(b'A')
        receive_data(data_socket, file_number+1) #recurse
    else:
        #RESPOND 'Q'
        data_socket.sendall(b'Q')


def receive_num_lines(data_socket):
    """
    gets the number of lines for the next file (assuming the next data to be received is the number of lines)

    :param data_socket: the socket to receive on
    :return: the number of lines
    :rtype: int
    :author: Lucas Gral
    """
    num_lines_bytes = b''
    for i in range(0, 4): #call four times
        num_lines_bytes += next_byte(data_socket)

    return int.from_bytes(num_lines_bytes, 'big') #TODO: double check once test-able


def receive_lines(data_socket, num_lines):
    """
    Determines the size of each line in order to convert data into bytes object

    :param socket.pyi data_socket: the socket to receive on
    :param int num_lines: the number of lines of data that need to be iterated through
    :return: the message that will be sent to a text file
    :rtype: any
    :author: Eden Basso
    """
    # use next_byte() to iterate through each line in data_socket num_lines times to find the size of each line
    response_size = 0
    byte_line = b''
    for i in range(num_lines):
        while (message_byte := next_byte(data_socket)) != b'\x0d\x0a':
            byte_line = byte_line + message_byte
            response_size = response_size + 1
        byte_line = byte_line + b'\n'
    data = data_socket.recv(response_size)
    return data


def write_lines_to_file(lines, file_number):
    """
    Writes raw bytes object into a file until an empty file is written

    :param any lines: data in raw bytes ready to be stored in a file
    :param int file_number: the numeric order in which the current file is being written/names as
    :return: file with message
    :rtype: file
    :author: Eden Basso
    """
    does_exist = True
    while does_exist == True:
        file_number = str(file_number)
        does_exist = os.access('file' + file_number, os.F_OK)
        if does_exist == False:
            message_file = os.open('file' + file_number, os.O_CREAT | os.O_RDWR)
            os.write(message_file, lines)
            os.close(message_file)
        file_number = int(file_number)
        file_number = file_number + 1
    return message_file


# Invoke the main method to run the program.
main()
