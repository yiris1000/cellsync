import os
import math
import hashlib
from typing import List, Dict, Tuple

class FileManager:
    @staticmethod
    def chunk_file(filepath: str, chunk_size: int = 1024) -> List[Dict]:
        """Reads a file and splits it into chunks."""
        chunks = []
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        
        with open(filepath, 'rb') as f:
            chunk_index = 0
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                
                chunk_id = f"{filename}_{chunk_index}"
                chunk_hash = hashlib.sha256(data).hexdigest()
                
                chunks.append({
                    'id': chunk_id,
                    'index': chunk_index,
                    'filename': filename,
                    'data': data.hex(), # Encode bytes to hex for JSON serialization
                    'hash': chunk_hash,
                    'total_chunks': math.ceil(file_size / chunk_size)
                })
                chunk_index += 1
        return chunks

    @staticmethod
    def reconstruct_file(chunks: List[Dict], output_path: str):
        """Reconstructs a file from a list of chunks."""
        # Sort chunks by index
        sorted_chunks = sorted(chunks, key=lambda x: x['index'])
        
        with open(output_path, 'wb') as f:
            for chunk in sorted_chunks:
                data = bytes.fromhex(chunk['data'])
                f.write(data)

    @staticmethod
    def distribute_chunks(chunks: List[Dict], cell_ports: List[int], redundancy: int = 2) -> Dict[int, List[Dict]]:
        """Distributes chunks to cells with specified redundancy."""
        distribution = {port: [] for port in cell_ports}
        num_cells = len(cell_ports)
        
        for i, chunk in enumerate(chunks):
            # Primary holder
            primary_idx = i % num_cells
            distribution[cell_ports[primary_idx]].append(chunk)
            
            # Redundant holders
            for r in range(1, redundancy):
                replica_idx = (primary_idx + r) % num_cells
                distribution[cell_ports[replica_idx]].append(chunk)
                
        return distribution
