#File: chatserver.py
#Author: Mathew Poff
#Description: server script to host a chat room.

import socket
import select

#open log file
log = open('log.txt', 'a+')

#set of connected clients
clients = set();

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
				handleMessage("A client joined.")
				(connection, address) = server.accept()
				clients.add(connection)

			else:

				#otherwise it is a new message
				try:
					message = connection.recv(1024).decode('utf-8')
					if not message:
						raise ConnectionError()
					else:
						handleMessage(message)

				#or the connection has been closed
				except ConnectionError:
					clients.remove(connection)
					handleMessage("A client disconnected.")

#writes the message to a file and sends the message to all clients
def handleMessage(message):
	log.write('>'+message+"\n")
	log.flush()
	print('>'+message)
	for client in clients:
		client.send(('>'+message).encode('utf-8'))

#runs the server
def runServer():
	startServer()
	handleInputs()

if __name__ == "__main__":
	runServer()