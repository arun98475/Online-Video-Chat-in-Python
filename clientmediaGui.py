import cv2
from socket import*  #socket, AF_INET, SOCK_STREAM,gethostname,SHUT_RDWR
from imutils.video import WebcamVideoStream
import pyaudio
from array import array
from threading import Thread
import numpy as np
import zlib
import struct
from PIL import ImageTk, Image
from tkinter import Label,Button

BufferSize = 4096
CHUNK=1024
lnF = 640*480*3
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100

class MediaChat:
    LOOPER=False
    clientVideoSocket = socket(family=AF_INET, type=SOCK_STREAM)
    clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
    frame_name="frame"
    #wvs = WebcamVideoStream(0)
    def __init__(self,win,HOST,PORT_VIDEO,PORT_AUDIO):
        self.win=win
        self.HOST=HOST
        self.PORT_VIDEO=PORT_VIDEO
        self.PORT_AUDIO=PORT_AUDIO
        self.label=Label(self.win)
        self.label.grid(row=3,column=3,padx=10)
        if self.LOOPER==False:
            image=ImageTk.PhotoImage(file='noload.png')
            self.label.configure(image=image)
            self.label.image=image
        
    def starter(self):
        self.clientVideoSocket.connect((self.HOST, self.PORT_VIDEO))
        try:
            MediaChat.wvs = WebcamVideoStream(0)
            self.wvs.start()
        except:
            print("Camera cannot start...")
        self.clientAudioSocket.connect((self.HOST, self.PORT_AUDIO))
        self.audio=pyaudio.PyAudio()
        self.stream=self.audio.open(format=FORMAT,channels=CHANNELS,rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)
        SendFrameThread = Thread(target=self.SendFrame).start()
        SendAudioThread = Thread(target=self.SendAudio).start()
        RecieveFrameThread = Thread(target=self.RecieveFrame).start()
        RecieveAudioThread = Thread(target=self.RecieveAudio).start()
    @classmethod
    def ChatManage(cls,Boolean):
        cls.LOOPER=Boolean
        if Boolean==False:
            cls.clientVideoSocket.shutdown(SHUT_RDWR) 
            cls.clientVideoSocket.close()
            cls.clientAudioSocket.shutdown(SHUT_RDWR) 
            cls.clientAudioSocket.close()
            cls.wvs.stream.release()
        else:
            cls.clientVideoSocket = socket(family=AF_INET, type=SOCK_STREAM)
            cls.clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
 
    def SendAudio(self):
        while self.LOOPER:
            try:
               data = self.stream.read(CHUNK)
               dataChunk = array('h', data)
               self.clientAudioSocket.sendall(data)
            except (error,OSError):
                    continue   
            

    def RecieveAudio(self):
        while self.LOOPER:
            try:
                data = self.recvallAudio(BufferSize)
                self.stream.write(data)
            except error:
                continue

    def recvallAudio(self,size):
            databytes = b''
            while len(databytes) != size:
               to_read = size - len(databytes)
               if to_read > (4 * CHUNK):
                   databytes += self.clientAudioSocket.recv(4 * CHUNK)
               else:
                   databytes += self.clientAudioSocket.recv(to_read)
            return databytes

            

    def SendFrame(self):
        while self.LOOPER:
            try:
                frame=self.Videolooper()
                frame = np.array(frame, dtype = np.uint8).reshape(1, lnF)
                jpg_as_text = bytearray(frame)

                databytes = zlib.compress(jpg_as_text, 9)
                length = struct.pack('!I', len(databytes))
                bytesToBeSend = b''
                self.clientVideoSocket.sendall(length)
                while len(databytes) > 0:
                    if (5000 * CHUNK) <= len(databytes):
                        bytesToBeSend = databytes[:(5000 * CHUNK)]
                        databytes = databytes[(5000 * CHUNK):]
                        self.clientVideoSocket.sendall(bytesToBeSend)
                    else:
                        bytesToBeSend = databytes
                        self.clientVideoSocket.sendall(bytesToBeSend)
                        databytes = b''
            except error:
                continue

        while self.LOOPER==False:
            try:
                frame=self.Videolooper()
            except:
                continue


    def RecieveFrame(self):
        while self.LOOPER:
            try:
                lengthbuf = self.recvallVideo(4)
                length, = struct.unpack('!I', lengthbuf)
                databytes = self.recvallVideo(length)
                img = zlib.decompress(databytes)
                if len(databytes) == length:
                  #  print("Recieving Media..")
                  #  print("Image Frame Size:- {}".format(len(img)))
                    img = np.array(list(img))
                    img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                    cv2.imshow(self.frame_name, img)
                    if cv2.waitKey(1) == 27:
                        cv2.destroyAllWindows()
                else:
                    print("Data CORRUPTED")
            except error:
                print("Not receving....")
                continue

    def recvallVideo(self,size):
            databytes = b''
            while len(databytes) != size:
                to_read = size - len(databytes)
                if to_read > (5000 * CHUNK):
                    databytes += self.clientVideoSocket.recv(5000 * CHUNK)
                else:
                    databytes += self.clientVideoSocket.recv(to_read)
            return databytes
        
    def Videolooper(self):
                frame = self.wvs.read()
                cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                fram = cv2.resize(cv2_im, (640, 480))
                #####Self Video loop start##########
                video=cv2.resize(fram, (320, 240))
                video=Image.fromarray(video)
                image=ImageTk.PhotoImage(image=video)
                self.label.configure(image=image)
                self.label.image=image
                #####Self Video loop stop##########
                return frame
    @classmethod
    def frame_namer(cls,new_name):
        cls.frame_name=new_name


