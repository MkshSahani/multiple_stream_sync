import socket, argparse 
import pickle, struct
import cv2, imutils, base64

ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--ip-address", required=True, help="Enter Target Address", type = str)
ap.add_argument("-p", "--port", required=True, help="Enter Port Number", type = int)

args = vars(ap.parse_args())
BUFF_SIZE = 65536 

host_ip = args['ip_address']
host_port = args['port']
server_addr = (host_ip, host_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
server_socket.bind(server_addr)

# client_socket, addr = server_socket.accept()
msg, client_socket = server_socket.recvfrom(BUFF_SIZE)
vid = cv2.VideoCapture(0)
while True: 
    ret, frame = vid.read()
    if not ret: 
        continue
    frame = imutils.resize(frame)
    encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
    message = base64.b64encode(buffer)
    message = struct.pack("Q", len(message)) + message 
    server_socket.sendto(message, client_socket)
    cv2.imshow("Recored Frame", frame)
    key = cv2.waitKey(1)
    if key == 13: 
        break 
server_socket.close()






