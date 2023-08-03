import socket, cv2, base64,argparse, struct, imutils
import threading, pyshine as ps, time
from pynput.mouse import Controller

ap = argparse.ArgumentParser()
ap.add_argument("-ip", "-ip_address", required=True, type = str) # ip address of server. 
ap.add_argument("-vp", "--video-port", required=True, type = int) # video port number
ap.add_argument("-ap", "--audio-port", required=True, type = int) # audio port number. 
ap.add_argument("-mp", "--mouse-port", required=True, tpye = int) # mouse control data port 
args = vars(ap.parse_args())
print(args)
ip_address = args['ip']
video_stream_port = args['video_port']
audio_stream_port = args['audio_port']
mouse_port = args['mouse_port']
BUFF_SIZE = 65536 

print(args)


## video stream socket 
video_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_stream_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
video_stream_socket.bind((ip_address, video_stream_port))

## audio stream socket 
audio_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
audio_stream_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
audio_stream_socket.bind((ip_address, audio_stream_port))
AUDIO_MODE = 'send'
audio_stream_driver, context = ps.audioCapture(mode = AUDIO_MODE)

## Mouse Control Stream Socket. 
mouse_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mouse_controller = Controller()
mouse_stream_socket.bind((ip_address, mouse_port))
mouse_stream_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

def send_video_stream(): 
    msg, video_client_socket = video_stream_socket.recvfrom(BUFF_SIZE)
    print(msg.decode())
    vid = cv2.VideoCapture(0)
    while True:
        ret, frame = vid.read()
        if not ret:
            continue 
        frame = imutils.resize(frame)
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)
        message = struct.pack("Q", len(message)) + message
        video_stream_socket.sendto(message, video_client_socket)
        cv2.imshow("Captured", frame)
        key = cv2.waitKey(1) 
        if key == 13: 
            break 
    video_stream_socket.close()

def send_audio_stream(): 
    msg, audio_client_socket = audio_stream_socket.recvfrom(BUFF_SIZE)
    print(msg.decode())
    while True:
        frame = audio_stream_driver.get(block=False)
        frame = frame.tobytes()
        audio_frame = struct.pack("Q", len(frame)) + frame
        audio_stream_socket.sendto(audio_frame, audio_client_socket)


data = []
def send_mouse_stream():
    msg, mouse_control_client = mouse_stream_socket.recvfrom(BUFF_SIZE)
    prev_current_time = time.time()
    seq_number = 0
    while True:
        pos = mouse_controller.position 
        data.append(pos)
        current_time = time.time()
        if current_time - prev_current_time >= 0.001:
            seq_number += 1
            str_data = str(data).encode()
            str_data_encode = base64.b64encode(str_data)
            message_packet = struct.pack("Q", len(str_data_encode)) + struct.pack("Q", seq_number) + \
            struct.pack("d", prev_current_time) + str_data_encode         
            mouse_stream_socket.sendto(message_packet, mouse_control_client)
            prev_current_time = time.time()
            data = []

vedio_stream_send_thread = threading.Thread(target=send_video_stream, args=())
audio_stream_send_thread = threading.Thread(target=send_audio_stream, args=())
mouse_stream_send_thread = threading.Thread(target=send_mouse_stream, args=())
vedio_stream_send_thread.start()
audio_stream_send_thread.start()
mouse_stream_send_thread.start()
