# About CellSync 🧬

## Inspiration
The internet is fragile. We rely on centralized giants for everything—banking, healthcare, communication. But as we've seen with recent events like the massive **Cloudflare outage**, when one central node fails, it takes half the world with it.

We asked ourselves: **"What if files could survive like living cells?"**

In biology, there is no "master server." If a cell dies, its neighbors detect the loss and replicate to heal the wound. If a virus enters, the immune system isolates it. We wanted to bring this biological resilience to digital storage.

## What it does
**CellSync** is a biological, distributed file system where data lives in independent "cells" rather than a central server.

*   **Self-Healing:** If a node (cell) crashes, neighbors detect the missing heartbeat and automatically replicate lost data to new cells.
*   **Immune System:** Specialized "Guard Cells" actively hunt for corruption. If they detect a hash mismatch (a "virus"), they alert the network to isolate the infected node.
*   **Differentiation:** Nodes start as generic "Stem Cells" and evolve into Storage or Guard roles based on the network's needs.

## How we built it
We built CellSync using **Python** to leverage its rich ecosystem for rapid prototyping.

### 1. The "Cell" Architecture
Each node is an independent process running the `Cell` class. We used **threading** to handle multiple biological functions simultaneously:
*   `listen_loop`: The "ears" of the cell, listening for UDP messages.
*   `heartbeat_loop`: The "pulse," broadcasting liveness to neighbors every 2 seconds.
*   `check_dead_neighbors_loop`: The "senses," detecting when a neighbor has gone silent.

### 2. Networking
We chose **UDP (User Datagram Protocol)** for communication. Unlike TCP, UDP is connectionless and lightweight, allowing our cells to "shout" messages (heartbeats, alerts) to neighbors without establishing a formal handshake—mimicking the fast, chemical signaling between biological cells.

### 3. The "Immune System" Algorithm
We implemented a distributed consensus mechanism for threat detection. When a Guard Cell receives a chunk, it verifies the data against a SHA-256 hash:

$$ H(data) \stackrel{?}{=} \text{expected\_hash} $$

If the check fails, the Guard broadcasts an `ALERT` packet. Other cells receive this and add the culprit's port to a `blacklist`, effectively cutting it off from the network—a digital quarantine.

## Challenges we ran into
*   **The "Split-Brain" Problem:** In a distributed system, it's hard to tell if a node is dead or just slow. We had to tune our heartbeat timeouts carefully ($T_{timeout} > 3 \times T_{heartbeat}$) to avoid false positives where the network would try to "heal" a healthy but laggy node.
*   **Concurrency Hell:** Managing shared state (like the `chunks` dictionary) across multiple threads (listener, heartbeat, chaos monkey) led to race conditions. We had to be very disciplined about how threads accessed shared memory.
*   **Visualizing the Invisible:** Backend systems are boring to watch. We spent significant time using `colorama` to build a real-time CLI dashboard so users could *see* the biology in action—green for healing, red for death, magenta for corruption.

## Accomplishments that we're proud of
*   **The "Chaos Monkey" Demo:** We successfully built a demo where we can randomly kill processes and inject corrupted data in real-time, and the system actually survives. Watching the terminal light up as cells "heal" the network is incredibly satisfying.
*   **Biological Accuracy:** We didn't just use biology as a buzzword; we actually implemented concepts like **differentiation** (nodes changing roles) and **apoptosis** (programmed cell death/isolation) in code.
*   **Zero Dependencies:** Aside from `colorama` for the UI, the core networking and logic are built with standard Python libraries, proving you don't need heavy frameworks to build distributed systems.

## What we learned
*   **Biology is a great teacher:** Concepts like "stem cell differentiation" map surprisingly well to "dynamic load balancing" in computer science.
*   **UDP is chaotic:** We learned why TCP exists! Packets get lost, arrive out of order, or get duplicated. Building a reliable system on top of an unreliable protocol was a crash course in network engineering.
*   **Resilience > Efficiency:** Our system replicates data aggressively. It's not the most storage-efficient way to save a file, but it is incredibly hard to kill. Sometimes, survival is more important than optimization.

## What's next for cellsync
*   **True Networking:** Moving from localhost ports to actual IP addresses to run across different physical machines in a LAN.
*   **Evolutionary Algorithms:** Implementing a genetic algorithm where cells optimize their own storage parameters (replication rate, heartbeat interval) over time based on network conditions.
*   **Cell Walls (Encryption):** Adding a layer of encryption to data chunks so that even if a cell is compromised, the data inside remains protected.
