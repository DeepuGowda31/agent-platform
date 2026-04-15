"use client";

const ROUTE_COLORS: Record<string, string> = {
  research: "bg-blue-100 text-blue-700 border-blue-200",
  data: "bg-green-100 text-green-700 border-green-200",
  general: "bg-purple-100 text-purple-700 border-purple-200",
};

const ROUTE_LABELS: Record<string, string> = {
  research: "🔍 Research Agent",
  data: "📊 Data Agent",
  general: "💬 General Agent",
};

export function RouteBadge({ route }: { route: string }) {
  const color = ROUTE_COLORS[route] || "bg-gray-100 text-gray-700 border-gray-200";
  const label = ROUTE_LABELS[route] || route;
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${color}`}>
      {label}
    </span>
  );
}
