import type { AgentEvent, KnowledgeDocument, SecurityStatus, Task } from "../types";

export const demoEvents: AgentEvent[] = [
  { id: "evt-1", type: "TASK_RECEIVED", label: "Task received", detail: "Inspection report workflow accepted", timestamp: "10:42:08", state: "complete" },
  { id: "evt-2", type: "PLAN_CREATED", label: "Plan created", detail: "4-step plan prepared for document analysis", timestamp: "10:42:09", state: "complete", meta: "4 steps" },
  { id: "evt-3", type: "MODEL_SELECTED", label: "Local model selected", detail: "Reasoning model assigned for approval-note drafting", timestamp: "10:42:09", state: "complete", meta: "Ornith 1.5 9B" },
  { id: "evt-4", type: "DOCUMENT_PROCESSED", label: "Document processed", detail: "OCR extracted 18 findings from inspection-report.pdf", timestamp: "10:42:15", state: "complete", meta: "18 findings" },
  { id: "evt-5", type: "KNOWLEDGE_RETRIEVED", label: "Local knowledge retrieved", detail: "SOP-14 and equipment manual matched to the findings", timestamp: "10:42:17", state: "complete", meta: "2 sources" },
  { id: "evt-6", type: "OUTPUT_GENERATED", label: "Approval note generated", detail: "Draft is ready for review and download", timestamp: "10:42:28", state: "complete", meta: "DOCX" },
  { id: "evt-7", type: "TASK_COMPLETED", label: "Task completed", detail: "Workflow finished successfully", timestamp: "10:42:29", state: "complete" },
];

export const demoTasks: Task[] = [
  {
    id: "tsk-8f31a2",
    title: "Inspection report to approval note",
    description: "Extract findings from a scanned inspection report and draft an approval note.",
    type: "document",
    status: "completed",
    createdAt: "Today, 10:42 AM",
    duration: "21 sec",
    model: "Ornith 1.5 9B",
    artifact: { name: "Approval_Note.docx", type: "DOCX", size: "42 KB" },
    events: demoEvents,
    sources: ["SOP-14 · Pressure vessel inspection", "Equipment manual · Compressor unit C-204"],
    isPreview: true,
  },
  {
    id: "tsk-3c012b",
    title: "Calculate compressor efficiency",
    description: "Run a verified engineering calculation in the isolated code sandbox.",
    type: "coding",
    status: "completed",
    createdAt: "Yesterday, 4:18 PM",
    duration: "14 sec",
    model: "Ornith 1.5 9B",
    events: [
      { id: "code-1", type: "TASK_RECEIVED", label: "Task received", detail: "Coding workflow accepted", timestamp: "16:18:02", state: "complete" },
      { id: "code-2", type: "MODEL_SELECTED", label: "Coding model selected", detail: "A local model was assigned to generate the calculation", timestamp: "16:18:03", state: "complete", meta: "Ornith 1.5 9B" },
      { id: "code-3", type: "TOOL_COMPLETED", label: "Sandbox verified result", detail: "Code executed with network access disabled", timestamp: "16:18:16", state: "complete", meta: "Isolated" },
      { id: "code-4", type: "TASK_COMPLETED", label: "Task completed", detail: "Calculation result returned", timestamp: "16:18:16", state: "complete" },
    ],
    isPreview: true,
  },
  {
    id: "tsk-9a40de",
    title: "Valve inspection image review",
    description: "Review a maintenance image for visible anomalies and produce a summary.",
    type: "vision",
    status: "failed",
    createdAt: "Yesterday, 11:06 AM",
    duration: "8 sec",
    model: "Vision model unavailable",
    events: [
      { id: "vision-1", type: "TASK_RECEIVED", label: "Task received", detail: "Vision workflow accepted", timestamp: "11:06:01", state: "complete" },
      { id: "vision-2", type: "MODEL_SELECTED", label: "Vision model selected", detail: "No local vision endpoint was available", timestamp: "11:06:02", state: "error", meta: "Unavailable" },
      { id: "vision-3", type: "TASK_FAILED", label: "Task failed", detail: "Connect a local vision model and retry", timestamp: "11:06:09", state: "error" },
    ],
    isPreview: true,
  },
];

export const knowledgeDocuments: KnowledgeDocument[] = [
  { id: "doc-1", name: "SOP-14 Pressure Vessel Inspection.pdf", type: "PDF", size: "2.4 MB", status: "indexed", chunks: 86, updatedAt: "Today, 09:18 AM" },
  { id: "doc-2", name: "Compressor Unit C-204 Manual.pdf", type: "PDF", size: "8.1 MB", status: "indexed", chunks: 214, updatedAt: "Yesterday, 02:40 PM" },
  { id: "doc-3", name: "Maintenance Approval Matrix.docx", type: "DOCX", size: "184 KB", status: "processing", chunks: 0, updatedAt: "Just now" },
];

export const previewSecurity: SecurityStatus = {
  measured: false,
  outbound: "Not measured",
  sandbox: "unavailable",
  lastChecked: "Awaiting backend integration",
  message: "The security endpoint is not available in the current backend build. No sovereignty claim is being made.",
};
