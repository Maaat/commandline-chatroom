#File: chatclient.py
#Author: Mathew Poff
#Description: client script to connect to and send and receive messages in a chat room.

import sys
import socket
import threading
import select

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connects to the server
def connectToServer(serverAddress, serverPort):
	print("Connecting to server...")
	serverAddress = (serverAddress, serverPort)
	serverSocket.connect(serverAddress)
	print("Connected.")

#continuously waits for and handles messages from the server
def handleServerInput():
	while True:
		try:
			(readable, writable, errored) = select.select([serverSocket], [], [serverSocket], 0.1)
			if readable or errored:
				message = serverSocket.recv(1024).decode('utf-8')
				if message:
					print(message)
				else: break
		except: break
	print("Disconnected.")

#continuously prompts for user input and then sends it to the server
def handleUserInput():
	while True:
		message = input()

		#exit if the user types 'exit'
		if message == 'exit':
			serverSocket.close()
			break
			
		#otherwise send the message to the server
		else:
			serverSocket.send(message.encode('utf-8'))

#runs the client
def runClient(serverAddress, serverPort):

	connectToServer(serverAddress, serverPort)

	#handle server and user input in separate threads
	threading.Thread(target=handleServerInput).start()
	threading.Thread(target=handleUserInput).start()

if __name__ == "__main__":
	#this script needs 2 arguments
	if(len(sys.argv) < 3) :
		print('Usage : python chatclient.py hostname port')
		sys.exit()

	runClient(sys.argv[1], int(sys.argv[2]))