from cgi import print_arguments
import socket
import signal
import sys
import os
import time

# tcp server
self_ip = "0.0.0.0"
# self_port = 3516
self_port = 3861
BUFFER_SIZE = 20

conn = None

def do_exit(sig, stack):
    print("Try to shutdown socket connection")
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    sys.exit(0)
 
signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGUSR1, do_exit)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((self_ip, self_port))

print(f"Bind IP: {self_ip}, Port: {self_port}")
sock.listen(5)

print("Waiting to accept connection.")
conn, addr = sock.accept()
print('Connection address:', addr)
while 1:
    data = input()
    print("Start to send inputs: ", data)
    conn.send(data.encode('utf-8'))
    print("Success!")
    # recv = conn.recv(BUFFER_SIZE).decode()
    # print("Receive data: ", recv)
conn.shutdown(socket.SHUT_RDWR)
conn.close()

# udp
# target_ip = "192.168.10.169"
# target_port = 3516
# msg = "test"
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.sendto(msg, (target_ip, target_port))
# data, addr = sock.recvfrom(1024)
# print("received message: %s" % data)