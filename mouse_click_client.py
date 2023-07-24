from pynput.mouse import Controller 
import argparse, socket, base64, struct 
mouse_controller = Controller()

BUFF_SIZE = 65536
ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--ip-address", required=True, type = str)
ap.add_argument("-p", "--port", required = True, type = int)
args = vars(ap.parse_args())
print(args)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
server_address = (args['ip_address'], args['port'])

client_socket.sendto("SYN".encode(), server_address)
data = b""
metdata_size = struct.calcsize("Q")
while True:
    while len(data) < 3 * metdata_size: 
        packet, server_socket = client_socket.recvfrom(BUFF_SIZE)
        if not packet: 
            continue 
        data += packet 
    packet_size = data[:metdata_size]
    sequence_number = data[metdata_size : 2 * metdata_size]
    timestamp = data[2 * metdata_size : 3 * metdata_size]
    packet_size = struct.unpack("Q", packet_size)[0]
    timestamp = struct.unpack("d", timestamp)[0]
    sequence_number = struct.unpack("Q", sequence_number)[0]
    print("[*]")
    data = data[3 * metdata_size : ]
    while len(data) < packet_size: 
        packet, server_packet = client_socket.recvfrom(BUFF_SIZE)
        if not packet: 
            continue 
        data += packet
    packet_data = data[:packet_size]
    data = data[packet_size: ]
    mouse_control_stream = base64.b64decode(packet_data)
    print(f"Packet Size : {packet_size}")
    print(f"Sequence Number : {sequence_number}")
    print(f"timestamp : {timestamp}")
    print(mouse_control_stream.decode())


    