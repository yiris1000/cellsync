import os
import google.generativeai as genai
from typing import List, Dict
import json
from manager import manager

# Configure Gemini
# In a real app, use os.getenv("GOOGLE_API_KEY")
# For this hackathon demo, we might need to ask the user to set it or hardcode (not recommended)
# We will assume the environment variable is set.

class GeminiAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY not found. Agent will not work.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def process_query(self, user_query: str) -> Dict[str, str]:
        if not self.model:
            return {"response": "Error: GOOGLE_API_KEY not configured.", "action": None}

        # Get recent logs to give context
        logs = manager.get_logs()[-20:] # Last 20 logs
        log_context = "\n".join(logs)
        
        status = manager.get_status()
        active_ports = status['active_ports']

        prompt = f"""
        You are the AI System Administrator for CellSync, a biological distributed file system.
        
        Current System State:
        - Active Cells: {active_ports}
        - Recent Logs:
        {log_context}
        
        User Query: "{user_query}"
        
        Your goal is to answer the user's question based on the logs and state.
        You can also perform ACTIONS to fix the system.
        
        If the user asks to fix something or if you detect a problem that needs fixing based on the query, you can output a JSON action.
        
        Available Actions:
        - START_CLUSTER
        - STOP_CLUSTER
        - KILL_CELL <port>
        - REVIVE_CELL <port>
        
        Output Format:
        If you want to perform an action, return ONLY a JSON object:
        {{
            "response": "Explanation of what you are doing",
            "action": "ACTION_NAME",
            "target": <port_number_or_null>
        }}
        
        If no action is needed, just return a plain text response.
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Check if it's JSON
            if text.startswith("{") and text.endswith("}"):
                try:
                    data = json.loads(text)
                    self.execute_action(data.get("action"), data.get("target"))
                    return data
                except json.JSONDecodeError:
                    pass
            
            return {"response": text, "action": None}
            
        except Exception as e:
            return {"response": f"AI Error: {str(e)}", "action": None}

    def execute_action(self, action: str, target: int = None):
        if not action:
            return
            
        print(f"🤖 AGENT EXECUTING: {action} on {target}")
        
        if action == "START_CLUSTER":
            manager.start_cluster()
        elif action == "STOP_CLUSTER":
            manager.stop_cluster()
        elif action == "KILL_CELL" and target:
            manager.kill_cell(int(target))
        elif action == "REVIVE_CELL" and target:
            manager.revive_cell(int(target))

agent = GeminiAgent()
