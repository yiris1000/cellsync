import { useState, useEffect, useRef } from 'react'
import './index.css'

const API_URL = process.env.BACKEND_URL || "http://localhost:8000";

function App() {
  const [status, setStatus] = useState({ active_ports: [], total_ports: [] });
  const [logs, setLogs] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([
    { role: "system", content: "Hello! I am the CellSync Agent. How can I help you?" }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const logsEndRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(fetchStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const fetchStatus = async () => {
    try {
      const statusRes = await fetch(`${API_URL}/status`);
      const statusData = await statusRes.json();
      setStatus(statusData);

      const logsRes = await fetch(`${API_URL}/logs`);
      const logsData = await logsRes.json();
      setLogs(logsData.logs);
    } catch (e) {
      console.error("Error fetching status:", e);
    }
  };

  const sendCommand = async (endpoint, body = {}) => {
    try {
      await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      fetchStatus();
    } catch (e) {
      console.error(`Error sending command ${endpoint}:`, e);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatHistory(prev => [...prev, { role: "user", content: userMsg }]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const res = await fetch(`${API_URL}/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();

      setChatHistory(prev => [...prev, { role: "agent", content: data.response }]);

      if (data.action) {
        setChatHistory(prev => [...prev, { role: "system", content: `⚡ EXECUTING ACTION: ${data.action} on target ${data.target}` }]);
      }

    } catch (e) {
      setChatHistory(prev => [...prev, { role: "error", content: "Failed to reach Agent." }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8 font-mono">
      <header className="mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-4xl font-bold text-cyan-400 mb-2">CellSync 🧬</h1>
        <p className="text-slate-400">Biological Distributed File System Control Center</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* LEFT COLUMN: VISUALIZER & CONTROLS */}
        <div className="lg:col-span-2 space-y-8">

          {/* CELL VISUALIZER */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <span className="mr-2">🔬</span> Live Cell Cluster
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {status.total_ports.map(port => {
                const isAlive = status.active_ports.includes(port);
                return (
                  <div key={port} className={`
                    relative h-32 rounded-lg flex flex-col items-center justify-center border-2 transition-all duration-300
                    ${isAlive ? 'border-green-500 bg-green-500/10 shadow-[0_0_15px_rgba(34,197,94,0.3)]' : 'border-red-500 bg-red-500/10 grayscale'}
                  `}>
                    <div className={`text-4xl mb-2 ${isAlive ? 'animate-pulse' : ''}`}>
                      {isAlive ? '🦠' : '💀'}
                    </div>
                    <div className="font-bold text-lg">Cell-{port}</div>
                    <div className={`text-xs uppercase font-bold mt-1 ${isAlive ? 'text-green-400' : 'text-red-400'}`}>
                      {isAlive ? 'ALIVE' : 'DEAD'}
                    </div>

                    {/* Individual Controls */}
                    <div className="absolute top-2 right-2 flex gap-1">
                      {isAlive ? (
                        <button
                          onClick={() => sendCommand(`/kill/${port}`)}
                          className="p-1 bg-red-500/20 hover:bg-red-500/40 rounded text-xs text-red-300"
                          title="Kill Cell"
                        >
                          ❌
                        </button>
                      ) : (
                        <button
                          onClick={() => sendCommand(`/revive/${port}`)}
                          className="p-1 bg-green-500/20 hover:bg-green-500/40 rounded text-xs text-green-300"
                          title="Revive Cell"
                        >
                          ⚡
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* HACKER CONSOLE */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
            <h2 className="text-xl font-bold mb-4 flex items-center text-red-400">
              <span className="mr-2">💀</span> Chaos Monkey Console
            </h2>
            <div className="flex flex-wrap gap-4">
              <button
                onClick={() => sendCommand('/start')}
                className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded font-bold transition-colors"
              >
                ▶ START CLUSTER
              </button>
              <button
                onClick={() => sendCommand('/stop')}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded font-bold transition-colors"
              >
                ⏹ STOP CLUSTER
              </button>
              <div className="w-px bg-slate-600 mx-2"></div>
              <button
                onClick={() => {
                  const target = status.active_ports[Math.floor(Math.random() * status.active_ports.length)];
                  if (target) sendCommand(`/kill/${target}`);
                }}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-500 rounded font-bold transition-colors"
              >
                🎲 KILL RANDOM
              </button>
              {/* Add more hacker tools here later */}
            </div>
          </div>

          {/* SYSTEM LOGS */}
          <div className="bg-black rounded-xl p-4 border border-slate-700 shadow-lg font-mono text-sm h-64 overflow-y-auto">
            <h3 className="text-slate-500 mb-2 sticky top-0 bg-black pb-2 border-b border-slate-800">System Logs</h3>
            <div className="space-y-1">
              {logs.map((log, i) => (
                <div key={i} className="text-slate-300 break-words">
                  {log}
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN: AI AGENT */}
        <div className="lg:col-span-1 h-[calc(100vh-8rem)] sticky top-8">
          <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg h-full flex flex-col">
            <div className="p-4 border-b border-slate-700 bg-slate-800/50 rounded-t-xl">
              <h2 className="text-xl font-bold flex items-center text-purple-400">
                <span className="mr-2">🤖</span> Gemini Agent
              </h2>
              <p className="text-xs text-slate-400">AI System Administrator</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatHistory.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`
                    max-w-[85%] rounded-lg p-3 text-sm
                    ${msg.role === 'user' ? 'bg-cyan-600 text-white' :
                      msg.role === 'system' ? 'bg-yellow-500/20 text-yellow-200 border border-yellow-500/30' :
                        msg.role === 'error' ? 'bg-red-500/20 text-red-200' :
                          'bg-slate-700 text-slate-200'}
                  `}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-700 rounded-lg p-3 text-sm animate-pulse">
                    Thinking...
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleChatSubmit} className="p-4 border-t border-slate-700 bg-slate-800/50 rounded-b-xl">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask Gemini to fix the network..."
                  className="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-cyan-500 transition-colors"
                />
                <button
                  type="submit"
                  disabled={isChatLoading}
                  className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded transition-colors disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App
