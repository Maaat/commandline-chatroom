#File: chatserver.py
#Author: Mathew Poff
#Description: server script to host a chat room.

import socket
import select
import sqlalchemy

#connect to db
db = sqlalchemy.create_engine('sqlite:///chatroom.db')
dbConn = db.connect()

#turn off db logging
db.echo = False

#set up the db if it wasn't already there
dbMessages = sqlalchemy.Table('messages', sqlalchemy.MetaData(db),
	sqlalchemy.Column('username',sqlalchemy.String(50)),
	sqlalchemy.Column('message',sqlalchemy.String(200))
)
if not db.engine.dialect.has_table(db, 'messages'):
	dbMessages.create()

messagesResult = dbConn.execute(sqlalchemy.select([dbMessages]))
messageLog = {'text':""}
for row in messagesResult:
	if row['username']: messageLog['text'] += row['username'] + '>'
	messageLog['text'] += row['message'] + '\n'

print(messageLog['text'])

#open log file
logfile = open('log.txt', 'a+')

#set of connected clients
clients = set()
clientNames = {}

#server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#initial server setup
def startServer():
	#set up the listening socket
	server.bind(('0.0.0.0', 8080))
	server.listen(10)
	print("The server has started.")

#continuously handles inputs from clients as longt as the server runs
def handleInputs():
	#accept connections in a loop
	while True:
		#wait for input
		(readable, writable, errored) = select.select([server] + list(clients), [], [])

		for connection in readable:
			#the connection being the main socket means that there is a new client
			if connection == server:
				(connection, address) = server.accept()
				connection.send(messageLog['text'].encode('utf-8'))
				clients.add(connection)

			else:

				#otherwise it is a new message from a client
				try:
					if not connection:
						raise ConnectionError()
					handleClientMessage(connection)

				#or the connection has been closed
				except ConnectionError:
					clients.remove(connection)
					broadcast(clientNames[connection]+" disconnected.")

#broadcast a message from the server
def broadcast(message):

	#print to server terminal
	print(message)

	#insert the message into teh database
	dbConn.execute( dbMessages.insert().values(username=None, message=message) )

	#append to memory log
	messageLog['text'] += message + '\n'

	#write to text log
	logfile.write(message+"\n")
	logfile.flush()

	#send to clients
	for client in clients:
		client.send((message).encode('utf-8'))

#writes the message to a file and the database and sends the message to all clients
def handleClientMessage(client):

	#client sent a message
	message = client.recv(1024).decode('utf-8')

	#check if the user is setting their name
	if message.startswith("/name:") and not hasattr(client, 'username'):
		#set username
		clientNames[client] = message.split("/name:")[1]
		broadcast(clientNames[client]+" has joined.")
		return

	signedMessage = clientNames[client]+'>'+message

	#insert the message into the database
	dbConn.execute(dbMessages.insert().values(username=clientNames[client], message=message))

	#append to memory log
	messageLog['text'] += signedMessage + '\n'

	#write to text log
	logfile.write(signedMessage+"\n")
	logfile.flush()
	print(signedMessage)
	for client in clients:
		client.send((signedMessage).encode('utf-8'))

#runs the server
def runServer():
	startServer()
	handleInputs()

if __name__ == "__main__":
	runServer()