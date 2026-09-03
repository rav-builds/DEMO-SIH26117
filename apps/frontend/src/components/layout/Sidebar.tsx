import { Activity, BookOpen, Cpu, LayoutDashboard, LockKeyhole, Plus, Settings, ShieldCheck, Sparkles } from "lucide-react";
import type { ViewId } from "../../types";

interface SidebarProps { activeView: ViewId; onNavigate: (view: ViewId) => void; connected: boolean; }

const items: { id: ViewId; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "new-task", label: "New task", icon: Plus },
  { id: "activity", label: "Activity", icon: Activity },
  { id: "knowledge", label: "Knowledge base", icon: BookOpen },
  { id: "security", label: "Security center", icon: ShieldCheck },
];

export function Sidebar({ activeView, onNavigate, connected }: SidebarProps) {
  return <aside className="sidebar"><div className="brand"><div className="brand-mark"><Sparkles size={17} /></div><div><strong>Sovereign</strong><span>AI WORKBENCH</span></div></div><div className="workspace-switcher"><div className="workspace-avatar">MR</div><div><span>MRPL workspace</span><small>Private environment</small></div><span className="chevron">⌄</span></div><nav className="main-nav" aria-label="Main navigation">{items.map(({ id, label, icon: Icon }) => <button key={id} className={activeView === id ? "nav-item active" : "nav-item"} onClick={() => onNavigate(id)}><Icon size={18} /><span>{label}</span>{id === "activity" && <span className="nav-count">3</span>}</button>)}</nav><div className="sidebar-bottom"><div className="local-card"><div className="local-card-icon"><LockKeyhole size={15} /></div><div><strong>Local first</strong><span>Your data stays inside</span></div><span className="live-pulse" /></div><button className={activeView === "settings" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("settings")}><Settings size={18} /><span>Settings</span></button><div className="profile"><div className="profile-avatar">SJ</div><div><strong>Shubham Jha</strong><span>Contributor</span></div><span className="profile-more">•••</span></div></div><div className={`sidebar-connection ${connected ? "is-connected" : ""}`}><span className="connection-dot" /><span>{connected ? "Backend connected" : "Preview mode"}</span></div></aside>;
}
