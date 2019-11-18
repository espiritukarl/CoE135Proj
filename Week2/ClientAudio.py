from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import pyaudio
from array import array


HOST = input("Enter Host IP:\n")        # check ipconfig for an available local iPV4 address
PORT = int(input("Enter Desired PORT:\n"))  #input 0000 - 9999 as port
BufferSize = 4096

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

def send():
    while True:
        data = voice_stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")
        else:
            print("Silence..")
        client.sendall(data)


def receive():
    while True:
        data = recvall(BufferSize)
        voice_stream.write(data)

def recvall(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += client.recv(4 * CHUNK)
        else:
            databytes += client.recv(to_read)
    return databytes

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

audio=pyaudio.PyAudio()
voice_stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)


receive_thread = Thread(target=receive).start()
send_thread = Thread(target=send).start()
