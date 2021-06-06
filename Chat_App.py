from tkinter import *
from tkinter import font
import paho.mqtt.client as mqtt
from tkinter import messagebox
from tkinter import ttk
import random as rd
import string



class ChatClass:
	conn_status=False
	incoming_massage="\n"
	DummyVar="\n"
	TopicName = "ttopic"
	Myname="\n"
	l=["blue","red","purple","yellow","orange"]
	counter=0
	curr=0
	d={}

	def __init__(self):
		
		self.Window = Tk()          
		self.Window.withdraw()
		self.login = Toplevel()
		
		self.login.title("Chat Room App")
		self.login.resizable(width = False,height = False)
		self.login.configure(width = 600,height = 400,)

		self.pls = Label(self.login,text = "Enter Chat Room...",justify = CENTER,font = "Helvetica 20")
		self.pls.place(relheight = 0.1,relx = 0.30,rely = 0.1)

		self.labelName1=Label(self.login,text = "Your Name: ",font = "Helvetica 15")
		self.labelName1.place(relheight = 0.15,relx = 0.137,rely = 0.24)
		
		self.entryName1=Entry(self.login,font = "Helvetica 14")
		self.entryName1.place(relwidth = 0.38,relheight = 0.05,relx = 0.34,rely = 0.29)
        
		self.entryName1.focus()

		self.labelName2 = Label(self.login,text = "Room Name: ",font = "Helvetica 15")
		self.labelName2.place(relheight = 0.15,relx = 0.134,rely = 0.34)
		
		self.entryName2 = Entry(self.login,font = "Helvetica 14")
		self.entryName2.place(relwidth = 0.38,relheight = 0.05,relx = 0.34,rely = 0.39)
        
		self.entryName2.focus()

		self.labelName3 = Label(self.login,text = "Password: ",font = "Helvetica 15")
		self.labelName3.place(relheight = 0.15,relx = 0.135,rely = 0.44)
		
		self.entryName3 = Entry(self.login,show='*',font = "Helvetica 14")
		self.entryName3.place(relwidth = 0.38,relheight = 0.05,relx = 0.34,rely = 0.49)
        
		self.entryName3.focus()


		self.go = Button(self.login,text = "Next",font = "Helvetica 15 bold",
        command = lambda: self.ChatWindow(self.entryName1.get(),
                                       self.entryName2.get(),
                                       self.entryName3.get()))
		self.go.place(relwidth = 0.2,relheight = 0.07,relx = 0.44,rely = 0.68)
		self.Window.mainloop()
	
	def ChatWindow(self,name,un,pw):
		self.login.destroy()

		ChatClass.Myname=name
		
		self.window = Tk()
		self.window.title("Chat room")
		self.window.minsize(600, 510)

		self.Frame1 = LabelFrame(self.window, text="Chat Window",font = "Helvetica 12", width=600, height=400)
		self.Frame1.place(y=0, x=0)
		self.Frame2 = LabelFrame(self.window, text="Enter Massege",font = "Helvetica 12", width=600, height=63)
		self.Frame2.place(y=405, x=0)

		self.yscroll = Scrollbar(self.Frame1)
		self.yscroll.place(y=0, x=580, height=370)
		self.xscroll = Scrollbar(self.Frame1, orient=HORIZONTAL)
		self.xscroll.place(y=371, x=0, width=580)

		self.ChatText = Text(self.Frame1, yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set,background="lightgrey")
		self.ChatText.place(x=0, y=0, width=580, height=370)
		self.ChatText.configure(state="disabled")

		# self.ChatText.tag_config('otheruser', background="white",foreground=ChatClass.l[ChatClass.curr],font=("Helvetica",13))
		self.ChatText.tag_config('myown', background="lightgreen",justify=RIGHT,font=("Helvetica", 13))
		self.ChatText.tag_config('otherperson', background="white",font=("Helvetica", 12))
		
		self.yscroll.config(command=self.ChatText.yview)
		self.xscroll.config(command=self.ChatText.xview)

		self.MassageFill = Text(self.Frame2, font=("Helvetica", 12))
		self.MassageFill.place(x=0, y=0, width=475, height=40)

		self.SendButton = Button(self.Frame2, text="Send",font = "Helvetica 12 bold", command=self.send_message)
		self.SendButton.place(x=480, y=0, width=100, height=40)
		self.SendButton.configure(bg="grey",fg="white")

		self.ExitButton = Button(self.window, text="Exit",font = "Helvetica 12 bold", command=self.exit_room)
		self.ExitButton.place(x=260, y=474, width=80, height=30)
		self.ExitButton.configure(bg="grey",fg="white")

		#Server connection

		self.client = mqtt.Client()
		self.client.on_connect =self.on_connection
		self.client.on_message =self.on_message
		self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
		#set username and password
		self.client.username_pw_set(un, pw)

		self.client.connect("527bba9c3e0245fa96be5381346654c0.s1.eu.hivemq.cloud", 8883)

		self.client.loop_start()
		
		self.window.mainloop()

	def on_connection(self,client, user_data, flag, rc):
		# ChatClass.conn_status  # global variable in this file
		self.status_decoder = {  
			0: "Successfully Connected",
			1: "Connection refused: Incorrect Protocol Version",
			2: "Connection refused: Not Authorized",
		}
		self.conn_text = ("{} has Joined the Room with status: \n\t{}.\n".format(ChatClass.Myname,self.status_decoder.get(rc)))
		self.ChatText.configure(state="normal")
		self.ChatText.insert(INSERT, str(self.conn_text))
		self.client.subscribe(ChatClass.TopicName)
		ChatClass.conn_status = True
		self.ChatText.configure(state="disabled")


	def on_message(self,client,user_data,msg):
		# check incoming payload to prevent owner echo text
		
		ChatClass.incoming_massage = msg.payload.decode("utf-8")
		if ChatClass.incoming_massage.find(ChatClass.DummyVar) >= 0:
			pass
		else:
			self.ChatText.configure(state="normal")
			
			self.output_user=str(ChatClass.incoming_massage).splitlines()[0]

			if self.output_user in ChatClass.d:
				ChatClass.curr=ChatClass.d[self.output_user]
			else:
				ChatClass.d[self.output_user]=ChatClass.counter
				ChatClass.counter+=1
				ChatClass.curr=ChatClass.d[self.output_user]
			
			self.ChatText.tag_config(self.output_user, background="white",foreground=ChatClass.l[ChatClass.curr],font=("Helvetica",13))
			
			self.ChatText.insert(INSERT,self.output_user,self.output_user)
			self.ChatText.insert(INSERT,'  '+str(ChatClass.incoming_massage).splitlines()[1]+'\n','otherperson')
			
			self.ChatText.configure(state="disabled")


	def send_message(self):
		self.get_message = str(self.MassageFill.get("1.0", END))
		if self.get_message == " ":
			pass
		else:
			self.send_message = "{}\n{}\n".format(ChatClass.Myname,self.get_message)
			ChatClass.DummyVar = self.send_message
			self.ChatText.configure(state="normal")
			self.client.publish(ChatClass.TopicName,self.send_message)
			#self.print_message="\t{}\t\n".format(self.get_message)
			self.ChatText.insert(INSERT, str(self.get_message),'myown')
			self.MassageFill.delete("1.0", END)
			self.ChatText.configure(state="disabled")

	def exit_room(self):
		self.client.loop_stop(force=True)
		self.window.destroy()
	 

a = ChatClass()