from tkinter import *
from tkinter import messagebox as mbox
from messageGui import mainWindow
from socket import gethostname
from clientmediaGui import MediaChat
from threading import Thread

win=Tk()
win.config(bg="#A6DDFF")
win.attributes('-alpha', 0.95)
username=""
password=""

def connect():
   global media,msg
   res = msg.verifier(username,password)
   if not res:
      mbox.showinfo( "Warning", "Username or Password is wrong")
   else:
      uidLabel.config(text=f'UID:{res}')
      mainWindow.ChatManage(True)
      msg.starter()
      MediaChat.ChatManage(True)
      media.starter()
      dis_conn_but.config(state="normal",bg="red")
      conn_but.config(state="disabled",bg="light green")
      filemenu.entryconfig(0, state="normal")
             
def mesgThread():
    global msg
    msg=mainWindow(win,HOST="ARUN-PC",PORT=5000,BufferSize=1024)

def mediaThread():
    global media
    media=MediaChat(win,HOST="ARUN-PC",PORT_VIDEO=3000,PORT_AUDIO=4000)
    
def disConnect():
    MediaChat.ChatManage(False)
    mainWindow.ChatManage(False)
    dis_conn_but.config(state="disabled",bg="#FF5967")
    filemenu.entryconfig(0, state="disabled")
    conn_but.config(state="normal",bg="green")
def login():
    logwin=Tk()
    logwin.title("Login")
    x = win.winfo_x()
    y = win.winfo_y()
    w = 250#top.winfo_width()
    h = 100#top.winfo_height()  
    logwin.geometry(f'{w}x{h}+{x + 20}+{y + 25}')
    Label(logwin,text="Username:").grid(row=0,column=0)
    Label(logwin,text="Password:").grid(row=1,column=0)
    user_name=Entry(logwin)
    user_name.grid(row=0,column=1)
    paswd=Entry(logwin,show="*")
    paswd.grid(row=1,column=1)
    def log():
        global username,password
        if user_name.get()=="" or paswd.get()=="":
           mbox.showinfo( "Warning", "Username or Password filelds should not be empty")
        else:
           username=user_name.get()
           password=paswd.get()
           conn_but.config(state="normal",bg="green")
           logwin.destroy()
           MediaChat.frame_namer(username)
    Button(logwin,text="Login",command=log).grid(row=3,column=1,sticky=E+N+S+W)
    logwin.mainloop()
def register():
   regwin=Tk()
   regwin.title("Registration")
   lables=("Enter your Name:","Enter a Username:","Enter a Password:","Re-enter the Password:")
   def createLabelsAndEntry(pos):
      return Label(regwin,text=lables[pos]).grid(row=pos,column=0,sticky=E),Entry(regwin)
   LandE=[createLabelsAndEntry(i) for i in range(len(lables))]
   LandE[2][1].config(show="*")
   LandE[3][1].config(show="*")
   for i in range(len(lables)):
      LandE[i][1].grid(row=i,column=1,sticky=W,padx=8)
   def REGISTER():
      userRegDetails=tuple(i[1].get() for i in LandE)
      if "" in userRegDetails:
         mbox.showinfo( "Warning", "All fields required")
      elif userRegDetails[2]!=userRegDetails[3]:
         mbox.showinfo( "Warning","Password mismatch")
      else:
         reply=msg.newRegistration(userRegDetails)
         if reply=="success":
            mbox.showinfo( "Success","Your Details uploaded")
            conn_but.config(state="normal",bg="green")
            regwin.destroy()
         elif reply == "failure":
            mbox.showinfo( "Failure","Error occured")
         else:
            mbox.showinfo( "Exist",reply)
   Button(regwin,text="Register",bg="light green",command=REGISTER).grid(row=4,column=1,sticky=N+S+W+E,pady=8,padx=8)
   regwin.mainloop()   
 
def ConnectToClients():
    top=Toplevel()
    x = win.winfo_x()
    y = win.winfo_y()
    w = 250#top.winfo_width()
    h = 100#top.winfo_height()  
    top.geometry("%dx%d+%d+%d" % (w, h, x + 20, y + 25))
    top.title("Connect")
    Label(top,text="Enter the UID Number",pady=5).pack()
    uidEntry=Entry(top,width=20)
    uidEntry.pack(pady=5)
    def Meet():
        global msg
        res_uid=msg.newClientConnect(uidEntry.get())
        top.destroy()
        if not res_uid:
            mbox.showinfo( "Rejected","Your request has been not admitted")
        else:
            mbox.showinfo( "Information",res_uid)
        
    Button(top,text="Meet",width=16,pady=2,command=Meet).pack()
    top.mainloop()

      
first_thread=Thread(target=mesgThread).start()
second_thread=Thread(target=mediaThread).start()

conn_but=Button(win,text="Connect",command=connect,bg="light green",width=20,state="disabled")
conn_but.grid(row=5,column=3,sticky=E+S)

dis_conn_but=Button(win,text="Dis-Connect",command=disConnect,bg="#FF5967",width=20,state="disabled")
dis_conn_but.grid(row=5,column=3,sticky=W+S,padx=10)

loginButton=Button(win,text="Login",command=login,bg="blue",width=20)
loginButton.grid(row=1,column=3,sticky=N+W,padx=10)

registerButton=Button(win,text="Registration",command=register,bg="grey",width=20)
registerButton.grid(row=1,column=3,sticky=N+E)

uidLabel=Label(win,text="UID")
uidLabel.grid(row=2,column=3)

photo = PhotoImage(file ="tec.png")

Label(win,image=photo).grid(row=1,rowspan=5,column=4,sticky=N+E+S+W,padx=10)

menu=Menu(win)
win.config(menu=menu)
filemenu=Menu(menu,tearoff=0)
filemenu.add_command(label="connect" ,command=ConnectToClients,state="disabled")
menu.add_cascade(label="connect",menu=filemenu)
win.mainloop()
