#PLAYS THE STREAM

import pyaudio
import socket
import sys

HOST = input("Enter Host IP:\n")        # check ipconfig for an available local iPV4 address
PORT = int(input("Enter Desired PORT:\n"))  #input 0000 - 9999 as port

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
print("Playing...")

try:
    while True:
        data = s.recv(CHUNK)
        stream.write(data)
except KeyboardInterrupt:
    pass

print('Shutting down')
s.close()
stream.close()
audio.terminate()