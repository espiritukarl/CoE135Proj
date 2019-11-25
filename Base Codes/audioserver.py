# Version 1.00 Audio Server w/ a working Client when opened

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from array import array
import pyaudio


HOST = input("Enter Host IP\n")
HOST2 = '127.0.0.1'
PORT = 4000

BufferSize = 4096
addresses = {}
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

def Connections():
    while True:
        try:
            client, addr = server.accept()
            print("{} is connected!!".format(addr))
            addresses[client] = addr
            Thread(target=ClientConnectionSound, args=(client, )).start()
        except:
            continue

def ClientConnectionSound(client):
    while True:
        try:
            data = client.recv(BufferSize)
            broadcastSound(client, data)
        except:
            continue

def broadcastSound(clientSocket, data_to_be_sent):
    for client in addresses:
        if client != clientSocket:
            client.sendall(data_to_be_sent)

def SendAudio():
    while True:
        data = stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")
        else:
            print("Silence..")
        client.sendall(data)

def RecieveAudio():
    while True:
        data = recvall(BufferSize)
        stream.write(data)

def recvall(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += client.recv(4 * CHUNK)
        else:
            databytes += client.recv(to_read)
    return databytes

#sockets
server = socket(family=AF_INET, type=SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
try:
    server.bind((HOST, PORT))
except OSError:
    print("Server Busy")

server.listen(5)

#threading:
print("Waiting for connection..")
AcceptThread = Thread(target=Connections)
AcceptThread.start()

#client
client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST2, PORT))

audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)


RecieveAudioThread = Thread(target=RecieveAudio).start()
SendAudioThread = Thread(target=SendAudio).start()
#end of client

AcceptThread.join()