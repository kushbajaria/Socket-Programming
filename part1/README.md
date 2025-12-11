# Server and Client Local Socket Programming
## Group Members
1. Kush Bajaria (bajariakush@csu.fullerton.edu)
2. Joshua Yee (joshuayee@csu.fullerton.edu)
3. Randolph Brummett (rbrummett@csu.fullerton.edu)
4. Ric Escalante (rescalante12@csu.fullerton.edu)
5. Amir Valiulla (amir.valiulla@csu.fullerton.edu)

## Programming Language
- Python

## How to Execute
1. Open a terminal and start the server in the project directory:

   python3 socket_programming_server.py

2. In another terminal (same machine), run the client:

   python3 socket_programming_client.py

3. Use commands at the client prompt:
   - ls                : list files in server's current directory (uses data connection)
   - get <filename>    : download file from server
   - put <filename>    : upload file to server (client must have the file)
   - quit              : close connection and exit

## Expected Results
- Expected server results: ![alt text](server.png)
- Expected client results: ![alt text](client.png)

## Remarks
- Congrats, if you have reached this far, you have sucessfully ran the local server and client sockets.