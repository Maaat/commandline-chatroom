#File: testchatroom.py
#Author: Mathew Poff
#Description: tests the chat server and client.

import unittest
from datetime import datetime
import sqlalchemy
import sqlalchemy.orm
import threading
import select
import time

import chatserver
import chatclient

class TestServer(unittest.TestCase):

	def testConstructor(self):
		server = chatserver.ChatServer()
		self.assertEqual(str(server.db.url), "sqlite:///chatroom.db")
		self.assertIsNotNone(server.dbConn)
		self.assertEqual(server.dbMessages.fullname, "messages")
		self.assertIsNotNone(server.messageLog)
		self.assertIsNotNone(server.logfile)
		self.assertIsNotNone(server.clients)
		self.assertIsNotNone(server.clientNames)
		server.serverSocket.close()

	def testStartServer(self):
		server = chatserver.ChatServer()
		server.startServer(8080)
		self.assertEqual(server.serverSocket.getsockname(), ('0.0.0.0', 8080))
		server.serverSocket.close()

	def testMessagePersist(self):
		#create a server
		server = chatserver.ChatServer()

		#create test message
		testMessage = "test message from " + str(datetime.now())

		#broadcast the message; there are no clients so it will just be persisted to the database and log file
		server.broadcast(testMessage)

		#check the log file for the message
		log = open('log.txt','r')
		self.assertEqual(log.readlines()[-1], testMessage+'\n')
		log.close()

		#check the database for the message
		session = sqlalchemy.orm.sessionmaker(bind=server.db.engine)()
		(username, newestMessage) = session.query(server.dbMessages).all()[-1]
		self.assertEqual(newestMessage, testMessage)
		self.assertIsNone(username)

		server.serverSocket.close()

class testClient(unittest.TestCase):

	def testConstructor(self):
		client = chatclient.ChatClient()
		self.assertIsNotNone(client.serverSocket)
		client.serverSocket.close()

	def testConnectToServerFail(self):
		client = chatclient.ChatClient()

		#try to connect to a non-existent server
		try:
			client.connectToServer('localhost',9999,'Mat')

			#this line shouldn't be reachable
			self.assertTrue(False)
		except ConnectionRefusedError:
			client.serverSocket.close()

if __name__ == "__main__":
	unittest.main()