import { Activity, BookOpen, Home, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import type { ViewId } from "../../types";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function AppShell({ activeView, onNavigate, connected, children }: { activeView: ViewId; onNavigate: (view: ViewId) => void; connected: boolean; children: ReactNode }) {
  const mobileItems = [{ id: "overview" as ViewId, label: "Home", icon: Home }, { id: "new-task" as ViewId, label: "New", icon: PlusCircle }, { id: "activity" as ViewId, label: "Activity", icon: Activity }, { id: "security" as ViewId, label: "Security", icon: ShieldCheck }];
  return <div className="app-shell"><Sidebar activeView={activeView} onNavigate={onNavigate} connected={connected} /><main className="main-content"><TopBar activeView={activeView} onNavigate={onNavigate} onMenu={() => document.body.classList.toggle("nav-open")} /><div className="page-content">{children}</div></main><div className="mobile-overlay" onClick={() => document.body.classList.remove("nav-open")} /><nav className="mobile-nav" aria-label="Mobile navigation">{mobileItems.map(({ id, label, icon: Icon }) => <button key={id} className={activeView === id ? "active" : ""} onClick={() => onNavigate(id)}>{id === "new-task" ? <Icon /> : <Icon size={17} />}<span>{label}</span></button>)}</nav></div>;
}

function PlusCircle() { return <span className="mobile-plus"><span>+</span></span>; }
