from client_config import *

import socket
import threading
import time
import random
import string
import datetime
import json
import struct
import os
import queue

# List of toll booth threads initialized
toll_booths = []

class TollBooth(threading.Thread):
    def __init__(self, booth_id, area_id, booth_type):
        # Initialize necessary fields and socket
        threading.Thread.__init__(self)
        self.booth_id = booth_id
        self.area_id = area_id
        self.booth_type = booth_type
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TOLL_SERVER_HOST, TOLL_SERVER_PORT))
        self.vehicle_queue = queue.Queue()

    def run(self):
        # Send client details to server
        toll_booth_details = {
            "area_id": self.area_id,
            "booth_id": self.booth_id,
            "booth_type": self.booth_type
        }
        # Length-Prefixed framing for receiving data to prevent data overlap
        # due to nature of tcp being stream-oriented
        json_str = json.dumps(toll_booth_details).encode()
        # Pack the length of the json_str as a 4 byte uint
        length_prefix = struct.pack('!I', len(json_str))
        self.socket.sendall(length_prefix + json_str)
        
        if self.booth_type == "Entry":
            # Send entry data and check if server disconnects
            t1 = threading.Thread(target=self.send_entry_data)
            t2 = threading.Thread(target = self.listen_for_notifications)
            t1.start()
            t2.start()

            t1.join()
            t2.join()
        elif self.booth_type == "Exit":
            # Send exit data
            self.send_exit_data()
        else:
            # Send entry and exit data
            t1 = threading.Thread(target=self.send_entry_data)
            t2 = threading.Thread(target=self.send_exit_data)
            t1.start()
            t2.start()

            t1.join()
            t2.join()

    def listen_for_notifications(self):
        while True:
            # Get message from the server by reading first 4 bytes for the length header
            raw_length = self.recv_helper(4)
            message_length = struct.unpack('!I', raw_length)[0]
            # Receive the actual message based on the length
            message_data = self.recv_helper(message_length)
            message = message_data.decode('utf-8')

            # Close the application
            if message == "quit":
                os._exit(1)

    
    def recv_helper(self, n):
        # Helper function to receive n bytes of data
        data = b''
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    def send_exit_data(self):
        while True:
            # Get data of vehicle exiting the highway
            vehicle_data = self.vehicle_queue.get()

            if not vehicle_data:
                continue
            
            # Simulate vehicle travelling
            time.sleep((self.area_id - vehicle_data['entry_point_id']) * VEHICLE_SPEED_MULTIPLIER)
            
            # Generate exit data of vehicle
            exit_data = {
                "plate_number": vehicle_data['plate_number'],
                "timestamp": self.get_current_time(),
                "entry_point_id": vehicle_data['entry_point_id'],
                "exit_point_id": self.area_id,
                "booth_id": self.booth_id,
                "amount": -1,
                "transaction_type": "Exit"
            }
            
            # Send exit_data to server
            json_str = json.dumps(exit_data).encode()
            length_prefix = struct.pack('!I', len(json_str))
            self.socket.sendall(length_prefix + json_str)

            # Get message from the server by reading first 4 bytes for the length header
            raw_length = self.recv_helper(4)
            message_length = struct.unpack('!I', raw_length)[0]
            # Receive the actual message based on the length
            message_data = self.recv_helper(message_length)
            exit_data['amount'] = message_data.decode('utf-8')

            type = exit_data['transaction_type']
            timestamp = exit_data['timestamp']
            vehicle = exit_data['plate_number']
            exit_point = exit_data['exit_point_id']
            exit_booth = exit_data['booth_id']
            amount = exit_data['amount']

            print(f"{YEL} [{type} - {timestamp}] {vehicle} at Exit {exit_point} booth {exit_booth} with Payment {amount} dollars {RESET}")

            

    def send_entry_data(self):
        while True:
            # Generate random data of vehicle entering the highway
            entry_data = {
                "plate_number": self.generate_plate_num(),
                "timestamp": self.get_current_time(),
                "entry_point_id": self.area_id,
                "booth_id": self.booth_id,
                "transaction_type": "Entry"
            }

            vehicle = entry_data['plate_number']
            type = entry_data['transaction_type']
            entry_point = entry_data['entry_point_id']
            entry_booth = entry_data["booth_id"]
            timesteamp = entry_data['timestamp']

            # Send data to server using Length-Prefixed framing (see comment in def run())
            json_str = json.dumps(entry_data).encode()
            length_prefix = struct.pack('!I', len(json_str))
            self.socket.sendall(length_prefix + json_str)

            print(f"{GRN} [{type} - {timesteamp}] {vehicle} at Entry {entry_point} booth {entry_booth} {RESET}")

            # Send vehicle data to other toll booths to simulate the vehicle exiting highway
            exit_point_id = random.randint(self.area_id + 1, TOTAL_ENTRY_EXIT_POINTS)
            max_booth_id = BOOTH_COUNT_TOLL_PLAZA if exit_point_id == TOTAL_ENTRY_EXIT_POINTS else BOOTH_COUNT_REGULAR
            booth_id = random.randint(1, max_booth_id)
            
            for booth in toll_booths:
                if booth.booth_id == booth_id and booth.area_id == exit_point_id:
                    booth.vehicle_queue.put(entry_data)
                    break

            # Sleep at random intervals to simulate cars entering the highway
            time.sleep(random.uniform(ENTRY_INTERVAL_MIN, ENTRY_INTERVAL_MAX))
    
    def generate_plate_num(self):
        # Generate 4 random uppercase letters
        letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

        # Generate a 4 digit random number
        number = ''.join(random.choices(string.digits, k = 4))

        return f"{letters}-{number}"
    
    def get_current_time(self):
        # Get current time in YYYY-MM-DD HH:MM:SS format
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")