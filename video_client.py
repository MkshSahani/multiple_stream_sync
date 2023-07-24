import socket, argparse, pickle, struct, cv2, base64, numpy as np
BUFF_SIZE = 65536
ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--ip-address", required=True, help="Enter Target Address", type = str)
ap.add_argument("-p", "--port", required=True, help="Enter Port Number", type = int)

args = vars(ap.parse_args())
host_ip = args['ip_address']
host_port = args['port']
server_addr = (host_ip, host_port)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
# client_socket.connect(server_addr)

data = b""
metadata_size = struct.calcsize("Q")

client_socket.sendto("SYN".encode(), server_addr)
while True: 
    while len(data) < metadata_size: 
        # data += client_socket.recv(4 * 1024)
        packet, server_socket = client_socket.recvfrom(BUFF_SIZE)
        if not packet: 
            continue 
        data += packet 
    print(data)
    packet_size = data[:metadata_size]
    data = data[metadata_size : ]
    packet_size = struct.unpack("Q", packet_size)[0]
    print(f"len : {packet_size}")
    while len(data) < packet_size: 
        packet = client_socket.recv(4 * 1024)
        if not packet: 
            break
        data += packet 
    frame = data[:packet_size]
    data = data[packet_size:]
    print(data)
    print(frame)
    frame_data = base64.b64decode(frame)
    frame_data = np.frombuffer(frame_data, dtype = np.uint8)
    frame = cv2.imdecode(frame_data, 1)
    cv2.imshow("Frame Show", frame)

    if cv2.waitKey(1) == 13: 
        break 

client_socket.close()