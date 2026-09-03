import { Check, Circle, LoaderCircle, X } from "lucide-react";
import type { AgentEvent } from "../../types";

export function EventTimeline({ events, compact = false }: { events: AgentEvent[]; compact?: boolean }) {
  return <div className={`event-timeline ${compact ? "timeline-compact" : ""}`}>{events.map((event, index) => <div className={`event-row event-${event.state}`} key={event.id}><div className="event-marker">{event.state === "complete" ? <Check size={13} /> : event.state === "active" ? <LoaderCircle size={14} className="spin" /> : event.state === "error" ? <X size={13} /> : <Circle size={8} />}</div><div className="event-line" /><div className="event-copy"><div className="event-heading"><strong>{event.label}</strong>{event.meta && <span>{event.meta}</span>}</div><p>{event.detail}</p><small>{event.timestamp} · {event.type}</small></div>{index === 0 && !compact && <span className="event-live">LIVE TRACE</span>}</div>)}</div>;
}
