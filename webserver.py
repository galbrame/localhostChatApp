#!/usr/bin/python3

#-----------------------------------------
# NAME: Megan Galbraith
# STUDENT NUMBER: 6795920
# COURSE: COMP 4300
# ASSIGNMENT: assignment 1
# 
# REMARKS: Multi-threaded webserver that can serve up any text format (html, txt
#          etc.) and answers REST style API calls (although currently only
#          implements /api/chatrooms).
#
#-----------------------------------------


import socket
import threading
import sys
import os
import json
from myDatabase import *
from myHttp import * 


running = True
HOST = ""
PORT = 50000
CODES = {200: "200 OK", 201: "201 Created", 204: "204 No Content", 400: "400 Bad Request", 
            401: "401 Unauthorized", 404: "404 Not Found", 500: "500 Internal Server Error"}
TYPES = {"txt": "text/plain", "html": "text/html", "json": "application/json", 
            "jpeg": "image/jpeg", "png": "image:png"}
dbName = "chatApp" #can specify in args at runtime for testing purposes
db = None



#------------------------------------------
# readPath
#
# DESCRIPTION: Takes a path and tries to read from it. Throws a "404 not found"
#              error if the resource doesn't exist.
#
# PARAMETERS:
#       myPath: A file directory
#
# RETURNS:
#       body: Whatever was read from the path or an HTTP error
#-----------------------------------------
def readPath(myPath):
    body = ""
    searchPath = myPath
    #browser looking for index.html
    if myPath == "/":
        searchPath = "./index.html"

    elif len(myPath) > 1 and myPath[0] == "/":
        searchPath = "." + myPath

    elif myPath[0:2] != "./":
        searchPath = "./" + myPath
    
    if os.path.isfile(searchPath):
        try:
            fd = open(searchPath, "r")
            body = fd.read()
            fd.close()

        # resource found but some sort of error
        except Exception as e:
            raise ServerError

    # resource not found
    else:
        raise NotFound

    return body



#------------------------------------------
# parseAPI
#
# DESCRIPTION: Parses an API path call
#
# PARAMETERS:
#       path: an API call
#
# RETURNS:
#       parsed: a list of API path parts, minus the /api/ part
#-----------------------------------------
def parseAPI(path):
    parsed = path.split("/")
    #get rid of the /api/ part
    parsed.pop(0) 
    parsed.pop(0) 

    return parsed



#------------------------------------------
# doGET
#
# DESCRIPTION: Fulfills a response for a GET request. Something about cookie updates*******
#
# PARAMETERS:
#       path: A file directory
#       reqHeaders: A {list/dict?} of the http request headers
#
# RETURNS:
#       myResponse: An HttpResponse as a string
#-----------------------------------------
def doGET(path, reqHeaders):
    #default values
    respCode = CODES[204]
    contentType = TYPES["txt"]
    body = ""

    try:
        #API calls
        if path.find("api") > 0:
            apiPath = parseAPI(path)

            #/api/chatrooms
            if apiPath[0] == "chatrooms":
                body = db.getRoomList()
                print("Room list: ")
                print(body)

            #/api/<roomname>/update/<time>
            elif "update" in apiPath:
                body = db.checkForUpdates(apiPath[-1])
                if not body:
                    raise NotModified

            #either /api/<roomname> or will raise a 404
            else:
                roomName = apiPath[0]
                roomName = roomName.replace("%20", " ")
                body = db.getRoomMessages(roomName)

            contentType = TYPES["json"]

        #regular file fetching
        else:
            body = readPath(path)
            if body.find("<html>"):
                contentType = TYPES["html"]
            else:
                pathParts = path.split(".")
                contentType = TYPES.get(pathParts[-1])


    except HttpException:
        print("httpErr in doGET")
        raise

    if body:
        respCode = CODES[200]

    #if cookie
    #do something with headers

    myResponse = HttpResponse(respCode, contentType, "", body)

    return myResponse.toString()



#------------------------------------------
# doPOST
#
# DESCRIPTION: Responds to a POST request. Used to create new chat rooms or add
#              new messages to a chat history.
#
# PARAMETERS:
#       path: A file directory
#       reqHeaders: A {list/dict?} of the http request headers
#
# RETURNS:
#       myResponse: An HttpResponse as a string
#-----------------------------------------
def doPOST(path, reqHeaders, reqBody):
    pass



#------------------------------------------
# doUPDATE
#
# DESCRIPTION: Responds to an UPDATE request, mainly by adding a username
#              to a chat room participant list.
#
# PARAMETERS:
#       path: A file directory
#       reqHeaders: A {list/dict?} of the http request headers
#
# RETURNS:
#       myResponse: An HttpResponse as a string
#-----------------------------------------
def doUPDATE(path, reqHeaders):
    pass



#------------------------------------------
# doDELETE
#
# DESCRIPTION: Responds to a DELETE request, mainly by removing a username from
#              a chat room participant list.
#
# PARAMETERS:
#       path: A file directory
#       reqHeaders: A {list/dict?} of the http request headers
#
# RETURNS:
#       myResponse: An HttpResponse as a string
#-----------------------------------------
def doDELETE(path, reqHeaders):
    pass



#------------------------------------------
# beginThread
#
# DESCRIPTION: Threads collect and parse the client request, then form the
#              response and return it to the client.
#
# PARAMETERS:
#       conn: A TCP connection to the client
#-----------------------------------------
def beginThread(conn):
    try:
        
        myResponse = str (BadRequest)   #default setting
        #print('Connected by', addr)
        data = conn.recv(1024)

        if data:
            asText = data.decode("utf-8")
            print("Received:\n" + asText)

            newReq = HttpRequest(asText)
            msgType, path, reqHeaders, reqBody = newReq.parse()

            if msgType == "GET":
                myResponse = doGET(path, reqHeaders)
            elif msgType == "POST":
                myResponse = doPOST(path, reqHeaders, json.loads(reqBody))
            elif msgType == "UPDATE":
                myResponse = doUPDATE(path, reqHeaders)
            elif msgType == "DELETE":
                myResponse = doDELETE(path, reqHeaders)

        # just in case something goes ka-boom
        if myResponse is None:
            myResponse = str (ServerError)
        
        print("Response:\n" + myResponse)
        conn.sendall(myResponse.encode())


    except socket.timeout as e:
        print("Thread timeout happened")

    except HttpException as httpErr:
        #print(httpErr)
        print("Response:\n" + str (httpErr))
        conn.sendall(str (httpErr).encode())

    except Exception as e:
        print("Unknown exception happened")
        print(e)

    finally:
        conn.close()




#---"MAIN"---------------------------------------------------
#--  BEGIN WEBSERVER
#------------------------------------------------------------

args = sys.argv

# for testing purposes, can specify a mock database name and port
if len(args) > 1:
    args.pop(0) # toss webserver.py
    dbName = args.pop(0)
    PORT = 4000

print("server running on", socket.gethostname(), PORT)

db = sqlDB(dbName)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen()

    while running:
        try:
            conn, addr = sock.accept()
            print('Connected by', addr) #better here or in thread?
            newThread = threading.Thread(target=beginThread, args=(conn,))
            newThread.start()

        except socket.timeout as e:
            print("Socket timeout!")
        
        except KeyboardInterrupt as e:
            print("\n***SERVER EXITING***\n")
            sock.close()
            running = False
            # if this is just testing, delete the mock database
            if dbName != "chatApp":
                os.remove(dbName + ".db")
        
        except Exception as e:
            print("An unknown exception occurred")
            print(e)

sys.exit(0)