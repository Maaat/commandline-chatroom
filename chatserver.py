#File: chatserver.py
#Author: Mathew Poff
#Description: server script to host a chat room.

import sys
import socket
import select
import sqlalchemy

class ChatServer():

	#constructor
	def __init__(self):
		#connect to db
		self.db = sqlalchemy.create_engine('sqlite:///chatroom.db')
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

	#continuously handles inputs from clients as long as the server runs
	def handleInputs(self):
		#accept connections in a loop
		while True:
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
		self.handleInputs()

#entry point
if __name__ == "__main__":
	ChatServer().runServer(8080)