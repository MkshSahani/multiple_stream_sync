import cv2, imutils, socket 
import numpy as np 
import time 
import base64 

BUFF_SIZE = 65536 
server_socket = socket.socket(
    socket.AF_INET, 
    socket.SOCK_DGRAM
)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host = "localhost"
port = 9999 
server_socket.bind((host, port))
vid = cv2.VideoCapture(0)
fps, st, frame_to_count, cnt = (0, time.time(), 20, 0)

while True: 
    msg, client_address = server_socket.recvfrom(BUFF_SIZE)
    print(f"Connected.... {client_address}")
    while True:
        print("#" * 20)
        _, frame = vid.read()
        frame = imutils.resize(frame, width=600)
        encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
        message = base64.b64encode(buffer)
        print(message)
        i = 0 
        while i * BUFF_SIZE < len(message):
            msg = message[(i - 1) * BUFF_SIZE : i * BUFF_SIZE]
            server_socket.sendto(msg, client_address)
            print("===== Message ======")
            i += 1
        print("Frame Sent...")

        if cnt == frame_to_count:
            try: 
                fps =  round(frame_to_count / time.time() - st)
                st = time.time()
                cnt = 0
            except: 
                pass 
        cnt += 1

