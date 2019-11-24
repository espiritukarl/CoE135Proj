
import threading
from threading import Thread
import time
import io
import socket
import sys
import struct
import time
import pyaudio
import select

trigger = 0

# Define a function for the thread
def server(HOST, PORT):
   print('SERVER: Preparing sockets for connection...')
   serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   serversocket.bind((HOST, PORT))
   serversocket.listen(5)
   print('SERVER: Sockets prepared and ready.')

   FORMAT = pyaudio.paInt16
   CHANNELS = 1
   RATE = 44100
   CHUNK = 4096

   audio = pyaudio.PyAudio()

   def callback(in_data, frame_count, time_info, status):
    for s in read_list[1:]:
        s.send(in_data)
    return (None, pyaudio.paContinue)

   # start Recording
   stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
   # stream.start_stream()

   read_list = [serversocket]
   print ("Sending Audio Data...")

   try:
    while True:
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is serversocket:
                (clientsocket, address) = serversocket.accept()
                read_list.append(clientsocket)
                print ("Sending Audio: Active")
            else:
                data = s.recv(1024)
                if not data:
                    read_list.remove(s)
   except KeyboardInterrupt:
    pass
   
   print ("finished recording")
  
   serversocket.close()
   # stop Recording
   stream.stop_stream()
   stream.close()
   audio.terminate()

def client(HOST, PORT):
  print("CLIENT Starting...")
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

print("YOU ARE THE MAIN HOST!")
HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address
HOST2 = input("Enter Client IP ADDRESS:\n")        # check ipconfig for an available local iPV4 address

PORT = 9898
PORT2 = 8787
PORTAS = 9899
PORTAC = 8788


#MULTITHREADING PART (SERVER THEN CLIENT)

t = Thread(target=server, args=(HOST,PORT))
t.daemon = True
t.start()


client(HOST2,PORT2)
    



