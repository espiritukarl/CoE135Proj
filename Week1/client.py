# CLIENT 1.00
# one-way low latency sending
# can be opened with server simultaneously for 2-way connection
# no audio yet

import cv2
import io
import socket
import struct
import time
import pickle
#import zlib #for compression

HOST = input("Enter Host IP:\n")        #check ipconfig for an available local iPV4 address
PORT = int(input("Enter Desired PORT:\n"))  #any port from 0000-9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
connection = client_socket.makefile('wb')

camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)

camera.set(3, 640) #size1
camera.set(4, 480) #size2

img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

print("Starting Camera Application")
while True:
    ret, frame = camera.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    #data = zlib.compress(pickle.dumps(frame, 0))
    data = pickle.dumps(frame, 0)
    size = len(data)

    #for debugging
    #print("Time{}: Size{}".format(img_counter, size))
    #client_socket.sendall(struct.pack(">L", size) + data)
    #img_counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):       #press q on camera window to exit
        break

camera.release()
cv2.destroyAllWindows()