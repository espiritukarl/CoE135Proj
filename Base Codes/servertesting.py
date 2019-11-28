# Version 1.10 testing audio w/ chatroom
# things to fix: disconnect audio in sync w/ chatroom, add video! timeouts on other machines for some odd reason

from threading import Thread
from array import array
import socket
import pyaudio
import tkinter

# for chatroom & audio:
def accept_connections():
    # accepts incoming clients
    while True:
        client, addr = SERVER.accept()
        client2, addr2 = ASERVER.accept()
        print("%s:%s has connected." % addr)
        client.send(bytes("Type your name and press 'Enter'!", "utf8"))
        addresses[client] = addr
        addresses2[client2] = addr2
        Thread(target=handler, args=(client,)).start()
        Thread(target=ClientConnectionSound, args=(client2, )).start()

#for chatroom:
def handler(client):
    # handles the clients
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome to the chatroom %s! Type {quit} if you want to exit.' % name
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
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is for tkinter
    # handles sending of messages
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.destroy()

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
        data = stream.read(CHUNK)
        clientaudio_socket.sendall(data)

def RecieveAudio():
    while True:
        data = recvall(BUFSIZ2)
        stream.write(data)

def recvall(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += clientaudio_socket.recv(4 * CHUNK)
        else:
            databytes += clientaudio_socket.recv(to_read)
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

# sockets
clients = {} #for chat
addresses = {} #for chat
addresses2 = {} #for audio

HOST = input("Enter Host IP\n") #for server
PORT = 33000
PORT2 = 9898

BUFSIZ = 1024 #for chat
BUFSIZ2 = 4096 #for audio
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

ADDR = (HOST, PORT) #tupple for server chatroom
ADDR1 = (HOST, PORT2) #tupple for server audio

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #chatroom
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

ASERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #audio
ASERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ASERVER.bind(ADDR1)

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

    RecieveAudioThread = Thread(target=RecieveAudio).start()
    SendAudioThread = Thread(target=SendAudio).start()

    receive_thread = Thread(target=receive)
    receive_thread.start()
    
    tkinter.mainloop()
    
    ACCEPT_THREAD.join()
    SERVER.close()
