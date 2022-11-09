# localhostChatApp

## About

Made for a networking assignment (and posted with permission), this project contains a web server, sqlite database, and a web-based GUI. For quicker production and to get around CORS requirements, this chat app only runs on a local machine.

The web server must be running prior to opening the GUI (index.html), as the server serves the web page itself. The GUI and server then communicate based on REST API calls.

The GUI displays the available chat rooms (two are preloaded) and their current occupants. Chat rooms are limited to five participants.


## How to Run

1. Download and unzip all of the files.
2. In a terminal, navigate to the directory containing the unzipped files.
3. Lunch the web server: ```python3 webserver.py```
4. Open a web browser (both Chrome and Firefox have been tested and work) and type ```127.0.0.1:50000``` into the address bar.
5. You should now see the chat app GUI.
[!](assets/images/GUI_screenshot.png)


## Testing

The sqlite database interface (myDatabase.py), custom http request and response handler (myHttp.py), and web server (webserver.py) are tested using the Python library unittest. Test response print order was observed to change depending on what shell the tests were run in, but the overall behaviour was always the same.

### Running Tests

1. In a terminal, navigate to the directory containing webserver.py and test_suite.py.
2. Launch the webserver in test mode by passing in a mock database name (this will also run the server on a different port so that it doesn't interfere with production mode): ```python3 webserver.py testDB```
3. In a second terminal, navigate to the same directory and launch the test suite in "verbose" mode: ```python -m unittest -v```
4. You should see test output in the terminal running test_suite.py and server request/response messages in the terminal running webserver.py.
