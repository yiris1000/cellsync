import sys
import time
import random
from network import UDPNetwork
from file_manager import FileManager
from colorama import init, Fore, Style

init(autoreset=True)

PORTS = [5000, 5001, 5002, 5003]

def attack(filepath="demo_test.txt"):
    print(f"{Fore.RED}----------------HACKER TOOL INITIALIZED----------------{Style.RESET_ALL}")
    print(f"Targeting Cluster on Ports: {PORTS}")
    
    try:
        # 1. Load the real file to get valid IDs (so the attack looks legit)
        chunks = FileManager.chunk_file(filepath)
        if not chunks:
            print("Error: Could not load target file.")
            return

        # 2. Create a malicious payload (Corrupted Chunk)
        target_chunk = chunks[0]
        original_data = target_chunk['data']
        
        # Malicious modification
        target_chunk['data'] = "DEADBEEF" * 100 # Obvious garbage
        chunk_id = target_chunk['id']
        
        print(f"\n{Fore.YELLOW}- Crafting Malicious Payload...{Style.RESET_ALL}")
        print(f"   Target Chunk: {chunk_id}")
        print(f"   Original Data (First 20 chars): {original_data[:20]}...")
        print(f"   Injected Data: {target_chunk['data'][:20]}...")
        
        # 3. Send to the network
        net = UDPNetwork(4999) # Hacker uses port 4999
        
        print(f"\n{Fore.RED}- LAUNCHING ATTACK...{Style.RESET_ALL}")
        for port in PORTS:
            print(f"   -> Injecting into Cell-{port}...")
            net.send_message(port, 'STORE', target_chunk)
            time.sleep(0.1)
            
        net.close()
        print(f"\n{Fore.GREEN}- Attack Complete. Check the main terminal for the system's reaction.{Style.RESET_ALL}")

    except FileNotFoundError:
        print(f"{Fore.RED}Error: {filepath} not found. Make sure you uploaded it in the main terminal first.{Style.RESET_ALL}")

if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else "demo_test.txt"
    attack(target_file)
