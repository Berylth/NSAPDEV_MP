# NSAPDEV_MP: Toll Server and Client Application
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
     - Saves all data to csv files and closes  both client and server application.

## Client configurations
*Server Information*
- TOLL_SERVER_HOST: String representing the IP Address of the Toll Server application.
- TOLL_SERVER_PORT: Integer representing the Port Number of the Toll Server application.

*Toll Booth Setup*
- TOTAL_ENTRY_EXIT_POINTS: Positive integer representing the total number of entry/exit points in the highway system.
- BOOTH_COUNT_TOLL_PLAZA: Positive integer representing the bumber of booths at a toll plaza (located at the first and last entry/exit points).
- BOOTH_COUNT_REGULAR: Positive integer representing the number of booths at each regular entry/exit point.

*Car Generation*
- ENTRY_INTERVAL_MIN: Positive floating number representing the minimum interval (in seconds) between vehicle generation at entry booths.
- ENTRY_INTERVAL_MAX: Positive floating number representing the maximum interval (in seconds) between vehicle generation at entry booths.
- VEHICLE_SPEED_MULTIPLIER: Positive floating number representing the multiplier to simulate vehicle travel time between entry and exit points.

## Server configurations
*Server Information*
- SERVER_ADDR: String representing the IP Address of the Toll Server application.
- SERVER_PORT: Integer representing the Port Number of the Toll Server application.

*Toll fee*
- FEE_PER_ENTRY_OR_EXIT_POINT: Positive integer representing the toll fee charged per entry/exit point crossed.

*Output Directory*
- OUTPUT_DIR: String representing the directory where CSV files (logs) will be saved when the server is terminated. Leave empty to save in the current directory.

## Members
- Garcia, Ralph Timothy D.
- Magura, Bryle Jhone R.
