import threading
from threading import Thread
import socket
import pyaudio
import wave
import sys
import pickle
import time
import struct


HOST = input("Enter Host IP:\n")        # check ipconfig for an available local iPV4 address
PORT = int(input("Enter Desired PORT:\n"))  #input 0000 - 9999 as port
BufferSize = 4096

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

def send():
    while True:
        sound = my_aud_msg.read(CHUNK) #read from stream
        #sound_arr = array('h',sound)create array of the read data    
        client.sendall(sound)         

def receive():
    while True:
        databytes = b''
        while len(databytes) != BufferSize: 
            if( (Buffersize-len(databytes)) > CHUNK): #read and append from socket 
                databytes += client.recv(CHUNK)
            else:
                databytes += client.recv(Buffersize-len(databytes)) #read and append remaining  data 

        my_aud_msg.write(sound) #play the sound

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

aud = pyaudio.PyAudio()
my_aud_msg = aud.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

#create threads for sending and receiving 

send_sound_thread = Thread(target=send)
send_sound_thread.start()
recv_sound_thread = Thread(target = receive)
recv_sound_thread.start()