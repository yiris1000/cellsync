import subprocess
import sys
import os
import time
import signal
import shutil
import random
import threading
from typing import Dict, List, Optional, Any

# Configuration
ALL_PORTS = [5000, 5001, 5002, 5003]

class CellManager:
    def __init__(self):
        self.running_cells: Dict[int, subprocess.Popen] = {}
        self.logs: List[str] = []
        self.log_lock = threading.Lock()

    def _log(self, message: str):
        with self.log_lock:
            timestamp = time.strftime("%H:%M:%S")
            self.logs.append(f"[{timestamp}] {message}")
            # Keep only last 1000 logs
            if len(self.logs) > 1000:
                self.logs.pop(0)

    def get_logs(self) -> List[str]:
        with self.log_lock:
            return list(self.logs)

    def start_cell(self, port: int):
        if port in self.running_cells:
            self._log(f"Cell-{port} is already running.")
            return

        neighbors = [p for p in ALL_PORTS if p != port]
        # We run cell.py from the current directory (backend/)
        cwd = os.path.dirname(os.path.abspath(__file__))
        
        args = [sys.executable, "cell.py", str(port)] + [str(n) for n in neighbors]
        
        # Capture output for logging
        p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        self.running_cells[port] = p
        self._log(f"Spawned Cell-{port} (PID: {p.pid})")

        # Start monitoring thread
        def monitor_output(proc, p_port):
            for line in iter(proc.stdout.readline, b''):
                msg = line.decode().strip()
                if msg:
                    self._log(f"[Cell-{p_port}] {msg}")
            proc.stdout.close()

        t = threading.Thread(target=monitor_output, args=(p, port))
        t.daemon = True
        t.start()

    def start_cluster(self):
        self._log("Launching CellSync Cluster...")
        # Cleanup old storage
        cwd = os.path.dirname(os.path.abspath(__file__))
        for port in ALL_PORTS:
            storage_path = os.path.join(cwd, f"storage_{port}")
            if os.path.exists(storage_path):
                shutil.rmtree(storage_path)

        for port in ALL_PORTS:
            self.start_cell(port)
            time.sleep(0.5)
        self._log("Cluster active.")

    def stop_cluster(self):
        self._log("Shutting down cluster...")
        for port, p in list(self.running_cells.items()):
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()
        self.running_cells.clear()
        self._log("All cells stopped.")

    def kill_cell(self, port: int):
        if port in self.running_cells:
            p = self.running_cells[port]
            self._log(f"CHAOS: Killing Cell-{port} (PID: {p.pid})...")
            p.terminate()
            del self.running_cells[port]
        else:
            self._log(f"Cell-{port} is not running.")

    def revive_cell(self, port: int):
        if port not in self.running_cells:
            self._log(f"CHAOS: Reviving Cell-{port}...")
            self.start_cell(port)
        else:
            self._log(f"Cell-{port} is already alive.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "active_ports": list(self.running_cells.keys()),
            "total_ports": ALL_PORTS
        }

# Global instance
manager = CellManager()
