import socket, argparse 
import pickle, struct
import cv2, imutils, base64

ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--ip-address", required=True, help="Enter Target Address", type = str)
ap.add_argument("-p", "--port", required=True, help="Enter Port Number", type = int)

args = vars(ap.parse_args())
print(" * " * 10)
print(args)
print(" * " * 10)

host_ip = args['ip_address']
host_port = args['port']
server_addr = (host_ip, host_port)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_addr)
server_socket.listen(1)


client_socket, addr = server_socket.accept()
vid = cv2.VideoCapture(0)
while True: 
    ret, frame = vid.read()
    if not ret: 
        continue
    frame = imutils.resize(frame)
    encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
    message = base64.b64encode(buffer)
    # print(message)
    print("=== len ===")
    print(len(message))
    print("=== len ===")
    message = struct.pack("Q", len(message)) + message 
    client_socket.sendall(message)
    print("------------------------------")
    # cv2.imshow("Sending Frame", frame)
    key = cv2.waitKey(1)
    if key == 13: 
        break 
client_socket.close()
server_socket.close()






