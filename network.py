import socket
import json
import threading
from typing import Any, Tuple, Optional

class UDPNetwork:
    def __init__(self, port: int, buffer_size: int = 4096):
        self.port = port
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', port))
        self.running = True

    def send_message(self, target_port: int, message_type: str, data: Any = None):
        """Send a JSON message to a target port on localhost."""
        payload = {
            'type': message_type,
            'sender_port': self.port,
            'data': data
        }
        try:
            message_bytes = json.dumps(payload).encode('utf-8')
            self.socket.sendto(message_bytes, ('localhost', target_port))
        except Exception as e:
            print(f"Error sending message to {target_port}: {e}")

    def broadcast(self, target_ports: list[int], message_type: str, data: Any = None):
        """Send a message to multiple ports."""
        for port in target_ports:
            if port != self.port:
                self.send_message(port, message_type, data)

    def receive_message(self) -> Optional[Tuple[dict, tuple]]:
        """Blocking receive. Returns (payload_dict, address_tuple)."""
        if not self.running:
            return None
        try:
            data, addr = self.socket.recvfrom(self.buffer_size)
            payload = json.loads(data.decode('utf-8'))
            return payload, addr
        except socket.error:
            return None
        except json.JSONDecodeError:
            print(f"Received invalid JSON")
            return None

    def close(self):
        self.running = False
        self.socket.close()
