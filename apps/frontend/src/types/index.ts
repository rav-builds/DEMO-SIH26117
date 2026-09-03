export type ViewId = "overview" | "new-task" | "activity" | "knowledge" | "security" | "settings";

export type TaskStatus = "completed" | "running" | "failed" | "pending";
export type TaskType = "document" | "coding" | "vision" | "general";
export type EventState = "complete" | "active" | "pending" | "error";

export interface Artifact {
  name: string;
  type: string;
  size?: string;
  downloadUrl?: string;
}

export interface AgentEvent {
  id: string;
  type: string;
  label: string;
  detail: string;
  timestamp: string;
  state: EventState;
  meta?: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  type: TaskType;
  status: TaskStatus;
  createdAt: string;
  duration?: string;
  model?: string;
  artifact?: Artifact;
  events: AgentEvent[];
  sources?: string[];
  isPreview?: boolean;
}

export interface KnowledgeDocument {
  id: string;
  name: string;
  type: string;
  size: string;
  status: "indexed" | "processing" | "failed";
  chunks: number;
  updatedAt: string;
}

export interface HealthStatus {
  connected: boolean;
  message: string;
  backend: string;
  model: string;
  isPreview: boolean;
}

export interface SecurityStatus {
  measured: boolean;
  outbound: string;
  sandbox: "isolated" | "unavailable";
  lastChecked: string;
  message: string;
}

export interface CreateTaskInput {
  title: string;
  prompt: string;
  type: TaskType;
  file?: File;
}
