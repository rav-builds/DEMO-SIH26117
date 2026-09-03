import React, { useState, useEffect, useRef } from 'react';
import {
  Shield,
  Cpu,
  Terminal,
  Database,
  FileText,
  Send,
  ChevronDown,
  ChevronRight,
  Play,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  Layers,
  Search,
  Lock,
  RefreshCw,
  FolderOpen
} from 'lucide-react';

interface TaskMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  reasoning?: string;
  toolCalls?: Array<{ name: string; params: any; result?: any }>;
  status?: 'pending' | 'running' | 'completed' | 'failed';
  taskType?: string;
  timestamp: string;
}

interface ServerStatus {
  app: string;
  version: string;
  status: string;
  active_backend: string;
  active_model: string;
}

export default function App() {
  const [messages, setMessages] = useState<TaskMessage[]>([]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [taskType, setTaskType] = useState<'general' | 'rag' | 'agent' | 'vision' | 'document' | 'sandbox'>('general');
  const [sandboxEnabled, setSandboxEnabled] = useState(false);
  const [temperature, setTemperature] = useState(0.7);
  const [activeTab, setActiveTab] = useState<'sandbox' | 'rag' | 'security'>('sandbox');
  const [expandedReasoning, setExpandedReasoning] = useState<Record<string, boolean>>({});
  const [isStreaming, setIsStreaming] = useState(false);
  const [sandboxConsole, setSandboxConsole] = useState('Sandbox initialized. Ready for code execution.');
  const [serverStatus, setServerStatus] = useState<ServerStatus>({
    app: 'Sovereign AI Workbench',
    version: '0.1.0',
    status: 'online',
    active_backend: 'ollama',
    active_model: 'ornith-1.5:9b-q4_k_m',
  });
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Poll server status on load
  useEffect(() => {
    fetch('/api/health')
      .catch(() => {})
      .then(() => {
        return fetch('/');
      })
      .then((res) => res.ok ? res.json() : null)
      .then((data) => {
        if (data) setServerStatus(data);
      })
      .catch((err) => console.log('Backend not reached yet:', err));

    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = async () => {
    try {
      const res = await fetch('/api/security/audit?limit=10');
      const json = await res.json();
      if (json.success && json.data) {
        setAuditLogs(json.data);
      }
    } catch (e) {
      // Ignored if offline
    }
  };

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  const toggleReasoning = (id: string) => {
    setExpandedReasoning((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  /**
   * Native SSE ReadableStream consumer.
   * Parses standard `event: ...\ndata: ...\n\n` frames from FastAPI StreamingResponse.
   */
  const consumeTaskStream = async (taskId: string, assistantMsgId: string) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/stream`);
      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          if (!part.trim()) continue;
          let eventType = 'message';
          let eventData = '';

          for (const line of part.split('\n')) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              eventData = line.slice(6).trim();
            }
          }

          if (!eventData) continue;

          try {
            const parsed = JSON.parse(eventData);

            if (eventType === 'token') {
              const token = parsed.token || '';
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? { ...msg, content: msg.content + token, status: 'running' }
                    : msg
                )
              );
            } else if (eventType === 'reasoning') {
              const reasoning = parsed.reasoning || '';
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? { ...msg, reasoning: (msg.reasoning || '') + reasoning }
                    : msg
                )
              );
            } else if (eventType === 'tool_call') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? {
                        ...msg,
                        toolCalls: [
                          ...(msg.toolCalls || []),
                          { name: parsed.tool_name, params: parsed.tool_input },
                        ],
                      }
                    : msg
                )
              );
              if (parsed.tool_name === 'run_sandbox_code') {
                setSandboxConsole((prev) => prev + `\n\n[DOCKER SANDBOX INVOCATION]\nCode:\n${parsed.tool_input?.code || ''}`);
              }
            } else if (eventType === 'tool_result') {
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;
                  const calls = [...(msg.toolCalls || [])];
                  if (calls.length > 0) {
                    calls[calls.length - 1].result = parsed.result;
                  }
                  return { ...msg, toolCalls: calls };
                })
              );
              if (parsed.tool_name === 'run_sandbox_code' && parsed.result) {
                setSandboxConsole((prev) => prev + `\n[SANDBOX OUTPUT]\n${JSON.stringify(parsed.result, null, 2)}`);
              }
            } else if (eventType === 'completion') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId ? { ...msg, status: 'completed' } : msg
                )
              );
              fetchAuditLogs();
            } else if (eventType === 'error') {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? { ...msg, content: msg.content + `\n[Error: ${parsed.error}]`, status: 'failed' }
                    : msg
                )
              );
            }
          } catch (err) {
            console.error('Error parsing SSE frame:', err);
          }
        }
      }
    } catch (err) {
      console.error('Stream reader error:', err);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleSendPrompt = async (promptOverride?: string) => {
    const textToSend = promptOverride || inputPrompt;
    if (!textToSend.trim() || isStreaming) return;

    const userMsgId = 'msg_' + Date.now();
    const assistantMsgId = 'msg_' + (Date.now() + 1);

    const userMessage: TaskMessage = {
      id: userMsgId,
      role: 'user',
      content: textToSend,
      taskType: taskType,
      timestamp: new Date().toLocaleTimeString(),
    };

    const assistantPlaceholder: TaskMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      status: 'pending',
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);
    setInputPrompt('');
    setIsStreaming(true);

    try {
      // Dispatch task via POST /api/tasks
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: textToSend,
          task_type: taskType,
          sandbox_enabled: sandboxEnabled,
          temperature: temperature,
          stream: true,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const taskData = await res.json();
      const taskId = taskData.task_id;

      // Automatically expand reasoning accordion by default for the new message
      setExpandedReasoning((prev) => ({ ...prev, [assistantMsgId]: true }));

      // Attach SSE stream reader
      await consumeTaskStream(taskId, assistantMsgId);
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? { ...msg, content: `Error creating task: ${err.message}`, status: 'failed' }
            : msg
        )
      );
      setIsStreaming(false);
    }
  };

  return (
    <div className="workbench-container">
      {/* Top Status Bar: Sovereign Telemetry Ribbon */}
      <header className="topbar">
        <div className="topbar-left">
          <div className="brand-badge">
            <Cpu className="brand-logo" size={18} />
            <span>SOVEREIGN AI WORKBENCH</span>
          </div>
          <div className="air-gap-shield">
            <span className="shield-pulse"></span>
            <Shield size={12} />
            <span>Air-Gapped: Zero Egress</span>
          </div>
        </div>

        <div className="topbar-right">
          <div className="telemetry-chip">
            <span>ENGINE:</span>
            <strong>{serverStatus.active_backend.toUpperCase()}</strong>
          </div>
          <div className="telemetry-chip">
            <span>MODEL:</span>
            <strong>{serverStatus.active_model}</strong>
          </div>
          <div className="telemetry-chip">
            <span>ISOLATION:</span>
            <strong style={{ color: 'var(--accent-emerald)' }}>DOCKER (256MB)</strong>
          </div>
        </div>
      </header>

      {/* Main 3-Column Layout */}
      <div className="layout-body">
        {/* Left Navigation Sidebar */}
        <aside className="left-sidebar">
          <div className="sidebar-header">
            <button className="new-task-btn" onClick={() => setMessages([])}>
              <Sparkles size={14} />
              <span>New Sovereign Session</span>
            </button>
          </div>

          <div className="nav-section-title">Execution Modes</div>
          <ul className="nav-list">
            <li
              className={`nav-item ${taskType === 'general' ? 'active' : ''}`}
              onClick={() => setTaskType('general')}
            >
              <Cpu size={14} />
              <span>General Reasoning</span>
            </li>
            <li
              className={`nav-item ${taskType === 'agent' ? 'active' : ''}`}
              onClick={() => setTaskType('agent')}
            >
              <Layers size={14} />
              <span>Agentic Orchestration</span>
            </li>
            <li
              className={`nav-item ${taskType === 'rag' ? 'active' : ''}`}
              onClick={() => setTaskType('rag')}
            >
              <Database size={14} />
              <span>RAG Knowledge Vault</span>
            </li>
            <li
              className={`nav-item ${taskType === 'sandbox' ? 'active' : ''}`}
              onClick={() => {
                setTaskType('sandbox');
                setSandboxEnabled(true);
              }}
            >
              <Terminal size={14} />
              <span>Sandboxed Code</span>
            </li>
          </ul>

          <div className="nav-section-title">Session History</div>
          <div className="task-history-list">
            {messages
              .filter((m) => m.role === 'user')
              .map((m) => (
                <div key={m.id} className="task-history-item" onClick={() => handleSendPrompt(m.content)}>
                  <div className="task-history-prompt">{m.content}</div>
                  <div className="task-history-meta">
                    <span>{m.taskType?.toUpperCase()}</span>
                    <span>{m.timestamp}</span>
                  </div>
                </div>
              ))}
            {messages.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', padding: '0.5rem' }}>
                No active tasks.
              </div>
            )}
          </div>
        </aside>

        {/* Center Workspace Canvas */}
        <main className="center-canvas">
          <div className="chat-scroll-area" ref={chatScrollRef}>
            {messages.length === 0 ? (
              <div className="welcome-screen">
                <h2>Sovereign Defense AI Workbench</h2>
                <p>
                  Air-gapped intelligence platform running locally on your hardware. Multi-backend model support, hybrid RAG vector search, sandboxed execution, and tamper-proof security auditing.
                </p>

                <div className="quick-prompts-grid">
                  <div
                    className="quick-prompt-card"
                    onClick={() => {
                      setTaskType('agent');
                      handleSendPrompt('Use the calculator tool to compute 245 * 18, then summarize why this deterministic tool is safer than LLM hallucination.');
                    }}
                  >
                    <div className="quick-prompt-title">⚡ Deterministic Tool Agent</div>
                    <div className="quick-prompt-desc">Invoke high-precision math tools without LLM calculation errors</div>
                  </div>

                  <div
                    className="quick-prompt-card"
                    onClick={() => {
                      setTaskType('sandbox');
                      setSandboxEnabled(true);
                      handleSendPrompt('Write and execute a Python script to compute the first 10 Fibonacci numbers and verify their primes.');
                    }}
                  >
                    <div className="quick-prompt-title">🔒 Isolated Docker Sandbox</div>
                    <div className="quick-prompt-desc">Run arbitrary generated code within a 256MB memory cap, network-isolated container</div>
                  </div>

                  <div
                    className="quick-prompt-card"
                    onClick={() => {
                      setTaskType('rag');
                      handleSendPrompt('Explain how Reciprocal Rank Fusion combines vector similarity search with BM25 keyword matching in our RAG pipeline.');
                    }}
                  >
                    <div className="quick-prompt-title">📚 Hybrid RAG Search</div>
                    <div className="quick-prompt-desc">Query document collections with dual semantic & keyword ranking</div>
                  </div>

                  <div
                    className="quick-prompt-card"
                    onClick={() => {
                      setTaskType('general');
                      handleSendPrompt('Provide a high-level operational security review of our Sovereign AI Workbench blueprint.');
                    }}
                  >
                    <div className="quick-prompt-title">🛡️ Zero-Trust Security Review</div>
                    <div className="quick-prompt-desc">Analyze sovereign air-gapped guarantees and auditability</div>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`message-bubble ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}
                >
                  <div className="message-header">
                    <span className={`message-role ${msg.role}`}>
                      {msg.role === 'assistant' ? 'SOVEREIGN INTELLIGENCE' : 'OPERATOR'}
                    </span>
                    <span>{msg.timestamp}</span>
                  </div>

                  {/* Collapsible Reasoning Accordion */}
                  {msg.reasoning && (
                    <div className="reasoning-accordion">
                      <div className="reasoning-trigger" onClick={() => toggleReasoning(msg.id)}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Cpu size={13} />
                          <span>REASONING TRACE ({msg.reasoning.length} chars)</span>
                        </div>
                        {expandedReasoning[msg.id] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      </div>
                      {expandedReasoning[msg.id] && (
                        <div className="reasoning-content">{msg.reasoning}</div>
                      )}
                    </div>
                  )}

                  {/* Tool Call Badges */}
                  {msg.toolCalls &&
                    msg.toolCalls.map((tc, idx) => (
                      <div key={idx} className="tool-execution-badge">
                        <Terminal size={12} />
                        <span>
                          [EXEC: {tc.name}] {JSON.stringify(tc.params)}
                        </span>
                      </div>
                    ))}

                  {/* Primary Output Text */}
                  <div className="message-output">
                    {msg.content || (msg.status === 'running' || msg.status === 'pending' ? 'Synthesizing sovereign reasoning...' : '')}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Smart Prompt Input Dock */}
          <div className="prompt-dock-container">
            <div className="task-controls-ribbon">
              <div className="type-pills">
                {(['general', 'rag', 'agent', 'sandbox'] as const).map((t) => (
                  <button
                    key={t}
                    className={`type-pill ${taskType === t ? 'active' : ''}`}
                    onClick={() => {
                      setTaskType(t);
                      if (t === 'sandbox') setSandboxEnabled(true);
                    }}
                  >
                    {t}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <label className="toggle-item">
                  <input
                    type="checkbox"
                    checked={sandboxEnabled}
                    onChange={(e) => setSandboxEnabled(e.target.checked)}
                  />
                  <span>Sandbox (Docker 256MB)</span>
                </label>

                <div className="toggle-item" style={{ gap: '0.3rem' }}>
                  <span>Temp: {temperature}</span>
                  <input
                    type="range"
                    min="0"
                    max="1.5"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    style={{ width: '60px' }}
                  />
                </div>
              </div>
            </div>

            <div className="input-box-wrapper">
              <textarea
                className="prompt-textarea"
                rows={2}
                placeholder="Enter prompt or autonomous instruction... (Shift+Enter for new line)"
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendPrompt();
                  }
                }}
              />
              <button
                className="send-btn"
                disabled={!inputPrompt.trim() || isStreaming}
                onClick={() => handleSendPrompt()}
              >
                <Send size={14} />
                <span>{isStreaming ? 'Streaming...' : 'Execute'}</span>
              </button>
            </div>
          </div>
        </main>

        {/* Right Inspector Drawer */}
        <aside className="right-drawer">
          <div className="drawer-tabs">
            <button
              className={`drawer-tab ${activeTab === 'sandbox' ? 'active' : ''}`}
              onClick={() => setActiveTab('sandbox')}
            >
              Docker Sandbox
            </button>
            <button
              className={`drawer-tab ${activeTab === 'rag' ? 'active' : ''}`}
              onClick={() => setActiveTab('rag')}
            >
              Knowledge Vault
            </button>
            <button
              className={`drawer-tab ${activeTab === 'security' ? 'active' : ''}`}
              onClick={() => setActiveTab('security')}
            >
              Audit Trail
            </button>
          </div>

          <div className="drawer-content">
            {activeTab === 'sandbox' && (
              <div>
                <div className="inspector-card">
                  <div className="inspector-card-title">Sandbox Limits Enforcement</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
                    <div>Memory: <strong>256 MB</strong></div>
                    <div>Swap: <strong>Disabled (0)</strong></div>
                    <div>Network: <strong>None (--network=none)</strong></div>
                    <div>Filesystem: <strong>Read-Only</strong></div>
                    <div>Auto Remove: <strong>--rm (Immediate)</strong></div>
                    <div>PIDs Limit: <strong>64 processes</strong></div>
                  </div>
                </div>

                <div className="inspector-card">
                  <div className="inspector-card-title">Live Execution Console</div>
                  <div className="console-output">{sandboxConsole}</div>
                </div>
              </div>
            )}

            {activeTab === 'rag' && (
              <div>
                <div className="inspector-card">
                  <div className="inspector-card-title">Hybrid Retrieval Specs</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    <p>• <strong>Vector Search:</strong> Qdrant (Cosine 768-dim)</p>
                    <p>• <strong>Keyword Search:</strong> BM25Okapi</p>
                    <p>• <strong>Fusion:</strong> Reciprocal Rank Fusion (k=60)</p>
                    <p>• <strong>Embedding Batching:</strong> 32 chunks / call</p>
                  </div>
                </div>

                <div className="inspector-card">
                  <div className="inspector-card-title">Ingested Knowledge Collections</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Qdrant Collection: <code>sovereign_knowledge_base</code>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <div className="inspector-card">
                  <div className="inspector-card-title">Air-Gap Egress Status</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-emerald)', fontSize: '0.8rem', fontWeight: 600 }}>
                    <Shield size={16} />
                    <span>ZERO OUTBOUND EGRESS VIOLATIONS</span>
                  </div>
                </div>

                <div className="inspector-card">
                  <div className="inspector-card-title">Cryptographic Audit Trail (data/audit.jsonl)</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {auditLogs.map((log, idx) => (
                      <div key={idx} style={{ fontSize: '0.7rem', padding: '0.4rem', background: 'var(--bg-surface)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                        <div style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{log.event_type}</div>
                        <div style={{ color: 'var(--text-muted)' }}>{log.timestamp}</div>
                        {log.prompt_hash && (
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--text-secondary)' }}>
                            SHA256: {log.prompt_hash.substring(0, 16)}...
                          </div>
                        )}
                      </div>
                    ))}
                    {auditLogs.length === 0 && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        No audit events recorded yet.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
