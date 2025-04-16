from server_config import *

import threading
import socket
import json
import struct
import os
import csv
from pathlib import Path

# For mutex of shared resources between threads
total_profit_lock = threading.Lock()
current_cars_in_highway_lock = threading.Lock()
total_cars_entered_lock = threading.Lock()
total_cars_exited_lock = threading.Lock()

# Server data
total_profit = 0.0
current_cars_in_highway = []
total_cars_entered = []
total_cars_exited = []

# List of threads for each client connected
clients = []

class ServerConnections(threading.Thread):
    def __init__(self, conn, addr):
        # Initialize necessary fields
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        
        # Toll booth data
        self.profit = 0
        self.cars_entered = []
        self.cars_exited = []
        self.area_id = -1
        self.booth_id = -1
        self.booth_type = ''

    def run(self):
        # Length-Prefixed framing for receiving data to prevent data overlap
        # due to nature of tcp being stream-oriented
        # Get message from the server by reading first 4 bytes for the length header
        raw_length = self.recv_helper(4)
        # Receive the actual message based on the length
        message_length = struct.unpack('!I', raw_length)[0]
        message_data = self.recv_helper(message_length)
        json_str = message_data.decode('utf-8')
        client_info = json.loads(json_str)
        
        # Get Toll booth data from the message
        self.area_id = client_info['area_id']
        self.booth_id = client_info['booth_id']
        self.booth_type = client_info['booth_type']

        self.receive_data()

    def recv_helper(self, n):
        # Helper function to receive n bytes of data
        data = b''
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def receive_data(self):
        while True:
            # Receive data from client (See def run() for implementation details)
            raw_length = self.recv_helper(4)
            message_length = struct.unpack('!I', raw_length)[0]
            message_data = self.recv_helper(message_length)
            json_str = message_data.decode('utf-8')
            data = json.loads(json_str)

            if data['transaction_type'] == "Entry":
                # Update toll booth information
                self.cars_entered.append(data)

                # Critical section
                with total_cars_entered_lock:
                    # Update server information
                    global total_cars_entered
                    total_cars_entered.append(data)

                # Critical section
                with current_cars_in_highway_lock:
                    # Update server information
                    global current_cars_in_highway
                    current_cars_in_highway.append(data)
            else:
                # Calculate toll fee
                fee = (self.area_id - data['entry_point_id']) * FEE_PER_ENTRY_OR_EXIT_POINT
                data['amount'] = fee
                self.profit = self.profit + fee

                # Send data to client
                encoded_message = str(fee).encode()
                length_prefix = struct.pack('!I', len(encoded_message))
                self.conn.sendall(length_prefix + encoded_message)

                # Update toll booth information
                self.cars_exited.append(data)

                # Critical section
                with total_profit_lock:
                    # Update server information
                    global total_profit
                    total_profit = total_profit + fee

                # Critical section
                with total_cars_exited_lock:
                    # Update server information
                    global total_cars_exited
                    total_cars_exited.append(data)

                # Critical section
                with current_cars_in_highway_lock:
                    for i, cars in enumerate(current_cars_in_highway):
                        if cars.get('plate_number') == data['plate_number']:
                            # Update current cars in highway list
                            current_cars_in_highway.pop(i)
                            break          

class ServerConsole(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Handle various commands to get data from the server
        while True:
            # command = input(f"{MAG}Server:\\> {RESET}")
            command = input(r"Server:\> ")
            
            # command: gen_stats
            if command == "gen_stats":
                # Display toll_server data
                print(f"{GRN}Data of the toll_server: {RESET}")
                print(f"{GRN}Total profit: {total_profit}{RESET}")
                print(f"{GRN}Current cars in the highway: {len(current_cars_in_highway)}{RESET}")
                print(f"{GRN}Total cars entered: {len(total_cars_entered)}{RESET}")
                print(f"{GRN}Total cars exited: {len(total_cars_exited)}{RESET}")
                print(f"{GRN}Total clients connected: {len(clients)}{RESET}\n")

            # if input is a bunch of whitespaces
            elif len(command.strip()) == 0:
                print("\n", end="")
                continue

            # command: stats_area <area_id>
            elif command.split()[0] == "stats_area" and len(command.split()) == 2:
                # Get area_id
                area_id = int(command.split()[1])

                # Variable to check if area_id exists
                exists = False

                # Calculate profit, cars_entered, and cars_exited of that area
                profit = 0
                cars_entered = 0
                cars_exited = 0
                for c in clients:
                    if c.area_id == area_id:
                        profit = profit + c.profit
                        cars_entered = cars_entered + len(c.cars_entered)
                        cars_exited = cars_exited + len(c.cars_exited)
                        # Set to true
                        exists = True

                if not exists:
                    # Display error message
                    print(f"{RED}Area {area_id} does not exists\n{RESET}")
                else:
                    # Display area information
                    print(f"{GRN}Data of area {area_id}{RESET}")
                    print(f"{GRN}Profit: {profit}{RESET}")
                    print(f"{GRN}Cars Entered: {cars_entered}{RESET}")
                    print(f"{GRN}Cars Exited: {cars_exited}{RESET}\n")
                    
            # command: stats_booth <area_id> <toll_booth_id>    
            elif command.split()[0] == "stats_booth" and len(command.split()) == 3:

                area_id = int(command.split()[1])
                toll_booth_id = int(command.split()[2])
                found = False

                # Find toll_booth in the list of clients (threads) given area_id and toll_booth_id
                for c in clients:
                    if c.area_id == area_id and c.booth_id == toll_booth_id:
                        # Display individual toll_booth data
                        print(f"{GRN}Data of area {area_id} booth {toll_booth_id}{RESET}")
                        print(f"{GRN}Profit: {c.profit}{RESET}")
                        print(f"{GRN}Cars Entered: {len(c.cars_entered)}{RESET}")
                        print(f"{GRN}Cars Exited: {len(c.cars_exited)}{RESET}\n")
                        found = True
                        break
                
                # Error message if toll_booth does not exist
                if not found:
                    print(f"{RED}Area {area_id} booth {toll_booth_id} not found. .  .\n{RESET}")
            
            # command: help
            elif command == "help":
                # Display all commands
                print(f"{YEL}List of Commands: {RESET}")
                print(f"{YEL}- gen_stats {RESET}")
                print(f"{YEL}- stats_area <area_id> {RESET}")
                print(f"{YEL}- stats_booth <area_id> <toll_booth_id> {RESET}")
                print(f"{YEL}- help {RESET}")
                print(f"{YEL}- clear {RESET}")
                print(f"{YEL}- quit {RESET}\n")

            # command: clear
            elif command == "clear":
                # Clear screen console
                os.system('cls' if os.name == 'nt' else 'clear')
                print(BANNER)

            # command : quit
            elif command == "quit":
                # Save all data to csv
                self.save_to_csv()

                # Message one of the clients to quit
                for c in clients:
                    if c.booth_type == "Entry":
                        message = "quit"
                        enocded_message = message.encode()
                        length_prefix = struct.pack('!I', len(enocded_message))
                        c.conn.sendall(length_prefix + enocded_message)
                        break
                # Exit process
                print(f"{CYN}Exiting. . .\n{RESET}")
                os._exit(1)
            else:
                print(f"{RED}Command not recognized. . . Try the \"help\" command\n{RESET}")

    def save_to_csv(self):
        global total_cars_entered
        global total_cars_exited
        global current_cars_in_highway

        if len(total_cars_entered) == 0 or len(total_cars_exited) == 0:
            return

        # Check if output dir exists
        if OUTPUT_DIR != "" and not Path(OUTPUT_DIR).is_dir(): # os.path.isdir("my_folder")
            Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True) # os.makedirs(OUTPUT_DIR)

        # Get path of the output csv
        output_csv1 = Path(OUTPUT_DIR) / "current_cars_in_highway.csv"
        output_csv2 = Path(OUTPUT_DIR) / "total_cars_entered.csv"
        output_csv3 = Path(OUTPUT_DIR) / "total_cars_exited.csv"

        # Critical section (ensure data integrity)
        with current_cars_in_highway_lock, total_cars_entered_lock, total_cars_exited_lock:

            # Create csv1 which contains data for current cars in highway
            print(f"{CYN}Creating csv for current cars in highway. . .{RESET}")
            with open(output_csv1, "w", newline="") as csvfile:
                # Get keys
                if len(current_cars_in_highway) != 0:
                    fieldnames = current_cars_in_highway[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Write data to csv
                    writer.writeheader()
                    writer.writerows(current_cars_in_highway)
            print(f"{CYN}DONE{RESET}")

            # Create csv2 which contains data for total cars entered in highway
            print(f"{CYN}Creating csv for total cars entered in highway. . .{RESET}")
            with open(output_csv2, "w", newline="") as csvfile:
                # Get keys
                fieldnames = total_cars_entered[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write data to csv
                writer.writeheader()
                writer.writerows(total_cars_entered)
            print(f"{CYN}DONE{RESET}")

            # Create csv3 which contains data for total cars exited in highway
            print(f"{CYN}Creating csv for total cars exited in highway. . .{RESET}")
            with open(output_csv3, "w", newline="") as csvfile:
                # Get keys
                fieldnames = total_cars_exited[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write data to csv
                writer.writeheader()
                writer.writerows(total_cars_exited)    
            print(f"{CYN}DONE{RESET}") 

        message_directory = "current directory" if OUTPUT_DIR == "" else OUTPUT_DIR
        print(f"{CYN}Data has been saved, check {message_directory} for more details. . .{RESET}")

def main():
    # Create socket
    print(BANNER)
    print(f"{YEL}\nStarting the server. . . {RESET}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind socket
    print(f"{YEL}Binding socket to port {SERVER_PORT}{RESET}")
    server_socket.bind((SERVER_ADDR, SERVER_PORT))

    # Socket listening at the assigned port
    print(f"{YEL}Listening to port {SERVER_PORT}. . .{RESET}\n")
    server_socket.listen()

    # Start Server Console here
    ServerConsole().start()

    while True:
        # Accept incoming connections and run it as a seperate thread
        conn, addr = server_socket.accept()
        client = ServerConnections(conn, addr)
        clients.append(client)
        client.start()

if __name__ == "__main__":
    main()