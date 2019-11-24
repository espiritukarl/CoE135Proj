#SERVER 3 - one-to-one with audio(client only)

import threading
from threading import Thread
import time
import cv2
import io
import socket
import sys
import struct
import time
import pickle
import pyaudio
import select

trigger = 0

# Define a function for the thread
def server(HOST, PORT):
   print('SERVER: Preparing sockets for connection...')
   s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   s.bind((HOST,PORT))
   s.listen(10)
   print('SERVER: Sockets prepared and ready.')

   conn,addr=s.accept()

   data = b""
   payload_size = struct.calcsize(">L")
   print("SERVER: payload_size: {}".format(payload_size))

   while True:
      while len(data) < payload_size:
        #print("Recv: {}".format(len(data)))
        data += conn.recv(4096)
      global trigger
      trigger += 1
      #print("Receiving: {}".format(len(data)))
      packed_msg_size = data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack(">L", packed_msg_size)[0]
      #print("SERVER: Packet Size: {}".format(msg_size))
      while len(data) < msg_size:
        data += conn.recv(4096)
      frame_data = data[:msg_size]
      data = data[msg_size:]

      frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
      frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
      cv2.imshow('SERVER: Friend Camera',frame)

      if cv2.waitKey(1) & 0xFF == ord('q'):   #press q on window to stop
         break

def client(HOST, PORT):
  print("CLIENT Starting...")
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((HOST, PORT))
  connection = client_socket.makefile('wb')

  cam = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

  cam.set(3, 640)
  cam.set(4, 480)

  img_counter = 0

  encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

  while True:
    ret, frame = cam.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    #data = zlib.compress(pickle.dumps(frame, 0))
    data = pickle.dumps(frame, 0)
    size = len(data)

    #print("{}: {}".format(img_counter, size))
    client_socket.sendall(struct.pack(">L", size) + data)
    img_counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
      break

  cam.release()
  cv2.destroyAllWindows()

def audios(HOST,PORT): #ME
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 44100
  CHUNK = 4096

  audio = pyaudio.PyAudio()

  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind((HOST, PORT))
  serversocket.listen(5)

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

def audioc(HOST,PORT): #FRIEND
  #PLAYS THE STREAM

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
  print ("finished recording")
  
  serversocket.close()
  # stop Recording
  stream.stop_stream()
  stream.close()
  audio.terminate()


print("YOU ARE THE MAIN HOST!")
#HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address
#HOST2 = input("Enter Client IP ADDRESS:\n")        # check ipconfig for an available local iPV4 address

HOST = "192.168.100.6"
HOST2 = "192.168.100.17"

PORT = 9898
PORT2 = 8787
PORTAS = 4848
PORTAC = 4545


#MULTITHREADING PART (SERVER THEN CLIENT)

t = Thread(target=server, args=(HOST,PORT))
#t.daemon = True
t.start()

t2 = Thread(target=audios, args=(HOST,PORTAS))
#t2.daemon = True
t2.start()

#t3.daemon = True


while True:
  if(trigger >20):
    print("TRIGGER!")
    #t3 = Thread(target=audioc, args=(HOST2,PORTAC))
    #t3.start()
    client(HOST2,PORT2)
    break


