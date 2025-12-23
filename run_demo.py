import sys
import time
import os
import signal
import shutil
import random
import threading
import subprocess
from file_manager import FileManager
from network import UDPNetwork
from colorama import init, Fore, Style

init(autoreset=True)

# Configuration
ALL_PORTS = [5000, 5001, 5002, 5003]
running_cells = {} # port -> process

def start_cell(port):
    neighbors = [p for p in ALL_PORTS if p != port]
    args = [sys.executable, "cell.py", str(port)] + [str(n) for n in neighbors]
    p = subprocess.Popen(args)
    running_cells[port] = p
    print(f"   Spawned Cell-{port} (PID: {p.pid})")

def start_cluster():
    # Cleanup old storage
    for port in ALL_PORTS:
        if os.path.exists(f"storage_{port}"):
            shutil.rmtree(f"storage_{port}")

    print(f"{Fore.CYAN}- Launching CellSync Cluster...{Style.RESET_ALL}")
    for port in ALL_PORTS:
        start_cell(port)
        time.sleep(0.5)
    print(f"{Fore.GREEN}- Cluster active...\n{Style.RESET_ALL}")

def stop_cluster():
    print(f"\n{Fore.RED}🛑 Shutting down cluster...{Style.RESET_ALL}")
    for p in running_cells.values():
        p.terminate()
    print(f"{Fore.GREEN}--------All cells stopped--------{Style.RESET_ALL}")

def demo_upload(filepath):
    print(f"\n{Fore.YELLOW}📤 Uploading {filepath}...{Style.RESET_ALL}")
    chunks = FileManager.chunk_file(filepath)
    # Distribute to currently running cells
    active_ports = list(running_cells.keys())
    if not active_ports:
        print(f"{Fore.RED}❌ No active cells to upload to!{Style.RESET_ALL}")
        return

    dist = FileManager.distribute_chunks(chunks, active_ports)
    
    net = UDPNetwork(4999) 
    
    for port, cell_chunks in dist.items():
        for chunk in cell_chunks:
            net.send_message(port, 'STORE', chunk)
            time.sleep(0.05) 
            
    print(f"{Fore.GREEN}- File distributed across {len(active_ports)} cells.{Style.RESET_ALL}")
    net.close()

def kill_random_cell():
    if not running_cells:
        return
    port = random.choice(list(running_cells.keys()))
    p = running_cells[port]
    print(f"\n{Fore.RED}- CHAOS: Killing Cell-{port} (PID: {p.pid})...{Style.RESET_ALL}")
    p.terminate()
    del running_cells[port]

def revive_random_cell():
    dead_ports = [p for p in ALL_PORTS if p not in running_cells]
    if not dead_ports:
        return
    port = random.choice(dead_ports)
    print(f"\n{Fore.GREEN}✨ CHAOS: Reviving Cell-{port}...{Style.RESET_ALL}")
    start_cell(port)

def corrupt_random_chunk(filepath):
    print(f"\n{Fore.MAGENTA}- CHAOS: Injecting CORRUPTED data...{Style.RESET_ALL}")
    chunks = FileManager.chunk_file(filepath)
    bad_chunk = chunks[0]
    bad_chunk['data'] = "deadbeef" * 10 
    
    net = UDPNetwork(4999)
    active_ports = list(running_cells.keys())
    if active_ports:
        target = random.choice(active_ports)
        net.send_message(target, 'STORE', bad_chunk)
    net.close()

def sabotage_random_cell():
    active_ports = list(running_cells.keys())
    if not active_ports:
        return
    target = random.choice(active_ports)
    print(f"\n{Fore.YELLOW}- INJECTING BUG into Cell-{target}...{Style.RESET_ALL}")
    
    net = UDPNetwork(4999)
    net.send_message(target, 'SABOTAGE', {})
    net.close()

def chaos_loop(filepath):
    print(f"\n{Fore.RED} CHAOS MODE ENGAGED {Style.RESET_ALL}")
    print("The system will now randomly kill, revive, and attack cells.")
    print("Press Ctrl+C to stop.\n")
    
    while True:
        time.sleep(random.randint(3, 6))
        action = random.choice(['kill', 'revive', 'corrupt', 'nothing'])
        
        if action == 'kill':
            kill_random_cell()
        elif action == 'revive':
            revive_random_cell()
        elif action == 'corrupt':
            corrupt_random_chunk(filepath)
        
        # Ensure at least 2 cells are always running so the network survives
        if len(running_cells) < 2:
            revive_random_cell()

def main():
    # Create dummy file
    with open("demo_test.txt", "w") as f:
        f.write("This is a test file for CellSync. " * 50)
    
    try:
        start_cluster()
        
        print(f"\n{Fore.CYAN}- Waiting 10s for differentiation...{Style.RESET_ALL}")
        time.sleep(10)
        
        print(f"\n{Fore.WHITE}[PRESS ENTER] to Upload File{Style.RESET_ALL}")
        input()
        demo_upload("demo_test.txt")
        
        print(f"\n{Fore.CYAN}Choose Mode:{Style.RESET_ALL}")
        print("1. Interactive (Manual Kill/Corrupt)")
        print("2. Chaos Monkey (Auto Random Destruction)")
        print("3. Live Bug Simulation (Isolation Demo)")
        choice = input("Enter 1, 2, or 3: ")
        
        if choice == '2':
            chaos_loop("demo_test.txt")
        elif choice == '3':
             # Bug Demo
            print(f"\n{Fore.WHITE}[PRESS ENTER] to Inject Bug into a Cell{Style.RESET_ALL}")
            input()
            sabotage_random_cell()
            print(f"\n{Fore.CYAN}- Watch as the Guard detects it and others ISOLATE the buggy cell...{Style.RESET_ALL}")
            input(f"\n{Fore.WHITE}[PRESS ENTER] to Finish{Style.RESET_ALL}")
        else:
            # Interactive Mode (Legacy)
            print(f"\n{Fore.WHITE}[PRESS ENTER] to Kill a Random Cell{Style.RESET_ALL}")
            input()
            kill_random_cell()
            
            print(f"\n{Fore.CYAN}- Watch healing...{Style.RESET_ALL}")
            
            print(f"\n{Fore.WHITE}[PRESS ENTER] to Revive it (Persistence Demo){Style.RESET_ALL}")
            input()
            revive_random_cell()
            
            print(f"\n{Fore.WHITE}[PRESS ENTER] to Test Corruption{Style.RESET_ALL}")
            input()
            corrupt_random_chunk("demo_test.txt")
            
            print(f"\n{Fore.WHITE}[PRESS ENTER] to Finish{Style.RESET_ALL}")
            input()

    except KeyboardInterrupt:
        pass
    finally:
        stop_cluster()

if __name__ == "__main__":
    main()
