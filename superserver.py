# SUPERSERVER 1.52
# PURE SERVER. NO CLIENT INCLUDED.
# VIDEO, AUDIO AND CHAT IS SYNC'D
# DISCONNECTION HANDLING FOR AUDIO&CHATROOM

from threading import Thread
import cv2
import socket
import struct
import pickle
import pyaudio
import tkinter


def server1(HOST, PORT):    #receives data from client1
   print('SERVER1: Starting... (Preparing Sockets for Receiving VData)')
   s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   s.bind((HOST,PORT))
   s.listen(10)
   #print('SERVER1: Sockets prepared and ready.')

   conn,addr=s.accept()

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
        
        if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
            break
        
    cam2.release()
    s2.close()

# for chatroom & audio:
def accept_connections():
    # accepts incoming clients
    while True:
        try:
            client, addr = SERVER.accept()
            client2, addr2 = ASERVER.accept()
            print("%s:%s has connected." % addr)
            client.send(bytes("Type your name and press 'Enter'!", "utf8"))
            addresses[client] = addr
            addresses2[client2] = addr2
            Thread(target=handler, args=(client,)).start()
            Thread(target=ClientConnectionSound, args=(client2, )).start()
        except OSError:
            continue

#for chatroom:
def handler(client):
    # handles the clients
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome to the chatroom %s! Type {quit} if you want to exit.' % name
    try:
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        broadcast(bytes(msg, "utf8"))
        clients[client] = name
        
        while True:
            msg = client.recv(BUFSIZ)
            if msg.decode("utf8") != "{quit}":
                print(name + ": " + msg.decode("utf8"))
                broadcast(msg, name+": ")
            else:
                print(name + " has disconnected.")
                del clients[client]
                broadcast(bytes("%s has left the chat." % name, "utf8"))
                break
    except:
        pass

def broadcast(msg, prefix=""):  # prefix is for name identification.
    # show message to clients
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

def receive():
    # Handles receiving of messages
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except:  # Possibly client has left the chat.
            break

def send(event=None):  # event is for tkinter
    # handles sending of messages
    try:
        msg = my_msg.get()
        my_msg.set("")  # Clears input field.
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            SERVER.close()
            ASERVER.close()
            client_socket.close()
            clientaudio_socket.close()
            top.destroy()
            
            print("SERVER HAS CLOSED")
            raise SystemExit
    except OSError:
        pass

def on_closing(event=None):
    # for closing of window
    my_msg.set("{quit}")
    send()
#end of chatroom

#for audio:
def ClientConnectionSound(client):
    while True:
        try:
            data = client.recv(BUFSIZ2)
            broadcastSound(client, data)
        except:
            continue

def broadcastSound(clientSocket, data_to_be_sent):
    for client in addresses2:
        if client != clientSocket:
            client.sendall(data_to_be_sent)

def SendAudio():
    while True:
        try:
            data = stream.read(CHUNK)
            clientaudio_socket.sendall(data)
        except OSError:
            continue

def ReceiveAudio():
    while True:
        try:
            data = recvall(BUFSIZ2)
            stream.write(data)
        except OSError:
            continue

def recvall(size):
    databytes = b''
    while len(databytes) != size:
        try:
            to_read = size - len(databytes)
            if to_read > (4 * CHUNK):
                databytes += clientaudio_socket.recv(4 * CHUNK)
            else:
                databytes += clientaudio_socket.recv(to_read)
        except OSError:
            break
    return databytes
#end of audio

#tkinter for chatroom
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
#end of tkinter

#sockets:
print("YOU ARE THE MAIN HOST!")
#HOST = input("Enter Your Server IP:\n")        # check ipconfig for an available local iPV4 address
#HOST2 = input("Enter Client IP ADDRESS:\n")        # check ipconfig for an available local iPV4 address


clients = {} #for chat
addresses = {} #for chat
addresses2 = {} #for audio

HOST = "192.168.100.6"
PORT  = 1001
PORT2 = 2001
PORT3 = 3001
PORT4 = 4001
PORT5 = 5001
PORT6 = 6001

BUFSIZ = 1024 #for chat
BUFSIZ2 = 4096 #for audio
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

ADDR = (HOST, PORT5) #tupple for server chatroom
ADDR1 = (HOST, PORT6) #tupple for server audio

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #chatroom
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

ASERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #audio
ASERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ASERVER.bind(ADDR1)


#MULTITHREADING PART
t = Thread(target=server1, args=(HOST,PORT ))
t.start()
t2 = Thread(target=server2, args=(HOST,PORT2))
t2.start()

if __name__ == "__main__":
    SERVER.listen(5)
    ASERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect(ADDR)
    
    clientaudio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientaudio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clientaudio_socket.connect(ADDR1)

    audio=pyaudio.PyAudio()
    stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

    Thread(target=ReceiveAudio).start()
    Thread(target=SendAudio).start()

    receive_thread = Thread(target=receive)
    receive_thread.start()
    
    tkinter.mainloop()
    
    ACCEPT_THREAD.join()
    SERVER.close()
