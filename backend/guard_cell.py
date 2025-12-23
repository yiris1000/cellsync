import hashlib
from cell import Cell

class GuardCell(Cell):
    def __init__(self, cell_id: str, port: int, neighbors: list[int]):
        super().__init__(cell_id, port, neighbors)
        self.role = "GUARD" # Explicitly set role, though differentiation logic exists in base

    def handle_message(self, payload: dict):
        # Intercept STORE messages to check for corruption
        msg_type = payload.get('type')
        data = payload.get('data')

        if msg_type == 'STORE':
            chunk_id = data.get('id')
            chunk_data_hex = data.get('data')
            expected_hash = data.get('hash')
            
            # Verify hash
            # Note: In a real system, we'd decode hex to bytes first
            # Here we assume data is stored as hex string in the chunk object
            # But the hash was calculated on raw bytes.
            
            try:
                chunk_bytes = bytes.fromhex(chunk_data_hex)
                actual_hash = hashlib.sha256(chunk_bytes).hexdigest()
                
                if actual_hash != expected_hash:
                    print(f"🛡️  GUARD-{self.port}: ⚠️  CORRUPTION DETECTED in chunk {chunk_id}")
                    print(f"   Expected: {expected_hash[:8]}...")
                    print(f"   Actual:   {actual_hash[:8]}...")
                    self.network.broadcast(list(self.alive_neighbors), 'ALERT', f"Corruption detected in {chunk_id}")
                    return # Do not store corrupted data
                else:
                    # print(f"🛡️  GUARD-{self.port}: Chunk {chunk_id} verified...")
                    pass
            except Exception as e:
                print(f"Error verifying chunk: {e}")

        # Pass to base handler for normal processing
        super().handle_message(payload)
