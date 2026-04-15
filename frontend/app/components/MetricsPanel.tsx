"use client";

interface MetricsData {
  requests_total: number;
  avg_latency_ms: number;
  agent_calls_total: number;
  llm_errors_total: number;
}

export function MetricsPanel({ metrics, health }: {
  metrics: MetricsData | null;
  health: { status: string; llm: boolean } | null;
}) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">System</span>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          health?.status === "ok"
            ? "bg-green-100 text-green-700"
            : "bg-red-100 text-red-700"
        }`}>
          {health?.status === "ok" ? "● Online" : "● Degraded"}
        </span>
      </div>
      {metrics && (
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-white rounded-lg p-2 border border-gray-100">
            <div className="text-gray-400">Requests</div>
            <div className="font-bold text-gray-800 text-base">{metrics.requests_total}</div>
          </div>
          <div className="bg-white rounded-lg p-2 border border-gray-100">
            <div className="text-gray-400">Avg Latency</div>
            <div className="font-bold text-gray-800 text-base">{metrics.avg_latency_ms}ms</div>
          </div>
          <div className="bg-white rounded-lg p-2 border border-gray-100">
            <div className="text-gray-400">Agent Calls</div>
            <div className="font-bold text-gray-800 text-base">{metrics.agent_calls_total}</div>
          </div>
          <div className="bg-white rounded-lg p-2 border border-gray-100">
            <div className="text-gray-400">LLM Errors</div>
            <div className={`font-bold text-base ${metrics.llm_errors_total > 0 ? "text-red-600" : "text-gray-800"}`}>
              {metrics.llm_errors_total}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
