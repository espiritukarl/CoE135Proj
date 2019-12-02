#main host's video cannot be broadcasted yet  first connection will be the only one to receive
#disconnection not present yet
#test broadcast
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

def server1(client, clients):    #receives data from client1
   print('SERVER1: Starting... (Preparing Sockets for Receiving VData)')
   
   #print('SERVER1: Sockets prepared and ready.')
   #if len(addresses) > 1 thus there are other clients send data to them

   #if i < 3 can still accept connections
   #conn,addr=s.accept()
                                                            
   data = b""
   payload_size = struct.calcsize(">L")
   print("SERVER1: Connected! Launching Camera Window...")

   while True:
      while len(data) < payload_size:
        #print("Recv: {}".format(len(data)))
        data += clients[0].recv(4096)
      #print("Receiving: {}".format(len(data)))
      packed_msg_size = data[:payload_size]
      data = data[payload_size:]
      msg_size = struct.unpack(">L", packed_msg_size)[0]
      #print("SERVER: Packet Size: {}".format(msg_size))
      while len(data) < msg_size:
        data += clients[0].recv(4096)
      frame_data = data[:msg_size]
      data = data[msg_size:]

      frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
      frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
      #string = ("Friend#{} Camera",NUM)
      cv2.imshow("Friend Camera",frame)
      
      broadcastVideo(clients[0],data,clients) #unsure if dictionary is passable
      
      #interrupt sana if meron
      #if i < 3:
       #  new,addr = s.accept()
        # client[new] = addr
         #i = i + 1
        
         
      if cv2.waitKey(1) & 0xFF == ord('q'):   #press q on window to stop
        break


def broadcastVideo(clientSocket, data_to_be_sent,client):
    for conn in client:
        if conn != clientSocket:
            client.sendall(data_to_be_sent)


def server2(HOST2, PORT2):    #sends data to client2
    print("SERVER2: Starting... (Preparing Sockets for Sending VData)")
    s2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s2.bind((HOST2,PORT2))
    s2.listen(10)
    #print('Socket now listening')

    conn2,addr2=s2.accept()

    cam2 = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    cam2.set(3, 640)
    cam2.set(4, 480)
    print("SERVER2: Sending VData to Client...")
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
    cam2.release()

def accept( server1,server2,server3):
    client1,addr1 = server1.accept()
    client2,addr2 = server2.accept()
    client3,addr3 = server3.accept()
    
    clients = [client1, client2, client3]

    return tuple(clients)

def ConnectionsUniv(HOSTU,PORTU):
    while True:
        serverUniv=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        serverUniv.bind((HOSTU,PORTU))
        serverUniv.listen(10)
        client, addr = serverUniv.accept() #a connection is present
        addresses[client] = addr
        #quitUsers[addr[0]] = False
        print("{} is connected!!".format(addr))
        for port in sorted(ports.keys()):
            if ports[port] == False:  #find an open port if False = unused then send it to requesting client 
                client.sendall(port.encode())
                ports[port] = True
                #since port is occupied setup a server for receiving end
                #1 sender per port thus send the assigned socket to a thread a start that thread  
                if port == '5001':
                    clients = accept(s1,s2,s3) #setup clients and main port for sendin
                    Thread(target=server1, args=(client, clients)).start() 
                    #begin own thread wherein Clients[0] is the sender of data and all other parts of the array are receivers  
                if port == '6001': 
                    clients = accept(s2,s1,s3)
                    Thread(target=server1, args=(client, clients)).start() 
                if port == '7001':
                    clients = accept(s3,s2,s1)
                    Thread(target=server1, args=(client, clients)).start() 
                break


print("YOU ARE THE MAIN HOST!")
#HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address
#HOST = socket.gethostname()
#print('Your Socket Host Name:',HOST)
HOST = "169.254.251.99"
ports = {'5001':False,'6001':False,'7001':False}
addresses = {}
clients = []
clients1 = []
clients2 = []
clients3 = []
PORTU = 9999
PORT  = 1001
PORT2 = 2001
PORT3 = 3001
PORT4 = 4001
#setup 3 connection
s1=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.bind((HOST,PORT2))
s1.listen(10)

s2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s2.bind((HOST,PORT3))
s2.listen(10)

s3=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s3.bind((HOST,PORT4))
s3.listen(10)

#MULTITHREADING PART
#start all receiving ports
Univ  = Thread(target=ConnectionsUniv, args=(HOST,PORTU ))
Univ.start()
t4 = Thread(target=server2, args=(HOST,PORT))
t4.start() #main

#t  = Thread(target=server1, args=(HOST,5001))
#t.start()
#t2 =Thread(target=server1, args=(HOST, 6001))
#t2.start()
#t3 =Thread(target=server1, args=(HOST, 7001))
#t3.start()