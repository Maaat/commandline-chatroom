#File: testchatroom.py
#Author: Mathew Poff
#Description: tests the chat server and client.

import unittest
from datetime import datetime

import chatserver
import chatclient

class testServer(unittest.TestCase):

	def testStartServer(self):
		chatserver.startServer()
		self.assertEqual(chatserver.server.getsockname(), ('0.0.0.0', 8080))
		chatserver.server.close()

	def testHandleMessage(self):
		testMessage = "test message from " + str(datetime.now())
		chatserver.handleMessage(testMessage)
		log = open('log.txt','r')
		self.assertEqual(log.readlines()[-1], '>'+testMessage+'\n')
		log.close()

class testClient(unittest.TestCase):

	def testConnectToServer(self):
		#try to connect to a non-existent server
		try:
			chatclient.connectToServer('localhost',9999)
		except ConnectionRefusedError:
			True

if __name__ == "__main__":
	unittest.main()