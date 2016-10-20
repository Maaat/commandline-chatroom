import socket
import threading
import select

def receiveLoop(connection):
	while True:
		if exiting:
			print("Disconnected.")
			return
		(readable, writable, errored) = select.select([connection], [], [connection], 0.1)
		if readable or errored:
			message = connection.recv(1024).decode('utf-8')
			if message:
				print(message)
			else:
				print("Disconnected.")

exiting = False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddress = ('127.0.0.1',8080)

print("Connecting to server...")
server.connect(serverAddress)
print("Connected.")

threading.Thread(target=receiveLoop, args=[server]).start()

while True:
	message = input()
	if message == 'exit':
		exiting = True
		break
	else:
		server.send(message.encode('utf-8'))