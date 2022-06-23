import socket

# tcp server
self_ip = "0.0.0.0"
self_port = 3516
BUFFER_SIZE = 20

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((self_ip, self_port))
sock.listen(5)

conn, addr = sock.accept()
print('Connection address:', addr)
while 1:
    # data = 'test'
    # conn.send(data.encode('utf-8'))
    recv = conn.recv(BUFFER_SIZE).decode()
    print(recv)
conn.close()

# udp
# target_ip = "192.168.10.169"
# target_port = 3516
# msg = "test"
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.sendto(msg, (target_ip, target_port))
# data, addr = sock.recvfrom(1024)
# print("received message: %s" % data)