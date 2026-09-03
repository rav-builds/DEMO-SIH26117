import type { LucideIcon } from "lucide-react";

interface MetricCardProps { label: string; value: string; detail: string; icon: LucideIcon; tone?: "mint" | "amber" | "blue" | "rose"; }

export function MetricCard({ label, value, detail, icon: Icon, tone = "mint" }: MetricCardProps) {
  return <article className="metric-card"><div className={`metric-icon metric-${tone}`}><Icon size={18} /></div><div><p className="metric-label">{label}</p><strong>{value}</strong><p className="metric-detail">{detail}</p></div></article>;
}
