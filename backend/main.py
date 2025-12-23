from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from manager import manager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CellSync API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    port: Optional[int] = None

class ChatRequest(BaseModel):
    message: str

@app.get("/status")
def get_status():
    return manager.get_status()

@app.post("/start")
def start_cluster():
    manager.start_cluster()
    return {"message": "Cluster started"}

@app.post("/stop")
def stop_cluster():
    manager.stop_cluster()
    return {"message": "Cluster stopped"}

@app.post("/kill/{port}")
def kill_cell(port: int):
    manager.kill_cell(port)
    return {"message": f"Cell {port} killed"}

@app.post("/revive/{port}")
def revive_cell(port: int):
    manager.revive_cell(port)
    return {"message": f"Cell {port} revived"}

@app.get("/logs")
def get_logs():
    return {"logs": manager.get_logs()}

@app.post("/agent/chat")
def agent_chat(req: ChatRequest):
    from agent import agent
    result = agent.process_query(req.message)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
