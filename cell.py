import time
import threading
import random
import hashlib
import os
import json
from typing import Dict, List, Set, Optional
from network import UDPNetwork
from colorama import init, Fore, Style

init(autoreset=True)

class Cell:
    def __init__(self, cell_id: str, port: int, neighbors: List[int]):
        self.cell_id = cell_id
        self.port = port
        self.neighbors = neighbors
        self.network = UDPNetwork(port)
        
        # Persistence
        self.storage_dir = f"storage_{port}"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Storage (Metadata in RAM, Data on Disk)
        self.chunks: Dict[str, str] = {} # chunk_id -> hex_data (Cache/Index)
        self.chunk_metadata: Dict[str, dict] = {} # chunk_id -> metadata
        
        self.load_from_disk()
        
        # State
        self.alive_neighbors: Set[int] = set(neighbors)
        self.blacklist: Set[int] = set() # Nodes to ignore (Isolation)
        self.last_heartbeat: Dict[int, float] = {n: time.time() for n in neighbors}
        self.running = True
        self.role = "STEM"
        self.start_time = time.time()
        
        # Threads
        self.threads = []

    def load_from_disk(self):
        """Load existing chunks from disk on startup."""
        if os.path.exists(self.storage_dir):
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.storage_dir, filename), 'r') as f:
                            data = json.load(f)
                            chunk_id = data.get('id')
                            self.chunks[chunk_id] = data.get('data')
                            self.chunk_metadata[chunk_id] = data
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")

    def start(self):
        """Start all cell processes."""
        print(f"{Fore.GREEN}🟢 Cell-{self.port} STARTED as {self.role}{Style.RESET_ALL}")
        
        t_listen = threading.Thread(target=self.listen_loop)
        t_heartbeat = threading.Thread(target=self.heartbeat_loop)
        t_check_dead = threading.Thread(target=self.check_dead_neighbors_loop)
        t_differentiate = threading.Thread(target=self.differentiation_loop)
        
        self.threads = [t_listen, t_heartbeat, t_check_dead, t_differentiate]
        for t in self.threads:
            t.daemon = True
            t.start()
            
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.network.close()
        print(f"{Fore.RED}🔴 Cell-{self.port} STOPPED{Style.RESET_ALL}")

    def listen_loop(self):
        """Listen for incoming messages."""
        while self.running:
            msg = self.network.receive_message()
            if msg:
                payload, addr = msg
                self.handle_message(payload)

    def handle_message(self, payload: dict):
        msg_type = payload.get('type')
        sender = payload.get('sender_port')
        data = payload.get('data')

        # ISOLATION LOGIC: Ignore blacklisted nodes
        if sender in self.blacklist:
            return

        if msg_type == 'HEARTBEAT':
            self.last_heartbeat[sender] = time.time()
            self.alive_neighbors.add(sender)
            
        elif msg_type == 'STORE':
            chunk_id = data.get('id')
            
            # GUARD LOGIC: Check for corruption if we are a GUARD
            if self.role == "GUARD":
                chunk_data_hex = data.get('data')
                expected_hash = data.get('hash')
                try:
                    chunk_bytes = bytes.fromhex(chunk_data_hex)
                    actual_hash = hashlib.sha256(chunk_bytes).hexdigest()
                    actual_hash = hashlib.sha256(chunk_bytes).hexdigest()
                    if actual_hash != expected_hash:
                        print(f"{Fore.MAGENTA}🛡️  GUARD-{self.port}: {Fore.RED}⚠️  CORRUPTION DETECTED from Cell-{sender}{Style.RESET_ALL}")
                        # Broadcast alert to isolate the sender
                        self.network.broadcast(list(self.alive_neighbors), 'ALERT', {'culprit': sender, 'chunk': chunk_id})
                        return # Reject storage
                except Exception as e:
                    print(f"Error verifying chunk: {e}")

            self.chunks[chunk_id] = data.get('data')
            self.chunk_metadata[chunk_id] = data
            
            # PERSISTENCE: Save to disk
            with open(os.path.join(self.storage_dir, f"{chunk_id}.json"), 'w') as f:
                json.dump(data, f)
            
            # print(f"💾 Cell-{self.port} stored chunk {chunk_id}")
            
        elif msg_type == 'REQUEST':
            chunk_id = data.get('chunk_id')
            requestor = data.get('requestor_port')
            if chunk_id in self.chunks:
                self.network.send_message(requestor, 'STORE', self.chunk_metadata[chunk_id])
                
        elif msg_type == 'REPLICATE':
            # A neighbor died, we need to check if we hold chunks that need replication
            # For simplicity in this demo, if we receive a REPLICATE request, 
            # we broadcast our chunks to the sender so they can restore redundancy
            # In a real system, this would be more targeted.
            target_port = sender
            for chunk_data in self.chunk_metadata.values():
                self.network.send_message(target_port, 'STORE', chunk_data)
                
        elif msg_type == 'ALERT':
            culprit = data.get('culprit')
            if culprit and culprit not in self.blacklist:
                self.blacklist.add(culprit)
                print(f"{Fore.RED}🚫 Cell-{self.port} ISOLATING Cell-{culprit} (Reason: Corruption){Style.RESET_ALL}")
                
        elif msg_type == 'SABOTAGE':
            print(f"{Fore.BLUE}- Cell-{self.port} Installing Firmware Update v2.0...{Style.RESET_ALL}")
            time.sleep(1)
            # Simulate a bug: Corrupt our own data
            if self.chunks:
                target_id = list(self.chunks.keys())[0]
                self.chunks[target_id] = "deadbeef" * 10
                print(f"{Fore.YELLOW}⚠️  Cell-{self.port} UPDATE FAILED: Memory Corruption Detected!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}- Cell-{self.port} BUG ACTIVATED: Broadcasting corrupted data...{Style.RESET_ALL}")
                # Trigger a sync so the network notices
                self.network.broadcast(list(self.alive_neighbors), 'STORE', self.chunk_metadata[target_id])

    def heartbeat_loop(self):
        """Send heartbeats to neighbors."""
        while self.running:
            self.network.broadcast(self.neighbors, 'HEARTBEAT')
            time.sleep(2)

    def check_dead_neighbors_loop(self):
        """Check for dead neighbors."""
        while self.running:
            time.sleep(3)
            now = time.time()
            dead_nodes = []
            
            for neighbor in list(self.alive_neighbors):
                if now - self.last_heartbeat.get(neighbor, 0) > 6: # 3 missed heartbeats (2s interval)
                    print(f"{Fore.YELLOW}⚠️  Cell-{self.port} detected DEAD neighbor: {neighbor}{Style.RESET_ALL}")
                    dead_nodes.append(neighbor)
            
            for dead in dead_nodes:
                self.alive_neighbors.remove(dead)
                self.trigger_healing(dead)

    def trigger_healing(self, dead_node: int):
        """Trigger healing process when a node dies."""
        # Ask surviving neighbors to send their chunks so we can ensure redundancy
        # In this simple demo, we ask everyone to send us what they have, 
        # and we store it if we don't have it (increasing redundancy count effectively)
        print(f"{Fore.CYAN}- Cell-{self.port} initiating healing for Node {dead_node}...{Style.RESET_ALL}")
        self.network.broadcast(list(self.alive_neighbors), 'REPLICATE')

    def differentiation_loop(self):
        """Differentiate role after 10 seconds."""
        time.sleep(10)
        if self.role == "STEM":
            # Simple logic: Lowest port becomes GUARD, others STORAGE
            # In a real distributed system, this would be a consensus algorithm
            # Here we just use the sorted list of neighbors + self
            all_nodes = sorted(self.neighbors + [self.port])
            if self.port == all_nodes[-1]: # Highest port is GUARD (arbitrary choice)
                self.role = "GUARD"
            else:
                self.role = "STORAGE"
            
            print(f"{Fore.BLUE}- Cell-{self.port} differentiated into {self.role}{Style.RESET_ALL}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python cell.py <port> <neighbor_port1> <neighbor_port2> ...")
        sys.exit(1)
        
    port = int(sys.argv[1])
    neighbors = [int(p) for p in sys.argv[2:]]
    
    cell = Cell(f"cell-{port}", port, neighbors)
    cell.start()