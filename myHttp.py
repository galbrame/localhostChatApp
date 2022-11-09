#-----------------------------------------
# NAME: Megan Galbraith
# STUDENT NUMBER: 6795920
# COURSE: COMP 4300
# ASSIGNMENT: assignment 1
# 
# REMARKS:  An http request parsing and response creation class, for cleaner looking
#           code. Also, some custom error codes that auto-generate http responses.
#
#-----------------------------------------


import json

#PARSES REQUESTS
class HttpRequest:
    msgType = None
    path = None
    headers = {}
    body = None

    def __init__(self, newReq):
        self.request = newReq


    def parse(self):        
        try:
            # split body from header and pop header off
            reqBody = self.request.split("\r\n\r\n" or "\n\r\n\r" or "\n\n")
            tempHeader = reqBody.pop(0)
            self.body = reqBody.pop(0) # want a string/JSON, not a list

            # split header into request type and headers
            tempHeader = tempHeader.split("\r\n" or "\n\r" or "\n")
            tempMsgType = tempHeader.pop(0)
            # turn request type into list for easier use
            tempMsgType = tempMsgType.split(" ")
            self.msgType = tempMsgType.pop(0)
            self.path = tempMsgType.pop(0)

            # turn headers into dictionary
            for pair in tempHeader:
                if pair != "": # ignore empty
                    temp = pair.split(": ")
                    self.headers[temp[0]] = temp[1]
            
            if not self.msgType or not self.path:
                raise HttpException
        
            return self.msgType, self.path, self.headers, self.body
            #let server parse the JSON body -> might not even need to do it

        except Exception:
            raise BadRequest() from None


    def getMsgType(self):
        return self.msgType

    def getHeaders(self):
        return self.headers

    def getBody(self):
        return self.body


#-------------------------------------
#BUILDS RESPONSES
class HttpResponse:
    httpResp = None
    _RESPONSE = "HTTP/1.1 {}\r\nContent-Type: {}\r\nContent-Length: {}\r\nSet-Cookie: {}\r\n\r\n{}"

    def __init__(self, status, contentType, cookie, body):
        contentLen = 0 #default
        respMsg = body
        if contentType == "application/json":
            respMsg = json.dumps(body)

        if body:
            contentLen = len(str(respMsg))
        
        self.httpResp = self._RESPONSE.format(status, contentType, contentLen, cookie, respMsg)

    def toString(self):
        return self.httpResp



#------------------------------------------
#CUSTOM EXCEPTIONS
class HttpException (Exception):
    _RESPONSE = "HTTP/1.1 {}\r\nContent-Length: {}\r\n\r\n{}"
    statusCode = None

    def __init__(self):
        super().__init__(self._RESPONSE.format(self.statusCode, 0, ""))


class NotModified(HttpException):
    statusCode = "304 Not Modified"

class BadRequest(HttpException):
    statusCode = "400 Bad Request"

class NotFound(HttpException):
    statusCode = "404 Not Found"

class ServerError(HttpException):
    statusCode = "500 Internal Server Error"
