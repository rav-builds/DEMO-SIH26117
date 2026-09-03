import { ArrowUpRight, FileText, FlaskConical, Image, TerminalSquare } from "lucide-react";
import type { Task } from "../../types";
import { StatusBadge } from "../ui/StatusBadge";

const icons = { document: FileText, coding: TerminalSquare, vision: Image, general: FlaskConical };
const labels = { document: "Document workflow", coding: "Coding workflow", vision: "Vision workflow", general: "Reasoning workflow" };

export function TaskCard({ task, onOpen }: { task: Task; onOpen: (task: Task) => void }) { const Icon = icons[task.type]; return <button className="task-card" onClick={() => onOpen(task)}><div className={`task-type-icon type-${task.type}`}><Icon size={18} /></div><div className="task-card-body"><div className="task-card-top"><span className="task-type-label">{labels[task.type]}</span><StatusBadge status={task.status} /></div><h3>{task.title}</h3><p>{task.description}</p><div className="task-card-meta"><span>{task.createdAt}</span>{task.duration && <><i /> <span>{task.duration}</span></>}<ArrowUpRight size={15} /></div></div></button>; }
