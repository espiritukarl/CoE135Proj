#port assignment is ok 
#port where to receive other video is ok 
#server current code can't pass what it received
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
import tkinter
import pyaudio

def client1(HOST, PORT): #sends the data to server
  print("CLIENT1: Starting...")
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
    cv2.imshow('SELF CAMERA',frame)
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



# Define a function for the thread
def client2(HOST2, PORT2):   #receives data from server
    print("CLIENT2: Starting...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST2, PORT2))
    connection = client_socket.makefile('wb')

    data = b""
    payload_size = struct.calcsize(">L")
    print("CLIENT2: Starting Camera...")
    #print("payload_size: {}".format(payload_size))
    while True:
        while len(data) < payload_size:
            #print("Recv: {}".format(len(data)))
            data += client_socket.recv(4096)

        #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += client_socket.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow('Host Camera',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
          break


print("YOU ARE THE MAIN HOST!")
#HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address

#HOST = socket.gethostname()
#print('Your Socket Host Name:',HOST)
HOST = "169.254.251.99"
ports = {'5001':False,'6001':False,'7001':False}
addresses = {}
clients = {}
PORTU = 9999
PORT  = 1001
PORT2 = 2001
PORT3 = 3001
PORT4 = 4001

clientVideoSocketUniv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientVideoSocketUniv.connect((HOST, PORTU))

my_port = clientVideoSocketUniv.recv(4).decode() #wait for my port 

#multithreading 
t2 = Thread(target=client2, args=(HOST,PORT2)) #launch server video recv
t2.start()

ports[my_port] = True #I send my video here, make it occupied
t = Thread(target=client1, args=(HOST, int(my_port) )) #send my video to server
t.start()

#locate and launch my other receive ports 
#I receive from 2 other ports thus repeat it 2 times
for portnos in sorted(ports.keys()):
    if ports[portnos] == False:
        ports[portnos] = True # set true since i will already launch a receiving thread
        RecieveFrameThread1 = Thread(target=client2 , args=(HOST, int(portnos) ), daemon=True).start()
        print(portnos,' - Connected !')
        break

for portnos in sorted(ports.keys()):
    if ports[portnos] == False:
        ports[portnos] = True # set true since i will already launch a receiving thread
        RecieveFrameThread2 = Thread(target=client2 , args=(HOST, int(portnos) ), daemon=True).start()
        print(portnos,' - Connected !')
        break


