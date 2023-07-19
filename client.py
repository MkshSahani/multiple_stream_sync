import cv2, imutils, socket 
import numpy as np 
import time, base64 
import matplotlib.pyplot as plt

BUFF_SIZE = 65536 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host = "localhost"
port = 9999
socket_address = (host, port)
msg = b'Hello'

client_socket.sendto(msg, socket_address)
fps, st, frame_to_count, cnt = (0, time.time(), 20, 0)
cv2.destroyAllWindows()
# cv2.namedWindow("frame")

while True:
    packet, _ = client_socket.recvfrom(BUFF_SIZE)
    print(packet)
    data = base64.b64decode(packet)
    npdata = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(npdata, 1)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == 13: 
        client_socket.close()
        break
    if cnt == frame_to_count:
        try: 
            fps = round(frame_to_count / (time.time() - st))
            st = time.time()
            cnt = 0
        except: 
            pass 
    cnt += 1 