from socket import* #AF_INET, SOCK_STREAM, socket,gethostname,SHUT_RDWR
from threading import Thread
from tkinter import Tk,Button,Text,Entry,END,StringVar,Scrollbar,E,S,N,Toplevel,Label
import pickle

HEADERSIZE = 10
class mainWindow:
    LOOPER=False
    VERYFY_PORT=6000
    client = socket(family=AF_INET, type=SOCK_STREAM)
    REG_port=7000
    PORT_CLI_ADD=8000
    registration=socket(family=AF_INET, type=SOCK_STREAM)
    def __init__(self,win,HOST,PORT,BufferSize):
        self.win=win
        self.HOST=HOST
        self.PORT=PORT
        self.BufferSize=BufferSize
        self.win.title("Chat")
        yscroll=Scrollbar(self.win)
        yscroll.grid(row=1,column=2,rowspan=5,sticky=E+S+N)
        self.Evar=StringVar()
        self.chat_box=Text(self.win,width=25,height=25,state='disabled',yscrollcommand=yscroll.set)
        yscroll.config(command=self.chat_box.yview)
        self.chat_entry=Entry(self.win,width=35,textvariable=self.Evar)
        self.chat_box.grid(row=1,column=1,columnspan=2,rowspan=5)
        self.chat_entry.grid(row=6,column=1)
        self.chat_entry.bind('<Return>',self.Send)
        Button(self.win,text="Send",command=self.Send).grid(row=6,column=2)

    def verifier(self,username,password):
        self.verify=socket(family=AF_INET, type=SOCK_STREAM)
        self.verify.connect((self.HOST, self.VERYFY_PORT))
        self.verify.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        details={"username":username,"password":password}
        cred=pickle.dumps(details)
        self.verify.send(cred)
        ch= self.verify.recv(16).decode("utf-8")
        if ch !="NOT-GRAND":
            self.verify.shutdown(SHUT_RDWR)
            self.verify.close()
            self.myuid=ch
            return ch
        self.verify.shutdown(SHUT_RDWR)
        self.verify.close()
        return False
        
    def starter(self):
        self.client.connect((self.HOST,self.PORT))
        RecieveThread = Thread(target=self.Recieve).start()
 
    @classmethod
    def ChatManage(cls,Boolean):
        cls.LOOPER=Boolean
        if Boolean==False:
            cls.client.shutdown(1) #SHUT_RDWR
            cls.client.close()
        else:
            cls.client = socket(family=AF_INET, type=SOCK_STREAM)
            
    def Recieve(self):
        while self.LOOPER:
            try:
                ch= self.client.recv(self.BufferSize).decode("utf-8")
                if not self.CodeAnalizer(ch):
                    self.chat_box.config(state='normal')
                    self.chat_box.insert(END,ch+"\n","he")
                    self.chat_box.tag_configure("he", foreground="green")
                    self.chat_box.config(state='disable')
            except error:
                if self.LOOPER:
                   self.client.connect((self.HOST,self.PORT))
                continue
            except OSError:
                continue


    def Send(self,*arg):
            msg = self.chat_entry.get()
            self.chat_box.config(state='normal')
            self.chat_box.insert(END,"You:"+msg+"\n","me")
            self.chat_box.tag_configure("me", foreground="blue")
            self.chat_box.tag_configure("me", justify='right')
            self.chat_box.config(state='disable')
            self.Evar.set("")
            if msg == "quit" or self.LOOPER==False:
                msg="quit"
                self.client.send(msg.encode("utf-8"))
                self.client.close()
            else:
                self.client.send(msg.encode("utf-8"))
    def newRegistration(self,details):
        name,username,password,x=details
        details_dic={"name":name,"username":username,"password":password}
        self.registration.connect((self.HOST, self.REG_port))
        cred=pickle.dumps(details_dic)
        self.registration.send(cred)
        msg=self.registration.recv(32).decode("utf-8")
        return msg
        
    def newClientConnect(self,uidno):
        self.newClient=socket(family=AF_INET, type=SOCK_STREAM)
        self.newClient.connect((self.HOST, self.PORT_CLI_ADD))
        uids={"client_uid":uidno,"req_uid":self.myuid}
        #print(uids)
        uid_to_send=pickle.dumps(uids)
        self.newClient.send(uid_to_send)
        auth= self.newClient.recv(1024).decode("utf-8")
        if auth =="NO":
            self.newClient.shutdown(SHUT_RDWR)
            self.newClient.close()
            return False
        self.newClient.shutdown(SHUT_RDWR)
        self.newClient.close()
        return auth
    def CodeAnalizer(self,code):
        if code[4:13]=="759aruS77":
            client_name=code[13:]
            self.requester_id=code[:4]
            self.ClientWindow(self.requester_id,client_name)
            return True
        return False
    def ClientWindow(self,requester_id,client_name):
        ctop=Tk()
        ctop.config(bg="blue")
        x = self.win.winfo_x()
        y = self.win.winfo_y()
        w = 250#top.winfo_width()
        h = 100#top.winfo_height()  
        ctop.geometry("%dx%d+%d+%d" % (w, h, x + 20, y + 25))
        ctop.title("Request")
        Label(ctop,text=f'You have a join request from {client_name}(id:{requester_id})').grid(row=0,column=0,columnspan=2,pady=10)
        def ClientResponse(boolean):
            newClient=socket(family=AF_INET, type=SOCK_STREAM)
            newClient.connect((self.HOST, self.PORT_CLI_ADD))
            if boolean:
                reply={"client_uid":self.myuid,"req_uid":self.requester_id,"reply":"1"}
            else:
                reply={"client_uid":self.myuid,"req_uid":self.requester_id,"reply":"0"}
            newClient.send(pickle.dumps(reply))
            newClient.shutdown(SHUT_RDWR)
            newClient.close()
            ctop.destroy()
        Button(ctop,text ="Admit",command=lambda:ClientResponse(True)).grid(row=1,column=0,padx=20,pady=20)
        Button(ctop,text="Reject",command=lambda:ClientResponse(False)).grid(row=1,column=1,padx=20,pady=20)
        ctop.mainloop()
