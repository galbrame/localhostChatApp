#!/usr/bin/python3

#-----------------------------------------
# NAME: Megan Galbraith
# STUDENT NUMBER: 6795920
# COURSE: COMP 4300
# ASSIGNMENT: Assignment 1
# 
# REMARKS: The testing suite used to test the functionality of the webserver,
#          myHttp classes, and myDatabase class.
#
#-----------------------------------------

import unittest
import socket
import time
import json
from myHttp import *
from myDatabase import *


#------------------------------------------
# Test the classes in myHttp.py
#------------------------------------------
class httpClassTests(unittest.TestCase):

    _REQUEST = "{} {} HTTP/1.1\r\nContent-Length: {}\r\n\r\n{}"


    #------------------------------------------
    def test_request_parse(self):
        rType = "GET"
        rPath = "/path/resource"
        rBody = ""
        rLen = len(rBody)
        req = self._REQUEST.format(rType, rPath, rLen, rBody)
        
        print("\nTesting http request parsing")
        
        testRequest = HttpRequest(req)
        msgType, path, headers, body = testRequest.parse()

        self.assertEqual(msgType, rType)
        self.assertEqual(path, rPath)
        self.assertEqual(int (headers.get("Content-Length")), rLen)
        self.assertEqual(body, rBody)


    #------------------------------------------
    def test_create_reponse(self):
        status = "200 OK"
        contentType = "text/html"
        cookie = "myCookie=userName"
        body = "<html><body><p>This is a webpage</p></body></html>"

        print("\nTesting http response creation")

        testReponse = HttpResponse(status, contentType, cookie, body)
        testReponse = testReponse.toString()

        self.assertTrue(testReponse.find(status) > 0)
        self.assertTrue(testReponse.find(contentType) > 0)
        self.assertTrue(testReponse.find(cookie) > 0)
        self.assertTrue(testReponse.find(body) > 0)


#------------------------------------------
# Test the classes in myDatabase.py
#------------------------------------------
class databaseTests(unittest.TestCase):
    db = None

    #------------------------------------------
    def setUp(self):
        self.db = sqlDB("test")


    #------------------------------------------
    def tearDown(self):
        self.db.destroyDB()
        self.db = None


    #------------------------------------------
    def test_create_room(self):
        newRoom = "Cookie Club"

        print("Testing database: create new room")

        self.db.createRoom(newRoom)


    #------------------------------------------
    def test_add_user_to_room(self):
        room = "Ponies"
        newUser = "Stacey's mom"

        print("Testing database: add user to room")

        self.db.addParticipant(room, newUser)

    
    #------------------------------------------
    def test_remove_user_from_room(self):
        room = "Ponies"
        user = "Nancy"

        print("Testing database: remove user from room")

        self.db.removeParticipant(room, user)

    
    #------------------------------------------
    def test_get_room_list(self):
        print("Testing database: get list of rooms, with current users")

        roomList = self.db.getRoomList()

        self.assertEqual(len(roomList), 2)
        self.assertEqual(len(roomList["Sports Fans"]), 5)
        self.assertEqual(len(roomList["Ponies"]), 2)


    #------------------------------------------
    def test_get_room_chat_history(self):
        #from database initialization data
        historyData = [('Nancy', 1, 'Omg! I love ponies SOOOOOOOO MUCH'),
                        ('Nancy', 2, 'Like. SO much. <3'),
                        ('Drew', 3, 'No way! *I* love ponies SO much!'),
                        ('Nancy', 4, 'We should 100% be best friends'),
                        ('Drew', 5, '100%')]
        
        print("Testing database: get chat history for a room")

        messages = self.db.getRoomMessages("Ponies")
        messages = list(messages.values())

        for i in range(len(messages)):
            self.assertEqual(messages[i]["username"], historyData[i][0])
            self.assertEqual(messages[i]["msg"], historyData[i][2])


    #------------------------------------------
    def test_add_message(self):
        room = "Sports Fans"
        user = "Super Dave"
        newMsg = "Helloooooooo sports fans!!!"
        t = time.time()
        
        print("Testing database: add a message")

        msgConfirm = self.db.addNewMsg((room, user, t, newMsg))

        self.assertEqual(room, msgConfirm["roomName"])
        self.assertEqual(user, msgConfirm["userName"])
        self.assertEqual(newMsg, msgConfirm["msg"])


    #------------------------------------------
    def test_check_updates(self):
        data = [("Ponies", "Nancy", 10.10, "This is the newest message!"),
                ("Ponies", "Drew", 11.11, "No, THIS IS!!!")]
        prevMsgTime = 5.5

        print("Testing database: check for updates")

        #add message to chats
        for d in data:
            self.db.addNewMsg(d)
        
        #check vs last timestamp
        update = self.db.checkForUpdates("Ponies", prevMsgTime)
        update = list(update.values())

        self.assertEqual(len(update), 2)

        for i in range(len(update)):
            self.assertEqual(update[i]["username"], data[i][1])
            self.assertEqual(update[i]["msg"], data[i][3])






#------------------------------------------
# Test the classes in webserver.py
# NOTE: webserver must be running on the same machine before launching test
#       suite
#------------------------------------------
class webserverTests(unittest.TestCase):
    _HOST = '127.0.0.1'
    _PORT = 4000
    _REQUEST = "{} {} HTTP/1.1\r\nCookie: {}\r\nContent-Length: {}\r\n\r\n{}"
    serConn = None


    #------------------------------------------
    def setUp(self):

        self.serConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serConn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serConn.connect((self._HOST, self._PORT))
        #prevents the tests from hanging if the webserver gets hung up
        self.serConn.settimeout(5)



    #------------------------------------------
    def tearDown(self):
        self.serConn.close()


    
    #------------------------------------------
    def parseResponse(self, response):
        respHeaders = {}
        
        # split body from header and pop header off
        respBody = response.split("\r\n\r\n" or "\n\r\n\r" or "\n\n")
        tempHeader = respBody.pop(0)
        
        #check if there even is a body before trying to pop it
        if respBody:
            respBody = respBody.pop(0) # want a string/JSON, not a list
        else:
            respBody = {}

        # split header into message status and headers
        tempHeader = tempHeader.split("\r\n" or "\n\r" or "\n")
        
        #get status code
        statusList = tempHeader.pop(0)
        print(statusList)
        statusList = statusList.split(" ")
        print(statusList)
        status = statusList[1]
        
        # turn headers into dictionary
        for pair in tempHeader:
            if pair != "": # ignore empty
                temp = pair.split(": ")
                respHeaders[temp[0]] = temp[1]
    
        return status, respHeaders, respBody



    #------------------------------------------
    def test_bad_request(self):
        testReq = "This is not a proper HTTP request"
        print("\nTesting 400 Bad Request server response")

        self.serConn.sendall(testReq.encode())
        testResp = self.serConn.recv(1024)
        theResp = testResp.decode("utf-8")

        status, respHeaders, respBody = self.parseResponse(theResp)

        #self.assertTrue(theResp.find("400 Bad Request") > 0)
        self.assertEqual(status, "400")

    

    #------------------------------------------
    def test_request_webpage(self):
        msgType = "GET"
        path = "index.html"
        cookie = "username"
        msgLen = 0
        body = ""
        testCompare = ""

        print("\nTesting GET html")
        testReq = self._REQUEST.format(msgType, path, cookie, msgLen, body)

        self.serConn.sendall(testReq.encode())
        testResp = self.serConn.recv(4096)
        theResp = testResp.decode("utf-8")

        status, respHeaders, respBody = self.parseResponse(theResp)

        try:
            respBody = json.loads(respBody)
        except json.JSONDecodeError as jde:
            print(jde)

        try:
            fd = open(path, "r")
            testCompare = fd.read()
            fd.close()
        except FileNotFoundError as e:
            print("index.html must be located in same directory as testing suite to run this test")

        #self.assertTrue(theResp.find(testCompare) > 0)
        self.assertEqual(testCompare, respBody)



    #------------------------------------------
    #def test_request_image(self):



    #this is kinda just the same test as get_html...
    #------------------------------------------
    def test_request_file(self):
        msgType = "GET"
        path = "./someText.txt"
        cookie = "username"
        msgLen = 0
        body = ""
        testCompare = ""

        print("\nTesting GET a file")
        testReq = self._REQUEST.format(msgType, path, cookie, msgLen, body)

        self.serConn.sendall(testReq.encode())
        testResp = self.serConn.recv(1024)
        theResp = testResp.decode("utf-8")

        status, respHeaders, respBody = self.parseResponse(theResp)

        try:
            respBody = json.loads(respBody)
        except json.JSONDecodeError as jde:
            print(jde)

        try:
            fd = open(path, "r")
            testCompare = fd.read()
            fd.close()
        except FileNotFoundError as e:
            print("someText.txt must be located in same directory as testing suite to run this test")

        #self.assertTrue(theResp.find(testCompare) > 0)
        self.assertEqual(testCompare, respBody)



    #------------------------------------------
    def test_request_doesnt_exist(self):
        msgType = "GET"
        path = "foo.txt"
        cookie = "username"
        msgLen = 0
        body = ""
        testCompare = "404 Not Found"

        print("\nTesting 404 File Not Found webserver response")
        testReq = self._REQUEST.format(msgType, path, cookie, msgLen, body)

        self.serConn.sendall(testReq.encode())
        testResp = self.serConn.recv(1024)
        theResp = testResp.decode("utf-8")

        self.assertTrue(theResp.find(testCompare) > 0)


    
    #------------------------------------------
    #def test_post_message(self):



    #------------------------------------------
    #def test_request_not_modified(self):



    #------------------------------------------
    def test_get_room_list(self):
        msgType = "GET"
        path = "/api/chatrooms"
        cookie = "username"
        msgLen = 0
        body = ""
        testCompare = {"Sports Fans": ["Cam", "Lucy", "Holden", "Aisha", "Kabir"],
                        "Ponies": ["Nancy", "Drew"]}

        print("\nTesting GET /api/chatrooms for list of chatrooms and current users")
        testReq = self._REQUEST.format(msgType, path, cookie, msgLen, body)
        print("The request: \n" + testReq)

        self.serConn.sendall(testReq.encode())
        testResp = self.serConn.recv(1024)
        theResp = testResp.decode("utf-8")
        print("The response: " + theResp)

        status, respHeaders, respBody = self.parseResponse(theResp)

        try:
            respBody = json.loads(respBody)
        except json.JSONDecodeError as jde:
            print(jde)

        self.assertEqual(respBody, testCompare)



    #------------------------------------------
    #def test_create_room
    

    
    #------------------------------------------
    def test_get_chat_history(self):
        msgType = "GET"
        path = "/api/Ponies"
        cookie = "username"
        msgLen = 0
        body = ""
        #from database initialization data
        testCompare = [('Nancy', 1, 'Omg! I love ponies SOOOOOOOO MUCH'),
                        ('Nancy', 2, 'Like. SO much. <3'),
                        ('Drew', 3, 'No way! *I* love ponies SO much!'),
                        ('Nancy', 4, 'We should 100% be best friends'),
                        ('Drew', 5, '100%')]
        
        print("Testing /api/<room_name> to get chat history for a room")

        testReq = self._REQUEST.format(msgType, path, cookie, msgLen, body)
        print("The request: \n" + testReq)

        self.serConn.sendall(testReq.encode())
        testResp = self.serConn.recv(1024)
        theResp = testResp.decode("utf-8")
        print("The response: " + theResp)

        status, respHeaders, respBody = self.parseResponse(theResp)

        try:
            respBody = json.loads(respBody)
        except json.JSONDecodeError as jde:
            print(jde)

        messages = list(respBody.values())

        for i in range(len(messages)):
            self.assertEqual(messages[i]["username"], testCompare[i][0])
            self.assertEqual(messages[i]["msg"], testCompare[i][2])



    #------------------------------------------
    #def test_get_chat_updates(self):






#------------------------------------------
#
#------------------------------------------
if __name__ == '__main__':
    unittest.main()