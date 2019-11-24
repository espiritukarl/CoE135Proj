# SUPERCLIENT 1.00
# PURE CLIENT. NO SERVER INCLUDED.
# AUDIO NOT YET INCLUDED
# SEPARATED INTO WEEK3 
# added Chatroom

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
# for chat:
def receive():
    # Handles receiving of messages
    while True:
        try:
            msg = chat_client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break
            
def send(event=None):  # event is for tkinter
    # handles sending of messages
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    chat_client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        chat_client_socket.close()
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
print("YOU ARE A CLIENT!")
#HOST = input("Enter HOST IP:\n")        # check ipconfig for an available local iPV4 address

HOST = "192.168.100.6"

PORT = 9898
PORT2 = 8787
PORTAS = 4545
PORTAC = 4848

BUFFSIZ = 1024

# for chat room
chat_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat_client_socket.connect(HOST,PORT)

#MULTITHREADING PART

t = Thread(target=client1, args=(HOST,PORT))
#t.daemon = True
t.start()

t2 = Thread(target=client2, args=(HOST,PORT2))
#t2.daemon = True
t2.start()

chat_thread = Thread(target=receive)
chat_thread.start()
tkinter.mainloop()
