import { Filter, Search, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import type { Task } from "../types";
import { TaskCard } from "../components/tasks/TaskCard";
import { SectionHeader } from "../components/ui/SectionHeader";
import { EmptyState } from "../components/ui/EmptyState";

export function ActivityPage({ tasks, onOpenTask }: { tasks: Task[]; onOpenTask: (task: Task) => void }) { const [query, setQuery] = useState(""); const filtered = tasks.filter((task) => task.title.toLowerCase().includes(query.toLowerCase())); return <div className="page-stack"><SectionHeader eyebrow="WORKSPACE HISTORY" title="Activity" description="Every task, model decision and generated deliverable in one place." action={<button className="outline-button"><SlidersHorizontal size={15} /> Filters</button>} /><div className="activity-toolbar"><div className="search-field"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search tasks" /></div><button className="filter-button"><Filter size={15} /> All statuses <span>⌄</span></button><span className="result-count">{filtered.length} tasks</span></div>{filtered.length ? <div className="activity-grid">{filtered.map((task) => <TaskCard key={task.id} task={task} onOpen={onOpenTask} />)}</div> : <EmptyState icon={Search} title="No tasks found" description="Try a different search term or clear the filter." />}</div>; }
