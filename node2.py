import socket, cv2, base64, argparse, struct
import threading, numpy as np, pyshine as ps
from pynput.mouse import Controller
BUFF_SIZE = 65536
ap = argparse.ArgumentParser()
ap.add_argument("-ip", "-ip-address", required=True, type = str) # ip address of server. 
ap.add_argument("-tvp", "--target-video-port", required=True, type = int) # video port number
ap.add_argument("-tap", "--target-audio-port", required=True, type = int) # audio port number. 
ap.add_argument("-tmp", "--target-mouse-port", required=True, type = int) # mouse control stream port number.
args = vars(ap.parse_args())
print(args)
ip_address = args['ip']
target_video_stream_port = args['target_video_port']
target_audio_stream_port = args['target_audio_port']
target_mouse_stream_port = args['target_mouse_port']
BUFF_SIZE = 65536

target_video_stream = (ip_address, target_video_stream_port)
target_audio_stream = (ip_address, target_audio_stream_port)
target_mouse_stream = (ip_address, target_audio_stream_port)

## video stream socket 
vedio_stream_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vedio_stream_recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

## audio stream socket 
audio_stream_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
audio_stream_recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

audio_driver,context = ps.audioCapture(mode='get')

## mouse contrl stream socket. 
mouse_control_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mouse_control_client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
mouse_controller = Controller()

def recv_video_stream():
    metadata_size = struct.calcsize("Q")
    vedio_stream_recv_socket.sendto("SYN".encode(), target_video_stream)
    data = b"" 
    while True: 
        while len(data) < metadata_size: 
            packet, server_socket = vedio_stream_recv_socket.recvfrom(BUFF_SIZE)
            if not packet: 
                continue 
            data += packet 
        packet_size = data[:metadata_size]
        data = data[metadata_size:]
        packet_size = struct.unpack("Q", packet_size)[0]
        while len(data) < packet_size:
            packet, server_socket = vedio_stream_recv_socket.recvfrom(BUFF_SIZE)
            if not packet:
                continue
            data += packet 
        frame = data[:packet_size]
        data = data[packet_size:]
        frame_data = base64.b64decode(frame)
        frame_data = np.frombuffer(frame_data, dtype = np.uint8)
        frame_data = cv2.imdecode(frame_data, 1)
        cv2.imshow("RECV Frame", frame_data)
        if cv2.waitKey(1) == 13: 
            break 
    vedio_stream_recv_socket.close() 


def recv_audio_stream():
    audio_stream_recv_socket.sendto("SYN".encode(), target_audio_stream)
    data = b""
    metdata_size = struct.calcsize("Q")
    while True:
        while len(data) < metdata_size: 
            packet, server_socket = audio_stream_recv_socket.recvfrom(BUFF_SIZE)
            if not packet:
                continue 
            data += packet 
        packet_size = data[:metdata_size]
        packet_size = struct.unpack("Q", packet_size)[0]
        data = data[packet_size:]
        while len(data) < packet_size: 
            packet, server_socket = audio_stream_recv_socket.recvfrom(BUFF_SIZE)
            if not packet: 
                continue 
            data += packet 
        audio_frame = data[:packet_size]
        data = data[packet_size:]
        audio_frame = np.frombuffer(audio_frame)
        audio_driver.put(audio_frame)


def recv_mouse_control_stream():

    mouse_control_client.sendto("SYN".encode(), target_mouse_stream)
    data = b""
    metdata_size = struct.calcsize("Q")
    while True:
        while len(data) < 3 * metdata_size: 
            packet, server_socket = mouse_control_client.recvfrom(BUFF_SIZE)
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
            packet, server_packet = mouse_control_client.recvfrom(BUFF_SIZE)
            if not packet: 
                continue 
            data += packet
        packet_data = data[:packet_size]
        data = data[packet_size: ]
        mouse_control_stream = base64.b64decode(packet_data)
        mouse_stream_str = mouse_control_stream.decode()
        mouse_conrol_strem_lst = np.frombuffer(mouse_stream_str)
        for pos in mouse_conrol_strem_lst:
            mouse_controller.position = (pos[0], pos[1])        


recv_vedio_thread = threading.Thread(target = recv_video_stream, args = ())
recv_audio_thread = threading.Thread(target = recv_audio_stream, args = ())
recv_vedio_thread.start() 
recv_audio_thread.start()