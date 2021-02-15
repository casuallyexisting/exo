import socket

HOST = "127.0.0.1"
PORT = 25077

while True:
    sock = socket.socket()
    sock.connect((HOST, PORT))
    outbound_message = 'TERMINAL://' + input("You: ")
    sock.sendall(outbound_message.encode('utf-8'))
    data = sock.recv(16384)
    if data:
        print('AI:', data.decode())
        sock.close()
