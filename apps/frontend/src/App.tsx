import { useEffect, useState } from "react";
import { AppShell } from "./components/layout/AppShell";
import { demoTasks, knowledgeDocuments } from "./data/demoData";
import { getHealth, createTask } from "./services/api";
import type { CreateTaskInput, HealthStatus, Task, ViewId } from "./types";
import { ActivityPage } from "./pages/ActivityPage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { NewTaskPage } from "./pages/NewTaskPage";
import { OverviewPage } from "./pages/OverviewPage";
import { SecurityPage } from "./pages/SecurityPage";
import { SettingsPage } from "./pages/SettingsPage";
import { TaskDetailPage } from "./pages/TaskDetailPage";

const initialHealth: HealthStatus = { connected: false, message: "Checking backend...", backend: "Checking...", model: "Checking...", isPreview: true };

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>("overview");
  const [tasks, setTasks] = useState<Task[]>(demoTasks);
  const [selectedTask, setSelectedTask] = useState<Task>();
  const [health, setHealth] = useState<HealthStatus>(initialHealth);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { void refreshHealth(); }, []);

  async function refreshHealth() { setHealth(await getHealth()); }
  function navigate(view: ViewId) { setSelectedTask(undefined); setActiveView(view); document.body.classList.remove("nav-open"); }
  function openTask(task: Task) { setSelectedTask(task); setActiveView("activity"); }
  async function handleCreateTask(input: CreateTaskInput) { setSubmitting(true); const task = await createTask(input); setTasks((current) => [task, ...current]); setSubmitting(false); setSelectedTask(task); setActiveView("activity"); }

  function renderPage() {
    if (selectedTask && activeView === "activity") return <TaskDetailPage task={selectedTask} onBack={() => setSelectedTask(undefined)} onNavigate={navigate} />;
    switch (activeView) {
      case "new-task": return <NewTaskPage onSubmit={handleCreateTask} submitting={submitting} onNavigate={navigate} recentTask={tasks[0]} onOpenTask={openTask} />;
      case "activity": return <ActivityPage tasks={tasks} onOpenTask={openTask} />;
      case "knowledge": return <KnowledgePage documents={knowledgeDocuments} />;
      case "security": return <SecurityPage health={health} />;
      case "settings": return <SettingsPage health={health} onRefresh={refreshHealth} />;
      default: return <OverviewPage tasks={tasks} health={health} onNavigate={navigate} onOpenTask={openTask} />;
    }
  }

  return <AppShell activeView={activeView} onNavigate={navigate} connected={health.connected}>{renderPage()}</AppShell>;
}
