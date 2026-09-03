import type { CreateTaskInput, HealthStatus, Task } from "../types";
import { demoEvents } from "../data/demoData";

const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000/api").replace(/\/$/, "");

export async function getHealth(): Promise<HealthStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(2500) });
    if (!response.ok) throw new Error(`Health check returned ${response.status}`);
    const data = (await response.json()) as { status?: string };
    return {
      connected: data.status === "ok",
      message: data.status === "ok" ? "Backend connected" : "Backend returned an unknown status",
      backend: "FastAPI",
      model: "Configured by backend",
      isPreview: false,
    };
  } catch {
    return {
      connected: false,
      message: "Backend unavailable · Preview mode",
      backend: "Not connected",
      model: "Not connected",
      isPreview: true,
    };
  }
}

export async function createTask(input: CreateTaskInput): Promise<Task> {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: input.prompt, task_type: input.type, metadata: { title: input.title }, file_paths: input.file ? [input.file.name] : [] }),
    });
    if (!response.ok) throw new Error(`Task endpoint returned ${response.status}`);
    return (await response.json()) as Task;
  } catch {
    return {
      id: `preview-${Date.now()}`,
      title: input.title,
      description: input.prompt,
      type: input.type,
      status: "running",
      createdAt: "Just now",
      model: "Preview pipeline",
      events: demoEvents.map((event, index) => ({ ...event, id: `new-${index}`, state: index < 2 ? "complete" : "pending" })),
      isPreview: true,
    };
  }
}

export { API_BASE_URL };
