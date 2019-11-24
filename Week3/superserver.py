# SUPERSERVER 1.30
# PURE SERVER. NO CLIENT INCLUDED.
# AUDIO INCLUDED - ONE-WAY ONLY
# SEPARATED INTO WEEK3 
# Added Chatbox! (See Terminal)

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
import tkinter


# Define a function for the thread
def server1(HOST, PORT):    #receives data from client1
   print('SERVER1: Preparing sockets for connection...')
   s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   s.bind((HOST,PORT))
   s.listen(10)
   print('SERVER1: Sockets prepared and ready.')

   conn,addr=s.accept()

   data = b""
   payload_size = struct.calcsize(">L")
   print("SERVER1: Starting Camera...")

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
         break

def server2(HOST2, PORT2):    #sends data to client2
    print("SERVER2: Starting...")
    s2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s2.bind((HOST2,PORT2))
    s2.listen(10)
    #print('Socket now listening')

    conn2,addr2=s2.accept()

    cam2 = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    cam2.set(3, 640)
    cam2.set(4, 480)

    img_counter2 = 0
    encode_param2 = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    while True:
        ret2, frame2 = cam2.read()
        result, frame2 = cv2.imencode('.jpg', frame2, encode_param2)
        data2 = pickle.dumps(frame2, 0)
        size2 = len(data2)
        #print("{}: {}".format(img_counter2, size2))
        conn2.sendall(struct.pack(">L", size2) + data2)
        img_counter2 += 1
    cam2.release()

def server3(HOST3,PORT3): #sends audio to client
  print("SERVER3 (S/AUDIO): Waiting for client...")
  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 44100
  CHUNK = 4096
  audio = pyaudio.PyAudio()

  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  serversocket.bind((HOST3, PORT3))
  serversocket.listen(10)

  def callback(in_data, frame_count, time_info, status):
    for s in read_list[1:]:
        s.send(in_data)
    return (None, pyaudio.paContinue)

  # start Recording
  stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
  # stream.start_stream()

  read_list = [serversocket]
  print ("SERVER3: Recording...")

  try:
    while True:
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is serversocket:
                (clientsocket, address) = serversocket.accept()
                read_list.append(clientsocket)
                print ("Connection from", address)
            else:
                data = s.recv(1024)
                if not data:
                    read_list.remove(s)
  except KeyboardInterrupt:
    pass

  print ("Finished recording")
  serversocket.close()
  # stop Recording
  stream.stop_stream()
  stream.close()
  audio.terminate()

def server4(HOST4,PORT4): #plays the client's audio
  print("SERVER4 (R/AUDIO): Waiting for client...")
  p2 = pyaudio.PyAudio()
  CHUNK2 = 1024 * 4
  FORMAT2 = pyaudio.paInt16
  CHANNELS2 = 2
  RATE2 = 44100
  stream2 = p2.open(format=FORMAT2,
                channels=CHANNELS2,
                rate=RATE2,
                output=True,
                frames_per_buffer=CHUNK2)

  with socket.socket() as server_socket2:
    server_socket2.bind((HOST4, PORT4))
    server_socket2.listen(1)
    conn2, address2 = server_socket2.accept()
    print("Connection from " + address2[0] + ":" + str(address2[1]))

    data2 = conn2.recv(4096)
    while data2 != "":
        data2 = conn2.recv(4096)
        stream2.write(data2)

  stream2.stop_stream()
  stream2.close()
  p2.terminate()

def chat_accept_connections():
    # accepts incoming clients
    while True:
        client, addr = CHATSERVER.accept()
        print("%s:%s has connected." % addr)
        client.send(bytes("Type your name and press 'Enter'!", "utf8"))
        addresses[client] = addr
        Thread(target=chat_handler, args=(client,)).start()

def chat_handler(client):
    # handles the clients
    name = client.recv(BUFFSIZ).decode("utf8")
    welcome = 'Welcome to the chatroom %s! Type {quit} if you want to exit.' % name
    if not name:
        client.close()
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    
    while True:
        msg = client.recv(BUFFSIZ)
        if msg.decode("utf8") != "{quit}":
            print(name + ": " + msg.decode("utf8"))
            broadcast(msg, name+": ")
        else:
            #client.send(bytes("{quit}", "utf8"))
            #client.close()
            print(name + " has disconnected.")
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break
            
def broadcast(msg, prefix=""):  # prefix is for name identification.
    # show message to clients
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)
            
def receive():
    # Handles receiving of messages
    while True:
        try:
            msg = CHATCLIENT.recv(BUFFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except OSError:
            break
            
def send(event=None):  # event is for tkinter
    # handles sending of messages
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    CHATCLIENT.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        CHATCLIENT.close()
        top.destroy()
        
def on_closing(event=None):
    # for closing of window
    my_msg.set("{quit}")
    send()
      
#tkinter GUI shit
top = tkinter.Tk()
top.title("Chatbox")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=35, width=75, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#sockets:
print("YOU ARE THE MAIN HOST!")
#HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address
#HOST2 = input("Enter Client IP ADDRESS:\n")        # check ipconfig for an available local iPV4 address

HOST = "192.168.100.6"
addresses = {}
clients = {}
PORT  = 1001
PORT2 = 2001
PORT3 = 3001
PORT4 = 4001

BUFFSIZ = 1024

# for chat
CHATSERVER=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CHATSERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
CHATSERVER.bind((HOST,PORT))
CHATSERVER.listen(5)

#MULTITHREADING PART
t = Thread(target=server1, args=(HOST,PORT ))
t.start()
t2 = Thread(target=server2, args=(HOST,PORT2))
t2.start()
t3 = Thread(target=server3, args=(HOST,PORT3))
t3.start()
t4 = Thread(target=server4, args=(HOST,PORT4))
#t4.start()

if __name__ == "__main__":
    # chat room server
    chat_server_thread = Thread(target=chat_accept_connections)
    chat_server_thread.start()
      
    # chat room client
    CHATCLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CHATCLIENT.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    CHATCLIENT.connect((HOST,PORT))
    chat_client_thread = Thread(target=receive)
    chat_client_thread.start()
      
    tkinter.mainloop()
   
    chat_server_thread.join()
    CHATSERVER.close()
