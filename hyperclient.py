# HYPERCLIENT 1.00
# PURE CLIENT. NO SERVER INCLUDED.
# MULTIPLE CLIENTS CAN CONNECT TO 1 SERVER
# VIDEO RECEIVING ONLY

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
            cv2.imshow('Host Camera',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
                send()
                break

        except:
            pass
        #print("msg_size: {}".format(msg_size))

    client_socket.close()

print("YOU ARE A CLIENT!")
#HOST = input("Enter HOST IP:\n")        # check ipconfig for an available local iPV4 address

HOST = "192.168.100.6"

PORT  = 1001
PORT2 = 2001
PORT3 = 3001
PORT4 = 4001
PORT5 = 5001 #for chat
PORT6 = 6001 #for audio

Thread(target=client2, args=(HOST,PORT )).start()
