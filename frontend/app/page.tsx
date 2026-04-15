"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Trash2, RefreshCw } from "lucide-react";
import { sendQuery, clearHistory, fetchMetrics, fetchHealth, AgentResponse } from "./lib/api";
import { RouteBadge } from "./components/RouteBadge";
import { MetricsPanel } from "./components/MetricsPanel";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  route?: string;
  steps?: string[];
  ts: number;
}

const SESSION_KEY = "agent_session_id";

function getOrCreateSession(): string {
  if (typeof window === "undefined") return "default";
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = `session_${Date.now()}`;
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("default");
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(getOrCreateSession());
  }, []);

  const refreshMetrics = useCallback(async () => {
    const [m, h] = await Promise.all([fetchMetrics(), fetchHealth()]);
    setMetrics(m);
    setHealth(h);
  }, []);

  useEffect(() => {
    refreshMetrics();
    const interval = setInterval(refreshMetrics, 10000);
    return () => clearInterval(interval);
  }, [refreshMetrics]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const query = input.trim();
    if (!query || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
      ts: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res: AgentResponse = await sendQuery(query, sessionId);
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.answer,
        route: res.route,
        steps: res.steps,
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      refreshMetrics();
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "⚠️ Failed to reach the agent. Is the backend running?",
          ts: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleClear() {
    await clearHistory(sessionId);
    setMessages([]);
    const newId = `session_${Date.now()}`;
    localStorage.setItem(SESSION_KEY, newId);
    setSessionId(newId);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-72 bg-white border-r border-gray-200 flex flex-col p-4 gap-4">
        <div>
          <h1 className="text-lg font-bold text-gray-900">Agent Platform</h1>
          <p className="text-xs text-gray-400 mt-0.5">Multi-Agent AI System</p>
        </div>

        <MetricsPanel metrics={metrics} health={health} />

        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Agents</span>
          <div className="space-y-1.5 text-xs text-gray-600">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-400"></span>
              Research — web + vector search
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400"></span>
              Data — SQL + calculator
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-400"></span>
              General — documents + API
            </div>
          </div>
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Try these</span>
          <div className="space-y-1">
            {[
              "What happened with sales?",
              "Calculate 15% of 2400",
              "Search the web for latest AI news",
              "What is 2 + 2 * 10?",
            ].map((q) => (
              <button
                key={q}
                onClick={() => setInput(q)}
                className="w-full text-left text-xs text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded px-2 py-1 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-auto space-y-2">
          <div className="text-xs text-gray-400 truncate">Session: {sessionId}</div>
          <button
            onClick={handleClear}
            className="w-full flex items-center justify-center gap-2 text-xs text-red-500 hover:text-red-700 border border-red-200 hover:border-red-400 rounded-lg py-2 transition-colors"
          >
            <Trash2 size={12} /> Clear Memory
          </button>
          <button
            onClick={refreshMetrics}
            className="w-full flex items-center justify-center gap-2 text-xs text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg py-2 transition-colors"
          >
            <RefreshCw size={12} /> Refresh Metrics
          </button>
        </div>
      </aside>

      {/* Chat area */}
      <main className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400 space-y-2">
                <div className="text-4xl">🤖</div>
                <div className="text-sm font-medium">Ask me anything</div>
                <div className="text-xs">I'll route your query to the best agent automatically</div>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-2xl space-y-1 ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col`}>
                {msg.role === "assistant" && msg.route && (
                  <RouteBadge route={msg.route} />
                )}
                {msg.role === "assistant" && msg.steps && msg.steps.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {msg.steps.map((step, i) => (
                      <span key={i} className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full border border-gray-200">
                        {step}
                      </span>
                    ))}
                  </div>
                )}
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm"
                  }`}
                >
                  {msg.content}
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(msg.ts).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1 items-center">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]"></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]"></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]"></span>
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="flex gap-3 items-end max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything... (Enter to send, Shift+Enter for new line)"
              rows={1}
              className="flex-1 resize-none border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              style={{ maxHeight: "120px" }}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-xl p-3 transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
