from socket import* #socket, AF_INET, SOCK_STREAM,gethostname
from threading import Thread
import struct
import pickle
import sqlite3
import concurrent.futures
import random
from AVMClass import AudioVideoMessage
HOST = gethostname()
PORT_VIDEO = 3000
PORT_AUDIO = 4000
PORT_MSG = 5000
VERYFY_PORT = 6000
REG_PORT = 7000
PORT_CLI_ADD=8000

lnF = 640*480*3
CHUNK = 1024
BufferSize = 4096
msg_BufferSize = 1024
addressesAudio = {}
addresses = {}
threads = {}
Athreads = {}

msg_addresses = {}
clients = {}

onlineClients=[]
tempClients={}

clientName="anonimous"
connection=True
clientRegisters={}

randindex=0
def randgen():
        global randindex
        rand=random.sample(range(7000,8000), 1000)
        random_number = rand[randindex]
        randindex+=1
        return random_number
def VideoServer():
        serverVideo = socket(family=AF_INET, type=SOCK_STREAM)
        serverVideo.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        serverVideo.bind((HOST, PORT_VIDEO))
        serverVideo.setblocking(1)
        serverVideo.listen(20)
        print("Waiting for video connection..\n")
        videoSocket,addr=serverVideo.accept()
        print("video connected")
        return videoSocket
        
def AudioServer():
        serverAudio = socket(family=AF_INET, type=SOCK_STREAM)
        serverAudio.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        serverAudio.bind((HOST, PORT_AUDIO))
        serverAudio.setblocking(1)
        serverAudio.listen(20)
        print("Waiting for audio connection..\n")
        audioSocket,addr=serverAudio.accept()
        print("Audio connected")
        return audioSocket
def MsgServer():
        server = socket(family=AF_INET, type=SOCK_STREAM)
        server.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        server.bind((HOST, PORT_MSG))
        server.setblocking(1)
        server.listen(20)
        print("Waiting for message Connections... \n")
        msgSocket,addr=server.accept()
        print("Messenger connected")
        return msgSocket
def VerServer():
        serverVerification = socket(family=AF_INET, type=SOCK_STREAM)
        serverVerification.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        serverVerification.bind((HOST, VERYFY_PORT))
        serverVerification.setblocking(1)
        serverVerification.listen(20)
        print("Waiting for verification... \n")
        verSocket,addr=serverVerification.accept()
        print("verification connected")
        cred=verSocket.recv(msg_BufferSize)
        msg=pickle.loads(cred)
        conn=sqlite3.connect("mydb.db")
        user_name=msg['username']
        datas=conn.execute("SELECT * FROM personal WHERE username='{}'" .format(user_name))
        data=datas.fetchone()
        if data is not None:
            if data[3]==msg['password']:
                clientName=data[1]
                uin=randgen()
                clientRegisters[clientName]=uin
                verSocket.send((str(uin)).encode("utf-8")) 
            else:
                verSocket.send(("NOT-GRAND").encode("utf-8"))
                clientName=None
                uin=None
        else:
            verSocket.send(("NOT-GRAND").encode("utf-8"))
            clientName=None
            uin=None
        conn.close()
        return clientName,uin
        
requestAdd={}
def ClientReq():
    while True:
        serverConnReq = socket(family=AF_INET, type=SOCK_STREAM)
        serverConnReq.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        serverConnReq.bind((HOST, PORT_CLI_ADD))
        serverConnReq.setblocking(1)
        serverConnReq.listen(20)
        print("Waiting for serverConnReq... \n")
        verSocket,addr=serverConnReq.accept()
        print("verification connected")
        try:
            uids=verSocket.recv(msg_BufferSize)
            uid=pickle.loads(uids)
            if 'reply' in uid:
                requesterID=uid['req_uid']
                requestedID=uid['client_uid']
                sock=requestAdd[requesterID]
                if uid['reply']=='1':
                    sock.send(f'{requested_name} has joined the chat'.encode("utf-8"))
                    ClientAdder(requesterID,requestedID) 
                elif uid['reply']=='0':
                    sock.send("NO".encode("utf-8"))     
                else:
                    continue
            else:
                requested_uid=uid['client_uid']
                requester_uid=uid["req_uid"]
                requestAdd[requester_uid]=verSocket
                if int(requested_uid) not in user_sockets:
                    verSocket.send("Requested user is not online".encode("utf-8"))
                elif requested_uid == requester_uid:
                    verSocket.send("You can't connect yourself".encode("utf-8"))
                else:
                    requester_name=user_sockets[int(requester_uid)][0]
                    requested_name=user_sockets[int(requested_uid)][0]
                    requested_sok=user_sockets[int(requested_uid)][3]
                    code=f'{requester_uid}759aruS77{requester_name}'
                    requested_sok.send(code.encode("utf-8"))
        except:
            continue
        
def RegServer():     
    while True:
        try:
            serverRegistration = socket(family=AF_INET, type=SOCK_STREAM)
            serverRegistration.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
            serverRegistration.bind((HOST, REG_PORT))
            serverRegistration.listen(20)
            print("Waiting for registration... \n")
            client, addr = serverRegistration.accept()
            cred=client.recv(msg_BufferSize)
            msg=pickle.loads(cred)
            conn=sqlite3.connect("mydb.db")
            c=conn.cursor()
            datas=conn.execute("SELECT * FROM personal WHERE username='{}'" .format(msg["username"]))
            data=datas.fetchone()
            if data is None:
               user_details=(None,msg["name"],msg["username"],msg["password"])
               c.execute('''INSERT INTO personal VALUES(?,?,?,?)''',user_details)
               conn.commit()
               conn.close()
               client.send(("success").encode("utf-8"))
            else:
               client.send(("Username already exist").encode("utf-8"))
        except:
            client.send(("failure").encode("utf-8"))
            continue
     

def VideoAudioMsg():
    with concurrent.futures.ThreadPoolExecutor() as executor:
            verify_server=executor.submit(VerServer)
            if verify_server.result() != (None,None):
                video_server = executor.submit(VideoServer)
                audio_server = executor.submit(AudioServer)
                msg_server = executor.submit(MsgServer)
                return verify_server.result(),video_server.result(),audio_server.result(),msg_server.result()
    return None,None,None,None

users={}
user_sockets={}
def MainExecuter():
    while True:
        try:
            clNameUID,videoSocket,audioSocket,msgSocket=VideoAudioMsg()
            if clNameUID is not None:
                clientName,UID=clNameUID
                user_sockets[UID]=(clientName,videoSocket,audioSocket,msgSocket)
                users[UID]=AudioVideoMessage(clientName,videoSocket,audioSocket,msgSocket,UID)
                users[UID].ConnectionsVideo()
                users[UID].ConnectionsSound()
                users[UID].Connections()
            else:
                continue
        except error:
            print("Connection error...reconnecting")
            continue  

def ClientAdder(your_uid,uid_num):           
    users[int(your_uid)].ClientAdder(user_sockets[int(uid_num)])
    users[int(uid_num)].ClientAdder(user_sockets[int(your_uid)])
    

def disconnected_user_manage():
  while True:
     try:
        if len(AudioVideoMessage.CONNECTION_DETECT)>0:
            for i in AudioVideoMessage.CONNECTION_DETECT:
                if AudioVideoMessage.CONNECTION_DETECT[i]==False and i in user_sockets:
                    user_sockets.pop(i)
     except:
            continue


Thread(target=MainExecuter).start()
Thread(target=ClientReq).start()
Thread(target=RegServer).start()
Thread(target=disconnected_user_manage).start()

