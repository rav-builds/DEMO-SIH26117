import { Bell, HelpCircle, Menu, Plus, Search } from "lucide-react";
import type { ViewId } from "../../types";

const titles: Record<ViewId, { title: string; subtitle: string }> = { overview: { title: "Overview", subtitle: "Your local intelligence workspace" }, "new-task": { title: "New task", subtitle: "Turn confidential work into an executable workflow" }, activity: { title: "Activity", subtitle: "Review every agent run and its evidence" }, knowledge: { title: "Knowledge base", subtitle: "Local documents available to your agents" }, security: { title: "Security center", subtitle: "Understand how your environment is protected" }, settings: { title: "Settings", subtitle: "Runtime preferences and connection details" } };

export function TopBar({ activeView, onNavigate, onMenu }: { activeView: ViewId; onNavigate: (view: ViewId) => void; onMenu: () => void }) {
  const page = titles[activeView];
  return <header className="topbar"><button className="mobile-menu" onClick={onMenu} aria-label="Open navigation"><Menu size={20} /></button><div><h1>{page.title}</h1><p>{page.subtitle}</p></div><div className="topbar-actions"><button className="icon-button search-button" aria-label="Search"><Search size={18} /></button><button className="icon-button" aria-label="Help"><HelpCircle size={18} /></button><button className="icon-button notification-button" aria-label="Notifications"><Bell size={18} /><span /></button><button className="top-new-task" onClick={() => onNavigate("new-task")}><Plus size={16} /> New task</button></div></header>;
}
