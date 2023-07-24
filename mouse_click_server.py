from pynput.mouse import Controller 
import argparse, base64
import socket, time, struct

ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--ip-address", required=True, type = str)
ap.add_argument("-port", "--port", required=True, type = int)

args = vars(ap.parse_args())
print(args)
address = (args['ip_address'], args['port'])
mouse_controler = Controller()
mouse_server_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mouse_server_server.bind(address)
data = []
msg, client_socket = mouse_server_server.recvfrom(1024)
print(f"[*] Msg recieved : {msg.decode()}")
prev_current_time = time.time()
seq_number = 0
while True: 
    pos = mouse_controler.position 
    data.append(pos)
    current_time = time.time()
    if current_time - prev_current_time >= 0.001:
        seq_number += 1
        str_data = str(data).encode()
        str_data_encode = base64.b64encode(str_data)
        message_packet = struct.pack("Q", len(str_data_encode)) + struct.pack("Q", seq_number) + \
        struct.pack("d", prev_current_time) + str_data_encode         
        mouse_server_server.sendto(message_packet, client_socket)
        prev_current_time = time.time()
        data = []
