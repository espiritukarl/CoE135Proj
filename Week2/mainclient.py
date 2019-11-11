
import threading
from threading import Thread
import time
import cv2
import io
import socket
import struct
import time
import pickle

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

      #print("Receiving: {}".format(len(data)))
      packed_msg_size = data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack(">L", packed_msg_size)[0]
      print("SERVER: Packet Size: {}".format(msg_size))
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
   client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   client_socket.connect((HOST, PORT))
   connection = client_socket.makefile('wb')

   camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)

   camera.set(3, 640) #size1
   camera.set(4, 480) #size2

   img_counter = 0

   encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

   print("CLIENT: Starting Camera Application")
   while True:
      ret, frame = camera.read()
      result, frame = cv2.imencode('.jpg', frame, encode_param)
      #data = zlib.compress(pickle.dumps(frame, 0))
      data = pickle.dumps(frame, 0)
      size = len(data)

    #for debugging
    #print("Time{}: Size{}".format(img_counter, size))
    #client_socket.sendall(struct.pack(">L", size) + data)
    #img_counter += 1

      if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
        break

   camera.release()
   cv2.destroyAllWindows()

print("YOU ARE A CLIENT!")
HOST2 = input("Enter HOST IP:\n")        # check ipconfig for an available local iPV4 address
HOST = input("Enter Your Available IPV4 Address:\n")        # check ipconfig for an available local iPV4 address
PORT = int(input("Enter Desired PORT:\n"))  #input 0000 - 9999 as port

# Create two threads as follows
#try:
#   threading.start_new_thread(server, (HOST, PORT, ) )
#   threading.start_new_thread( client, (HOST2, PORT2, ) )

#except:
#   print ("Error: unable to start thread")

#MULTITHREADING PART (CLIENT THEN SERVER)
t2 = Thread(target=client, args=(HOST,PORT))
t2.start()
t = Thread(target=server, args=(HOST,PORT))
t.start()
