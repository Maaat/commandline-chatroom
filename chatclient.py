#File: chatclient.py
#Author: Mathew Poff
#Description: client script to connect to and send and receive messages in a chat room.

import sys
import socket
import threading
import select

class ChatClient():

	#constructor
	def __init__(self):
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#connects to the server
	def connectToServer(self, serverAddress, serverPort, username):
		print("Connecting to server...")
		serverAddress = (serverAddress, serverPort)
		self.serverSocket.connect(serverAddress)
		self.serverSocket.send(("/name:"+username).encode('utf-8'))
		print("Connected.")

	#continuously waits for and handles messages from the server
	def handleServerInput(self):
		while True:
			try:
				(readable, writable, errored) = select.select([self.serverSocket], [], [self.serverSocket], 0.1)
				if readable or errored:
					message = self.serverSocket.recv(1024).decode('utf-8')
					if message:
						print(message)
					else: break
			except: break
		print("Disconnected.")

	#continuously prompts for user input and then sends it to the server
	def handleUserInput(self):
		while True:
			message = input()

			#exit if the user types 'exit'
			if message == 'exit':
				self.serverSocket.close()
				break
				
			#otherwise send the message to the server
			else:
				self.serverSocket.send(message.encode('utf-8'))

	#runs the client
	def runClient(self, serverAddress, serverPort):
		username = input("Enter your name:")
		self.connectToServer(serverAddress, serverPort, username)

		#handle server and user input in separate threads
		threading.Thread(target=self.handleServerInput).start()
		threading.Thread(target=self.handleUserInput).start()

#entry point
if __name__ == "__main__":
	#new ChatClient
	client = ChatClient()

	#this script needs 1 argument
	if(len(sys.argv) < 2) :
		print('Usage : python chatclient.py hostname')
		sys.exit()

	client.runClient(sys.argv[1], 8080)