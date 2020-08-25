from socket import*
from threading import Thread
import struct
import pickle

lnF = 640*480*3
CHUNK = 1024
BufferSize = 4096
msg_BufferSize = 1024

threads = {}
Athreads = {}

msg_addresses = {}


onlineClients=[]
tempClients={}

clientName="anonimous"
connection=True

class AudioVideoMessage:
    CONNECTION_DETECT={}
    def __init__(self,clientName,videoSocket,audioSocket,msgSocket,UID):
        self.addressesAudio = {}
        self.addresses = {}
        self.clients = {}
        self.clientName=clientName
        self.videoSocket=videoSocket
        self.audioSocket=audioSocket
        self.msgSocket=msgSocket
        self.UID=UID
        self.CONNECTION_DETECT[self.UID]=True
    def ConnectionsVideo(self):
        self.addresses[self.videoSocket] = self.clientName
        if len(self.addresses) > 0:
            for sockets in self.addresses:
                if sockets not in threads:
                    threads[sockets] = True
                    Thread(target=self.ClientConnectionVideo, args=(sockets,)).start()

          
            
    def ClientConnectionVideo(self,clientVideo):
        while True:
            try:
                lengthbuf = self.recvall(clientVideo, 4)
                length, = struct.unpack('!I', lengthbuf)
                self.recvall(clientVideo, length)
            except error:
                print("Client Video disconnected")
                self.addresses.pop(clientVideo)
                threads.pop(clientVideo)
                break
            except:
                continue
            
    def recvall(self,clientVideo, BufferSize):
        databytes = b''
        i = 0
        while i != BufferSize:
            to_read = BufferSize - i
            if to_read > (1000 * CHUNK):
                databytes = clientVideo.recv(1000 * CHUNK)
                i += len(databytes)
                self.broadcastVideo(clientVideo, databytes)
            else:
                if BufferSize == 4:
                    databytes += clientVideo.recv(to_read)
                else:
                    databytes = clientVideo.recv(to_read)
                i += len(databytes)
                if BufferSize != 4:
                    self.broadcastVideo(clientVideo, databytes)
        if BufferSize == 4:
            self.broadcastVideo(clientVideo, databytes)
            return databytes
            
    def broadcastVideo(self,clientSocket, data_to_be_sent):
   
        for clientVideo in self.addresses:
            if clientVideo != clientSocket:
                clientVideo.sendall(data_to_be_sent)
    
    def ConnectionsSound(self):
            self.addressesAudio[self.audioSocket] = self.clientName
            if len(self.addressesAudio) > 0:
                for sockets in self.addressesAudio:
                    if sockets not in Athreads:
                        Athreads[sockets] = True
                        Thread(target=self.ClientConnectionSound, args=(sockets, )).start()

    def ClientConnectionSound(self,clientAudio):
        while True:
            try:
                data = clientAudio.recv(BufferSize)
                self.broadcastSound(clientAudio, data)
            except error:
                print("Client Audio disconnected")
                self.addressesAudio.pop(clientAudio)
                break
            except:
                continue
    def broadcastSound(self,clientSocket, data_to_be_sent):
   
        for clientAudio in self.addressesAudio:
            if clientAudio != clientSocket:
                clientAudio.sendall(data_to_be_sent)
    
    def Connections(self):
           self.msgSocket.send((f"Welcome {self.clientName} to Chat Room. Type 'quit' to exit.").encode("utf-8"))
           msg_addresses[self.msgSocket] = self.clientName
           Thread(target = self.ClientConnection, args=(self.msgSocket, )).start()

    def ClientConnection(self,client):
        try:
            client.send(("Hello {}".format(self.clientName)).encode("utf-8"))
            message = ("{} has joined the chat..").format(self.clientName)
            self.Broadcast(message.encode("utf-8"))
            self.clients[client] = self.clientName
            while True:
                try:
                    msg = client.recv(msg_BufferSize).decode("utf-8")
                    if msg != "":
                        self.Broadcast(msg.encode("utf-8"), self.clientName)
                    else:
                        message = ("{} has left the chat.").format(self.clients[client])
                        self.Broadcast(message.encode("utf-8"))
                        client.send(("Will see you soon..").encode("utf-8"))
                        del self.clients[client]
                        break
                except error:
                    print("Message chat disconnected..")
                    del self.clients[client]
                    self.CONNECTION_DETECT[self.UID]=False
                    break
        except:
            print("Unknown error occurred!!")
            

    def Broadcast(self,msg, nam = ""):
        for sockets in self.clients:
            if self.clients[sockets]!=nam:
                name=nam+": "
                try:
                    sockets.send(name.encode("utf-8") + msg)
                except error:
                    continue
    def ClientAdder(self,clientdetails):
        clientName,videoSocket,audioSocket,msgSocket = clientdetails
        self.addressesAudio[audioSocket] = clientName
        self.addresses[videoSocket] = clientName
        self.clients[msgSocket] = clientName

    
    
    
