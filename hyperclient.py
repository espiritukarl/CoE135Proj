# HYPERCLIENT 2.50
# PURE CLIENT. NO SERVER INCLUDED.
# MULTIPLE CLIENTS CAN CONNECT TO 1 SERVER (WITH LIMIT)
# [NEW!] NOT TESTABLE ON 1 COMPUTER
# SERVER VIDEO ONLY, AUDIO, CHAT

from threading import Thread
import cv2
import socket
import struct
import pickle
import tkinter
import pyaudio

def client1(HOST, PORT): #sends the data to server
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("CLIENT1: Starting...")
    except OSError:
        pass
    #connection = client_socket.makefile('wb')

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
        try:
            client_socket.sendall(struct.pack(">L", size) + data)
            img_counter += 1
        except OSError:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
            break

    cam.release()
    cv2.destroyAllWindows()
    client_socket.close()

# Define a function for the thread
def client2(HOST2, PORT2):   #receives data from server
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST2, PORT2))
        print("CLIENT2: Starting...")
    except OSError:
        pass
    #connection = client_socket.makefile('wb')

    data = b""
    payload_size = struct.calcsize(">L")
    #print("payload_size: {}".format(payload_size))
    while True:
        while len(data) < payload_size:
            #print("Recv: {}".format(len(data)))
            try:
                data += client_socket.recv(4096)
            except OSError:
                break

        #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        try:
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow('Server Camera',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
                send()
                break

        except:
            pass
        #print("msg_size: {}".format(msg_size))

    client_socket.close()

#for chatroom:
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
    try:
        msg = my_msg.get()
        my_msg.set("")  # Clears input field.
        client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
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

#for audio
def SendAudio():
    while True:
        try:
            data = stream.read(CHUNK)
            clientaudio_socket.sendall(data)
        except OSError:
            break

def ReceiveAudio():
    while True:
        try:
            data = recvall(BUFSIZ2)
            stream.write(data)
        except OSError:
            break

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
            continue
    return databytes
#end of audio
    
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
#end of tkinter


print("YOU ARE A CLIENT!")
#HOST = input("Enter HOST IP:\n")        # check ipconfig for an available local iPV4 address

HOST = "192.168.100.6"

VPORT  = 1001
VPORT2 = 2001
APORT  = 3001
CPORT  = 4001

BUFSIZ = 1024 #for chat
BUFSIZ2 = 4096 #for audio
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

ADDR = (HOST, CPORT) #tupple for server chatroom
ADDR1 = (HOST, APORT) #tupple for server audio

Thread(target=client1, args=(HOST,VPORT )).start()
Thread(target=client2, args=(HOST,VPORT2)).start()


if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clientaudio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientaudio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        client_socket.connect(ADDR)
        clientaudio_socket.connect(ADDR1)
        audio=pyaudio.PyAudio()
        stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

        Thread(target=ReceiveAudio).start()
        Thread(target=SendAudio).start()

        receive_thread = Thread(target=receive)
        receive_thread.start()
    
        tkinter.mainloop()
        
    except OSError:
        print("SERVER IS CLOSED. CLIENT FAILED TO START.")