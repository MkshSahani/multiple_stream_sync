import socket, cv2, base64, pyaudio, argparse, struct, imutils
import threading, pyshine as ps, pickle

ap = argparse.ArgumentParser()
ap.add_argument("-ip", "-ip_address", required=True, type = str) # ip address of server. 
ap.add_argument("-vp", "--video-port", required=True, type = int) # video port number
ap.add_argument("-ap", "--audio-port", required=True, type = int) # audio port number. 
args = vars(ap.parse_args())
print(args)
ip_address = args['ip']
video_stream_port = args['video_port']
audio_stream_port = args['audio_port']
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
        frame = audio_stream_driver.get()
        # audio_frame = pickle.dumps(frame)
        audio_frame = base64.encode(frame)
        audio_frame = struct.pack("Q", len(audio_frame)) + audio_frame
        print("==============> Audio Sent =================")
        audio_stream_socket.sendto(audio_frame, audio_client_socket)

vedio_stream_send_thread = threading.Thread(target=send_video_stream, args=())
audio_stream_send_thread = threading.Thread(target=send_audio_stream, args = ())
vedio_stream_send_thread.start()
audio_stream_send_thread.start()
