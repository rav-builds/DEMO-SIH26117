import type { TaskStatus } from "../../types";

interface StatusBadgeProps {
  status: TaskStatus | "indexed" | "processing" | "failed" | "connected" | "preview" | "isolated" | "unavailable";
  label?: string;
  dot?: boolean;
}

export function StatusBadge({ status, label, dot = true }: StatusBadgeProps) {
  const defaultLabels: Record<string, string> = {
    completed: "Completed", running: "Running", failed: "Failed", pending: "Queued", indexed: "Indexed", processing: "Processing", connected: "Connected", preview: "Preview mode", isolated: "Isolated", unavailable: "Unavailable",
  };
  return <span className={`status-badge status-${status}`}>{dot && <span className="status-dot" />} {label || defaultLabels[status] || status}</span>;
}
