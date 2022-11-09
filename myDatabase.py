#!/usr/bin/python3

#-----------------------------------------
# NAME: Megan Galbraith
# STUDENT NUMBER: 6795920
# COURSE: COMP 4300
# ASSIGNMENT: assignment 1
# 
# REMARKS:  The database class, for the storing of chat rooms
#           and chat messages.
#
#-----------------------------------------


import sqlite3
import os


class sqlDB:
    dbName = ""

    def __init__(self, name):
        self.dbName = name + ".db"
        
        sqlConn = sqlite3.connect(self.dbName)
        cursor = sqlConn.cursor()
        print("\nConnected to database")

        #initialize the db if it doesn't already exist
        result = cursor.execute("SELECT name FROM sqlite_master")
        if result.fetchone() is None:
            self.createTables(cursor, sqlConn)
            self.addStartupData(cursor, sqlConn)

        sqlConn.close()

    
    #------------------------------------------
    # openDB
    #
    # DESCRIPTION: Helper method to establish a connection and cursor with
    #              the database. closeDB() MUST be called after transaction is
    #              committed.
    #
    # RETURNS:
    #       sqlConn: the connection to a database, necessary for closing.
    #       cursor: a sqlite cursor object       
    #-----------------------------------------
    def openDB(self):
        sqlConn = sqlite3.connect(self.dbName)
        cursor = sqlConn.cursor()

        return sqlConn, cursor


    #------------------------------------------
    # closeDB
    #
    # DESCRIPTION: Helper method to close the database connection. Just makes
    #              the code more clear in conjunction with openDB().
    #
    # PARAMETERS:
    #       sqlConn: the open connection to the sqLite3 database
    #-----------------------------------------
    def closeDB(self, sqlConn):
        sqlConn.close()


    #------------------------------------------
    # createTables
    #
    # DESCRIPTION: Create the rooms and chat messages tables when the
    #              database is initiated. 
    #
    # PARAMETERS:
    #       cursor: a sqlite cursor object       
    #-----------------------------------------
    def createTables(self, cursor, sqlConn):
        roomsTable = """CREATE TABLE rooms (
            roomName VARCHAR(50),
            userName VARCHAR(30)
        )"""

        chatsTable = """CREATE TABLE chats (
            roomName VARCHAR(50), 
            userName VARCHAR(30),
            timestamp FLOAT,
            msg TEXT
        )"""

        cursor.execute(roomsTable)
        sqlConn.commit()
        cursor.execute(chatsTable)
        sqlConn.commit()

    
    #------------------------------------------
    # addStartupData
    #
    # DESCRIPTION: Creates some rooms, adds some users and a chat history
    #              to the new database.
    #
    # PARAMETERS:
    #       cursor: a sqlite cursor object       
    #       sqlConn: a connection to the database object
    #-----------------------------------------
    def addStartupData(self, cursor, sqlConn):
        addRooms = [('Sports Fans',), ('Ponies',)]
        addUsers = [('Sports Fans', 'Cam'), ('Sports Fans', 'Lucy'), ('Sports Fans', 'Holden'),
                    ('Sports Fans', 'Aisha'), ('Sports Fans', 'Kabir'), ('Ponies', 'Nancy'), 
                    ('Ponies', 'Drew')]
        historyData = [('Ponies', 'Nancy', 1.1, 'Omg! I love ponies SOOOOOOOO MUCH'),
                        ('Ponies', 'Nancy', 2.2, 'Like. SO much. <3'),
                        ('Ponies', 'Drew', 3.3, 'No way! *I* love ponies SO much!'),
                        ('Ponies', 'Nancy', 4.4, 'We should 100% be best friends'),
                        ('Ponies', 'Drew', 5.5, '100%')]
        addHistory = "INSERT INTO chats VALUES(?, ?, ?, ?)"

        cursor.executemany("INSERT INTO rooms(roomName) VALUES(?)", addRooms)
        sqlConn.commit()
        cursor.executemany("INSERT INTO rooms VALUES(?, ?)", addUsers)
        sqlConn.commit()
        cursor.executemany(addHistory, historyData)
        sqlConn.commit()


    #------------------------------------------
    # createRoom
    #
    # DESCRIPTION: Create a new room as specified by the user. Raises an
    #              exception if the room was not created succefully.
    #
    # PARAMETERS:
    #       roomname: The name of the new room.
    #-----------------------------------------
    def createRoom(self, name):
        cmd = "INSERT INTO rooms(roomName) VALUES(?)"

        sqlConn, cursor = self.openDB()
        cursor.execute(cmd, (name,))
        sqlConn.commit()

        #verify
        result = cursor.execute("SELECT roomName FROM rooms WHERE roomName=?", (name,))
        roomNames = result.fetchone()
        self.closeDB(sqlConn)

        if name not in roomNames:
            raise DBError



    #------------------------------------------
    # getRoomList
    #
    # DESCRIPTION: Fetch the list of room names, with list of current
    #              participants for each room.
    #
    # RETURNS:
    #       roomList: a dictionary of "room": [users, ]
    #-----------------------------------------
    def getRoomList(self):
        cmd = "SELECT * FROM rooms"
        roomList = {}

        sqlConn, cursor = self.openDB()
        exe = cursor.execute(cmd)
        result = exe.fetchall()
        self.closeDB(sqlConn)

        if result is None:
            raise DBError

        #convert tuples into dictionary of rooms with lists of users
        for row in result:
            if roomList.get(row[0]) is None:
                roomList.update({row[0]: []})
            else:
                roomList[row[0]].append(row[1])
        print(roomList)
        return roomList


    #------------------------------------------
    # getRoomMessages
    #
    # DESCRIPTION: Fetch the chat history for a specific chat room.
    #
    # PARAMETERS:
    #       room: The name of the room
    #
    # RETURNS:
    #       result: A nested dictionary of timestamp: {username, msg}
    #-----------------------------------------
    def getRoomMessages(self, room):
        cmd = "SELECT * FROM chats WHERE roomName=? ORDER BY timestamp"
        history = {}

        sqlConn, cursor = self.openDB()
        exe = cursor.execute(cmd, (room,))
        result = exe.fetchall()
        self.closeDB(sqlConn)

        if result is None:
            raise DBError

        #convert query result into timestamp dictionary of user messages
        history = self.convertChatsToDict(result)

        return history


    #------------------------------------------
    # addParticipant
    #
    # DESCRIPTION: Add a participant to a room. Raises an exception if the
    #              participant list was not succesfully updated.
    #
    # PARAMETERS:
    #       room: The chat room the user is in
    #       user: The user to add to the room
    #-----------------------------------------
    def addParticipant(self, room, user):
        cmd = "INSERT INTO rooms VALUES(?, ?)"

        sqlConn, cursor = self.openDB()
        exe = cursor.execute(cmd, (room, user))
        sqlConn.commit()

        #verify
        exe = cursor.execute("SELECT userName FROM rooms WHERE roomName=? AND userName=?", (room, user))
        userName = exe.fetchone()
        self.closeDB(sqlConn)

        if user not in userName:
            raise DBError


    #------------------------------------------
    # removeParticipant
    #
    # DESCRIPTION: Remove a participant from the chat room. Raises an exception
    #              if not successful.
    #
    # PARAMETERS:
    #       room: The chat room the user is in
    #       user: The user to add to the room
    #-----------------------------------------
    def removeParticipant(self, room, user):
        cmd = "DELETE FROM rooms WHERE roomName=? AND userName=?"

        sqlConn, cursor = self.openDB()
        exe = cursor.execute(cmd, (room, user))
        sqlConn.commit()
        
        #verify
        exe = cursor.execute("SELECT userName FROM rooms WHERE roomName=? AND userName=?", (room, user))
        userName = exe.fetchone()
        self.closeDB(sqlConn)

        if userName is not None:
            raise DBError


    
    #------------------------------------------
    # addMsg
    #
    # DESCRIPTION: Add a new message to a specific chat room. Raises an
    #              exception if not successful.
    #
    # PARAMETERS:
    #       msgInfo: a tuple of (roomName, userName, timestamp, message)
    #
    # RETURNS:
    #       result: a tuple of the successful addition, in the same order
    #-----------------------------------------
    def addNewMsg(self, msgInfo):
        cmd = "INSERT INTO chats VALUES(?, ?, ?, ?)"

        sqlConn, cursor = self.openDB()
        cursor.execute(cmd, msgInfo)
        sqlConn.commit()

        #verify
        exe = cursor.execute("SELECT * FROM chats WHERE timestamp=?", (msgInfo[2],))
        result = exe.fetchone()
        self.closeDB(sqlConn)


        for i in range(4):
            if result[i] != msgInfo[i]:
                raise DBError

        ans = {"roomName": result[0],
                "userName": result[1],
                "timestamp": result[2],
                "msg": result[3]}
        
        return ans


    #------------------------------------------
    # checkForUpdates
    #
    # DESCRIPTION: Return any new messages from a specified timestamp.
    #
    # PARAMETERS:
    #       room: The name of the chat room
    #       lastTime: The time of the last message received
    # 
    # RETURNS:
    #       updates: a nested dictionary of any messages new to the user
    #-----------------------------------------
    def checkForUpdates(self, room, lastTime):
        NUM_COL = 4
        cmd = "SELECT * FROM chats WHERE roomName=? AND timestamp>?"
        updates = {}

        sqlConn, cursor = self.openDB()
        exe = cursor.execute(cmd, (room, lastTime))
        result = exe.fetchall()
        self.closeDB(sqlConn)


        #make sure we're always passing a list of tuples to convertChatsToDict
        if len(result) == NUM_COL:
            result = [result,]

        if result is not None:
            updates = self.convertChatsToDict(result)

        return updates



    #------------------------------------------
    # convertMsgDict
    #
    # DESCRIPTION: Convert a sql query result into a nested dictionary in the
    #              format of timestamp: {user, msg}.
    #
    # PARAMETERS:
    #       result: a "chats" table query result
    # 
    # RETURNS:
    #       updates: a nested dictionary of any messages new to the user
    #-----------------------------------------    
    def convertChatsToDict(self, result):
        theDict = {}
        
        for row in result:
            theDict.update({row[2]: {"username": row[1], "msg": row[3]}})

        return theDict



    #------------------------------------------
    # destroyDB
    #
    # DESCRIPTION: For testing situations, delete the test database once done
    #-----------------------------------------
    def destroyDB(self):
        os.remove(self.dbName)




# Custom exception for easier debugging
class DBError(Exception):

    def __init__(self):
        super().__init__("The database failed to execute a command")