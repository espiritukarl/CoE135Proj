# Version 1.20
# Final. Just need to integrate to Video-Audio stream.
from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
import tkinter

def accept_connections():
    # accepts incoming clients
    while True:
        client, addr = SERVER.accept()
        print("%s:%s has connected." % addr)
        client.send(bytes("Type your name and press 'Enter'!", "utf8"))
        addresses[client] = addr
        Thread(target=handler, args=(client,)).start()
    
def handler(client):
    # handles the clients
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome to the chatroom %s! Type {quit} if you want to exit.' % name
    if not name:
        client.close()
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
clients = {}
addresses = {}

HOST = ''
HOST2 = '127.0.0.1'
PORT = 33000

BUFSIZ = 1024
ADDR = (HOST, PORT)
ADDR2 = (HOST2, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDR)


if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client_socket.connect(ADDR2)
    
    receive_thread = Thread(target=receive)
    receive_thread.start()
    
    tkinter.mainloop()
    
    ACCEPT_THREAD.join()
    SERVER.close()
