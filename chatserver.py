import socket
import select

#set of connected clients
clients = set();

def handleMessage(message):
	print(message)
	for client in clients:
		client.send(('>'+message).encode('utf-8'))

#set up the listening socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8080))
server.listen(10)
print("The server has started.")

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
				if message == 'exit':
					raise ConnectionResetError()
				print(">" + message)
				handleMessage(message)

			#or the connection has been closed
			except ConnectionResetError:
				handleMessage("A client disconnected.")
				clients.remove(connection)