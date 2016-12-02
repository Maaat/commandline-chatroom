#File: chatserver.py
#Author: Mathew Poff
#Description: server script to host a chat room.

import sys
import socket
import select
import sqlalchemy
import threading
import xlsxwriter

class ChatServer():

	#constructor
	def __init__(self):
		#connect to db
		self.db = sqlalchemy.create_engine('sqlite:///chatroom.db',connect_args={'check_same_thread': False})
		self.dbConn = self.db.connect()

		#turn off db logging
		self.db.echo = False

		#set up the db if it wasn't already there
		self.dbMessages = sqlalchemy.Table('messages', sqlalchemy.MetaData(self.db),
			sqlalchemy.Column('username',sqlalchemy.String(50)),
			sqlalchemy.Column('message',sqlalchemy.String(200))
		)
		if not self.db.engine.dialect.has_table(self.db, 'messages'):
			self.dbMessages.create()

		#get message log from the database
		messagesResult = self.dbConn.execute(sqlalchemy.select([self.dbMessages]))

		#turn the message log into  single string
		self.messageLog = ""
		for row in messagesResult:
			if row['username']: self.messageLog += row['username'] + '>'
			self.messageLog += row['message'] + '\n'

		#display messageLog to the server terminal
		print(self.messageLog)

		#open log file
		self.logfile = open('log.txt', 'a+')

		#set of connected clients
		self.clients = set()
		self.clientNames = {}

		#server socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#initial server setup
	def startServer(self, port):
		#start the listening socket
		self.serverSocket.bind(('0.0.0.0', port))
		self.serverSocket.listen(10)
		print("The server has started.")

	#handle input written into the server terminal
	def handleUserInput(self):
		while True:
			try:
				message = input()

				#stop the server on '/exit'
				if message.lower() == '/exit':
					self.serverSocket.close()
					break

				#export a csv file on '/csv'
				elif message.split(' ')[0].lower() == '/spreadsheet':
					self.exportSpreadsheet(message.split(' ')[-1] if len(message.split(' '))>1 else '')

			except EOFError:
				self.serverSocket.close()
				break

	#export the chat log as a csv file
	def exportSpreadsheet(self, filename):
		#default filename is 'chatlog'
		filename = filename or 'chatlog'

		#init the spreadsheet file and writer
		workbook = xlsxwriter.Workbook(filename+'.xlsx')
		worksheet = workbook.add_worksheet()
		row = 0
		usernameCol=0
		messageCol=1

		#define bold text for headers
		bold = workbook.add_format({'bold': True})

		#widen the columns
		worksheet.set_column('A:A', 20)
		worksheet.set_column('B:B', 50)

		#pull the message from db
		messagesResult = self.dbConn.execute(sqlalchemy.select([self.dbMessages]))

		#write the headers
		worksheet.write(0,usernameCol,'Username',bold)
		worksheet.write(0,messageCol,'Message',bold)
		row += 1

		#write the db messages to the csv file
		for message in messagesResult:
			worksheet.write(row, usernameCol, message['username'])
			worksheet.write(row, messageCol, message['message'])
			row += 1

		print('speadsheet exported as '+filename+'.xlsx')

	#continuously handles inputs from clients as long as the server runs
	def handleClientInput(self):
		#accept connections in a loop
		while True:

			try:
				#wait for input
				(readable, writable, errored) = select.select([self.serverSocket] + list(self.clients), [], [])

				for connection in readable:
					#the connection being the main socket means that there is a new client
					if connection == self.serverSocket:
						(connection, address) = self.serverSocket.accept()
						connection.send(self.messageLog.encode('utf-8'))
						self.clients.add(connection)

					else:
						#otherwise it is a new message from a client
						try:
							if not connection:
								raise ConnectionError()
							self.handleClientMessage(connection)

						#or the connection has been closed
						except ConnectionError:
							self.clients.remove(connection)
							self.broadcast(self.clientNames[connection]+" disconnected.")

			except: break
		print("The server has stopped")

	#broadcast a message from the server
	def broadcast(self, message):
		#print to server terminal
		print(message)

		#insert the message into the database
		self.dbConn.execute( self.dbMessages.insert().values(username=None, message=message) )

		#append to memory log
		self.messageLog += message + '\n'

		#write to text log
		self.logfile.write(message+"\n")
		self.logfile.flush()

		#send to clients
		for client in self.clients:
			client.send((message).encode('utf-8'))

	#writes the message to a file and the database and sends the message to all clients
	def handleClientMessage(self, client):
		#client sent a message
		message = client.recv(1024).decode('utf-8')

		#do not allow empty meessages
		if not message or not message.strip(): raise ConnectionError()

		#check if the user is setting their name
		if message.startswith("/name:") and not hasattr(client, 'username'):
			#set username
			self.clientNames[client] = message.split("/name:")[1]
			self.broadcast(self.clientNames[client]+" has joined.")
			return

		#add the client name
		signedMessage = self.clientNames[client]+'>'+message

		#insert the message into the database
		self.dbConn.execute(self.dbMessages.insert().values(username=self.clientNames[client], message=message))

		#append to memory log
		self.messageLog += signedMessage + '\n'

		#write to text log
		self.logfile.write(signedMessage+"\n")
		self.logfile.flush()
		print(signedMessage)
		for client in self.clients:
			client.send((signedMessage).encode('utf-8'))

	#runs the server
	def runServer(self, port):
		self.startServer(port)

		#handle client and user inputs in separate threads
		threading.Thread(target=self.handleUserInput).start()
		self.handleClientInput()

#entry point
if __name__ == "__main__":
	ChatServer().runServer(8080)