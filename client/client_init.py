from toll_booth import TollBooth, toll_booths
from client_config import *
        
def main():
    # Create 18 entry or exit points
    for i in range(1, TOTAL_ENTRY_EXIT_POINTS + 1):
        
        # For first and last entry points, create 6 toll booths (default)
        if i == 1 or i == TOTAL_ENTRY_EXIT_POINTS:
            type = "Entry" if i == 1 else "Exit"

            for j in range(1, BOOTH_COUNT_TOLL_PLAZA + 1):
                t = TollBooth(j, i, type)
                toll_booths.append(t)
                
        # For other entry points, create 4 toll booths (default)
        else:
            type = "Entry/Exit"
            for j in range(1, BOOTH_COUNT_REGULAR + 1):
                t = TollBooth(j, i, type)
                toll_booths.append(t)

    for t in toll_booths:
        t.start()      

    for t in toll_booths:
        t.join()

if __name__ == "__main__":
    main()