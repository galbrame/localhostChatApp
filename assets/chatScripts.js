/******************************************
* NAME: Megan Galbraith
* STUDENT NUMBER: 6795920
* COURSE: COMP 4300
* ASSIGNMENT: Assignment 1
* 
* REMARKS: 
*
*******************************************/

// var WEB_SERVER
//wait...how does scope work in multiple instances of webpage? Constant overwriting?
  //I *think* this should be fine...
var WEB_SERVER = "127.0.0.1:50000"
var roomList = {}; //js object
var chatHist = {}; //js object
var myRequest; //XHR request
var myCSSRequest; //prevent namespace collision
var userName = "";
var timer = 0; //wait, how do I run web timers? Like, how check? Need fire IsModified every X seconds...



/******************************************
* buildRoomList
*
* DESCRIPTION: Build the div for adding rooms and users to the main page
******************************************/
function buildRoomList() {
    let theDiv = document.getElementById("chatRoomList");
    let innerDiv, fig, lnk, btn, figCap;

    let rooms = Object.keys(roomList);

    if (roomList.length === 0) {
        theDiv.innerText = "No chat rooms available. Please create one.";
    }
    else {
        if (theDiv.innerText !== "") {
            theDiv.innerText = "";
        }

        for (let i in rooms) {
            innerDiv = document.createElement("div");
            let att = document.createAttribute("class");
            att.value = "fig-centre";
            innerDiv.setAttributeNode(att);

            fig = document.createElement("figure");
            innerDiv.appendChild(fig);

            lnk = document.createElement("a");
            att = document.createAttribute("href");
            if (roomList[rooms[i]].length == 5) {
                att.value = "";
                let alert = document.createAttribute("onclick");
                alert.value = "alert('This room is full');";
                lnk.setAttributeNode(alert);
            }
            else {
                att.value = "./room.html";
            }
            lnk.setAttributeNode(att);
            fig.appendChild(lnk);

            btn = document.createElement("button");
            att = document.createAttribute("id");
            att.value = rooms[i];
            btn.setAttributeNode(att);
            btn.innerText = rooms[i];
            lnk.appendChild(btn);

            figCap = document.createElement("figcaption");
            //figCap.innerText = #users / 5<br>name<br<name> -> another for loop
            
            let count = roomList[rooms[i]].length;
            let innerTxt = count + " / 5";
            for (let j = 0; j < count; j++) {
                let txt = "<br>" + roomList[rooms[i]][j];
                innerTxt += txt;
            }
            figCap.innerHTML = innerTxt;

            fig.appendChild(figCap);

            theDiv.appendChild(innerDiv);
        }

    }
}



/******************************************
* GETRoomsLoadEvent
*
* DESCRIPTION: Fetch the list of rooms and current users
******************************************/
function GETRoomsLoadEvent() {
    console.log(myRequest.responseText);
    roomList = JSON.parse(myRequest.responseText);
    console.log("Received room list:");
    console.log(roomList);
    buildRoomList();
}


/******************************************
* cssLoadEvent
*
* DESCRIPTION: Fetch and load the stylesheet
******************************************/
function cssLoadEvent() {
    let css = myCSSRequest.responseText;
    let myHead = document.getElementById("head");
    myHead.innerHTML = "<style>" + css + "</style>";
}



/******************************************
* getCSS
*
* DESCRIPTION: Fetch the CSS and manually load it into the damn html
******************************************/
function getCSS() {
    myCSSRequest = new XMLHttpRequest();
    myCSSRequest.addEventListener("load", cssLoadEvent);
    myCSSRequest.open("GET", "assets/chatStyles.css");
    myCSSRequest.send()
}



/******************************************
* getListOfRooms
*
* DESCRIPTION: Fetch the list of rooms and current users
******************************************/
function getListOfRooms() {
    myRequest = new XMLHttpRequest();
    myRequest.addEventListener("load", GETRoomsLoadEvent);
    myRequest.open("GET", "/api/chatrooms");
    // if (userName != "") {
    //     myRequest.setRequestHeader('Cookie', 'userName='+userName)
    // }
    myRequest.send()
}


/******************************************
* createRoom
*
* DESCRIPTION: Creates a new chat room
* 
* PARAMETERS:
*       name: The name of the new chat room
******************************************/
function createRoom(name) {

}


/******************************************
* loadRoom
*
* DESCRIPTION: Loads all the info for the selected chat room
* 
* PARAMETERS:
*       roomName: The name of the new chat room
*       userName: The name for the user
******************************************/
//think I need to push room and user name to local storage when select room, then
//pull them out on loadRoom
//I CAN USE COOKIES!
function loadRoom(roomName, userName) {
    //send request
    
}


/******************************************
* loadHistory
*
* DESCRIPTION: Fetches the chat history for a specific chat room
******************************************/
function loadHistory(roomName) {

}





/******************************************
* sendMsg
*
* DESCRIPTION: Send a new message to the server and update the history
******************************************/
function sendMsg(userName, newMsg) {
    //time.time() kind of thing?
}


/******************************************
* checkForUpdates
*
* DESCRIPTION: Check if there have been any new messages sent in the last X seconds
******************************************/
function checkForUpdates(roomName){
    //time.time()?
}

