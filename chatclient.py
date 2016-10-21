#File: chatclient.py
#Author: Mathew Poff
#Description: client script to connect to and send and receive messages in a chat room.

import sys
import socket
import threading
import select

#method to wait for and handle messages from the server
def receiveLoop(connection):
	while True:
		try:
			(readable, writable, errored) = select.select([connection], [], [connection], 0.1)
			if readable or errored:
				message = connection.recv(1024).decode('utf-8')
				if message:
					print(message)
				else: break
		except: break
	print("Disconnected.")

#runs the client
def runClient(serverAddress, serverPort):

	#define server to connect to
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverAddress = (serverAddress, serverPort)

	#connect to the server
	print("Connecting to server...")
	serverSocket.connect(serverAddress)
	print("Connected.")

	#receive messages from the server in a thread separate from the user input thread
	receiveThread = threading.Thread(target=receiveLoop, args=[serverSocket])
	receiveThread.start()

	#receive user input
	while True:
		message = input()

		#exit if the user types 'exit'
		if message == 'exit':
			serverSocket.close()
			receiveThread.join()
			break
			
		#otherwise send the message to the server
		else:
			serverSocket.send(message.encode('utf-8'))

if __name__ == "__main__":
	#this script needs 2 arguments
	if(len(sys.argv) < 3) :
		print('Usage : python chatclient.py hostname port')
		sys.exit()

	runClient(sys.argv[1], int(sys.argv[2]))