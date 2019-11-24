# Version 1.00 
# to fix: tkinter not closing sockets properly, server not multithreaded to be a client as well
from socket import AF_INET, socket, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

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
    welcome = 'Welcome to the chatroom %s!' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    
    while True:
        msg = client.recv(BUFSIZ)
        if msg:
            print(name + ":" + msg.decode("utf8"))
            broadcast(msg)
        else:
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            clients.remove(client)
            client.close()
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    # show message to clients
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
