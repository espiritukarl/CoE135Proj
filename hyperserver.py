# HYPERSERVER 1.00
# PURE SERVER. NO CLIENT INCLUDED.
# ONE SERVER, MULTIPLE CLIENTS (WITH LIMIT)
# TESTABLE ON 1 COMPUTER (FOR THE MEANTIME)
# VIDEO SENDING ONLY YET

from threading import Thread
import cv2
import socket
import struct
import pickle
import pyaudio
import tkinter


def server1(conn1, addr1):    #receives data from client1
   data = b""
   payload_size = struct.calcsize(">L")
   print("SERVER1: Connected! Launching Camera Window...")

   while True:
      while len(data) < payload_size:
        #print("Recv: {}".format(len(data)))
        data += conn.recv(4096)
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
      #string = ("Friend#{} Camera",NUM)
      cv2.imshow("Friend Camera",frame)

      if cv2.waitKey(1) & 0xFF == ord('q'):   #press q on window to stop
         send()
         break

def server2(conn2,addr2):    #sends data to client2
    print("SERVER2: Starting... (Preparing Sockets for Sending VData)")
    #s2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #s2.bind((HOST2,PORT2))
    #s2.listen(10)
    #print('Socket now listening')

    #conn2,addr2=s2.accept()

    cam2 = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    cam2.set(3, 640)
    cam2.set(4, 480)
    print("SERVER2: Sending VData to Client {}...", addr)
    img_counter2 = 0
    encode_param2 = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    while True:
        ret2, frame2 = cam2.read()
        cv2.imshow('SELF_CAMERA',frame2)
        result, frame2 = cv2.imencode('.jpg', frame2, encode_param2)
        data2 = pickle.dumps(frame2, 0)
        size2 = len(data2)
        #print("{}: {}".format(img_counter2, size2))
        conn2.sendall(struct.pack(">L", size2) + data2)
        img_counter2 += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
            break
        
    cam2.release()
    s2.close()


print("YOU ARE THE MAIN HOST!")
#HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address
#HOST2 = input("Enter Client IP ADDRESS:\n")        # check ipconfig for an available local iPV4 address

HOST = "192.168.100.6"
PORT  = 1001
PORT2 = 2001
PORT3 = 3001
PORT4 = 4001
PORT5 = 5001
PORT6 = 6001

#MULTITHREADING PART
#t = Thread(target=server1, args=(HOST,PORT ))
#t.start()

count = 0
limit = 3   #can be set later
print('HYPER SERVER STARTING...')

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(10)

while True:
    # checker to block another transmission
    if count == limit:
        print("[LIMIT REACHED!]: No more participants will be accepted.")
        break

    conn, addr = s.accept()     # blocking function
    print ('CLIENT {}: CONNECTED SUCCESSFULLY!', addr)
    Thread(target=server2, args=(conn,addr)).start()
    count += 1
s.close()