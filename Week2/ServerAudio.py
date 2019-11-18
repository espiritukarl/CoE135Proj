from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


HOST = input("Enter Host IP:\n")        # check ipconfig for an available local iPV4 address
PORT = int(input("Enter Desired PORT:\n"))  #input 0000 - 9999 as port
Buffersize = 4096
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024
addresses = {}

def receive():
    while True:
        try:
            client, addr = server.accept()
            print("{} is connected!!".format(addr))
            addresses[client] = addr
            Thread(target=ClientAudio, args=(client, )).start()
        except:
            continue

def ClientAudio(client):
    while True:
        try:
            data = client.recv(Buffersize)
            broadcastSound(client, data)
        except:
            continue

def broadcastSound(clientSocket, data_to_be_sent):
    for client in addresses:
        if client != clientSocket:
            client.sendall(data_to_be_sent)


server = socket(family=AF_INET, type=SOCK_STREAM)
print('Preparing sockets for connection...')
server.bind((HOST,PORT))
server.listen(10)
print('Sockets prepared and ready.')

try:
    server.bind((HOST, PORT))
except OSError:
    print("Server Busy")

server.listen(2)
print("Waiting for connection..")

AcceptThread = Thread(target=receive)
AcceptThread.start()
AcceptThread.join()
