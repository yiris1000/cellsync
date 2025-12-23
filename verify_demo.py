import subprocess
import sys
import time
import os
import signal
import shutil
from file_manager import FileManager
from network import UDPNetwork
from colorama import init, Fore, Style

init(autoreset=True)

# Configuration
ALL_PORTS = [5000, 5001, 5002, 5003]
running_cells = {}

def start_cell(port):
    neighbors = [p for p in ALL_PORTS if p != port]
    args = [sys.executable, "cell.py", str(port)] + [str(n) for n in neighbors]
    p = subprocess.Popen(args)
    running_cells[port] = p
    print(f"   Spawned Cell-{port} (PID: {p.pid})")

def start_cluster():
    for port in ALL_PORTS:
        if os.path.exists(f"storage_{port}"):
            shutil.rmtree(f"storage_{port}")
    print(f"{Fore.CYAN}🚀 Launching CellSync Cluster...{Style.RESET_ALL}")
    for port in ALL_PORTS:
        start_cell(port)
        time.sleep(0.5)
    print(f"{Fore.GREEN}- Cluster active.\n{Style.RESET_ALL}")

def stop_cluster():
    print(f"\n{Fore.RED}🛑 Shutting down cluster...{Style.RESET_ALL}")
    for p in running_cells.values():
        p.terminate()
    print(f"{Fore.GREEN}- All cells stopped.{Style.RESET_ALL}")

def demo_upload(filepath):
    print(f"\n{Fore.YELLOW}- Uploading {filepath}...{Style.RESET_ALL}")
    chunks = FileManager.chunk_file(filepath)
    dist = FileManager.distribute_chunks(chunks, ALL_PORTS)
    net = UDPNetwork(4999) 
    for port, cell_chunks in dist.items():
        for chunk in cell_chunks:
            net.send_message(port, 'STORE', chunk)
            time.sleep(0.05) 
    print(f"{Fore.GREEN}- File distributed across {len(ALL_PORTS)} cells.{Style.RESET_ALL}")
    net.close()

def main():
    with open("demo_test.txt", "w") as f:
        f.write("This is a test file for CellSync. " * 50)
    
    try:
        start_cluster()
        time.sleep(10) # Wait for differentiation
        
        print(f"\n{Fore.WHITE}[AUTO] Uploading File{Style.RESET_ALL}")
        demo_upload("demo_test.txt")
        
        print(f"\n{Fore.WHITE}[AUTO] Killing Cell-5001{Style.RESET_ALL}")
        p = running_cells[5001]
        p.terminate()
        del running_cells[5001]
        
        time.sleep(5)
        
        print(f"\n{Fore.WHITE}[AUTO] Reviving Cell-5001 (Persistence){Style.RESET_ALL}")
        start_cell(5001)
        
        time.sleep(5)
        
        print(f"\n{Fore.WHITE}[AUTO] Testing Live Bug (Isolation){Style.RESET_ALL}")
        net = UDPNetwork(4999)
        net.send_message(5000, 'SABOTAGE', {}) # Sabotage Cell 5000
        net.close()
        
        time.sleep(5)
        print(f"\n{Fore.GREEN}[AUTO] Finished{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        pass
    finally:
        stop_cluster()

if __name__ == "__main__":
    main()
