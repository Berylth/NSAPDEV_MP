# NSAPDEV_MP
NSAPDEV Machine Project: Client-server toll application written in Python, designed to simulate a network of toll booths and their interactions on a highway system. The server manages multiple toll booths, processes entry and exit transactions, and keeps track of the toll fees and vehicle movements. The client represents a toll booth and handles the vehicle entry, exit, and communication with the server.

## Pre-requisites
1) [Python](https://www.python.org/downloads/)
2) Any Code Editor such as [VSCode](https://code.visualstudio.com/)
   
## How to run
1) Download the repository via git.
   ```
   https://github.com/Berylth/NSAPDEV_MP.git
   ```
2) Configure the IP Address and Port Number of the server and client application via the *client_config.py* and *server_config.py* found at the **client** and **server** folder respectively.
3) You may also configure other settings to your liking.
4) Run the server application:
   ```
   python toll_server.py
   ```
6) Run the client application:
   ```
   python client_init.py
   ```
   
## Command list
Note that the following commands can only be run at the server-side as the client-side is primarily sending/receiving information of vehicles entering/exiting the highway.
1) gen_stats
  - Displays general system statistics like total profit, cars entered/exited, and active toll booths.
2) stats_area <area_id>
  - Shows statistics for a specific area.
3) stats_booth <area_id> <booth_id>
  - Shows statistics for a specific booth.
4) clear
  - Clears the console of its contents.
5) help
  - Displays all possible commands that can be run along with their syntax.
6) quit
  - Closes both client and server application.

## Client configurations


## Server configurations

## Members
- Garcia, Ralph Timothy D.
- Magura, Bryle Jhone R.
