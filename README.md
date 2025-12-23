# CellSync 🧬
**A Biological, Self-Healing Distributed File System**

> "What if files could survive like living cells - distributed, self-replicating, and unkillable?"

## The Problem
The internet runs on single points of failure. Recent outages (like Cloudflare's) take down banking, government services, and major platforms for millions of users. Individual developers lose work to corrupted drives. We rely on centralized systems that are fragile by design.

## The Solution
**CellSync** is a distributed file system inspired by biology. Instead of a central server, data lives across independent "cells" that mimic living organisms:
*   **Survival**: Cells detect when a neighbor dies and automatically replicate data to heal the network.
*   **Adaptation**: Cells start as "Stem Cells" and differentiate into specialized roles (Storage, Guard) based on network needs.
*   **Immunity**: "Guard Cells" act as an immune system, detecting corrupted data and alerting the network to reject it.

## Key Features

### 1. Biological Self-Healing 
If a cell process is killed (simulating a server crash), neighboring cells detect the missing heartbeats. They immediately communicate to replicate the lost data chunks to other survivors, restoring redundancy without human intervention.

### 2. Stem Cell Differentiation 
There is no "master" node. All cells launch as generic **Stem Cells**. After a brief initialization period, they self-organize:
*   **Storage Cells**: Hold file chunks and handle replication.
*   **Guard Cells**: Perform integrity checks and monitor for threats.

### 3. Immune System (Threat Detection) 
Guard cells actively validate data integrity. If a corrupted chunk (e.g., from a hacker or bit rot) is introduced, the Guard detects the hash mismatch and broadcasts an **ALERT**, causing other cells to quarantine the threat.

## Architecture

*   **Language**: Python 3.10+
*   **Communication**: UDP (User Datagram Protocol) for fast, peer-to-peer messaging.
*   **Architecture**: Decentralized, Shared-Nothing.
*   **Visuals**: `colorama` for real-time terminal visualization.

## Quick Start

### Prerequisites
*   Python 3.x
*   `colorama`

### Installation
```bash
pip install -r requirements.txt
```

### Running the Demo
We've built a CLI demo to showcase the biological behaviors in real-time.

```bash
python run_demo.py
```

**The Demo Flow:**
1.  **Genesis**: 4 Stem Cells are spawned.
2.  **Differentiation**: Watch them evolve into Storage and Guard cells.
3.  **Upload**: A file is chunked and distributed across the organism.
4.  **Attack**: The script kills a cell. **Watch the system heal.**
5.  **Corruption**: The script injects bad data. **Watch the immune system react.**

##  Project Structure

*   `cell.py`: The core agent logic (Heartbeat, Storage, Differentiation).
*   `network.py`: Low-level UDP communication layer.
*   `file_manager.py`: Handles file chunking and reconstruction.
*   `run_demo.py`: Orchestration script for the live demonstration.

---
*Built for Major League Hacking*
