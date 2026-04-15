const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AgentResponse {
  session_id: string;
  query: string;
  route: string;
  answer: string;
  steps: string[];
}

export interface HistoryMessage {
  role: string;
  content: string;
  ts: number;
}

export async function sendQuery(
  query: string,
  sessionId: string
): Promise<AgentResponse> {
  try {
    const res = await fetch(`${BASE_URL}/agent/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, session_id: sessionId }),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  } catch (e) {
    throw e;
  }
}

export async function fetchHistory(sessionId: string): Promise<HistoryMessage[]> {
  const res = await fetch(`${BASE_URL}/agent/history/${sessionId}`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.history || [];
}

export async function clearHistory(sessionId: string): Promise<void> {
  await fetch(`${BASE_URL}/agent/history/${sessionId}`, { method: "DELETE" });
}

export async function fetchMetrics() {
  try {
    const res = await fetch(`${BASE_URL}/metrics`);
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function fetchHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
