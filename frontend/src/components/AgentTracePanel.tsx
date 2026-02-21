"use client"

import { useState } from "react"

type EventStatus = "running" | "complete" | "error" | "pending"

interface TraceEvent {
  kind: "tool_call" | "agent_call" | "memory_update" | "runner_start" | "runner_complete"
  agent?: string
  action?: string
  status?: EventStatus
  timestamp?: string
  result_count?: number
  forecasts?: number
  steps_count?: number
  hypotheses_count?: number
  recommendations_count?: number
  tools_registered?: number
  [key: string]: any
}

interface AgentTracePanelProps {
  events: TraceEvent[]
  sessionId?: string | null
  isLoading?: boolean
}

const KIND_ICON: Record<string, string> = {
  tool_call: "🔧",
  agent_call: "🧠",
  memory_update: "💾",
  runner_start: "▶",
  runner_complete: "✓",
}

const STATUS_CLASS: Record<string, string> = {
  running: "bg-blue-pen text-paper",
  complete: "text-pencil border border-pencil",
  error: "bg-accent text-paper",
  pending: "text-pencil/40 border border-muted-paper",
}

function statusBadge(status?: EventStatus) {
  if (!status) return null
  const cls = STATUS_CLASS[status] ?? STATUS_CLASS.pending
  return (
    <span
      className={`px-2 py-0.5 text-xs font-patrick ${cls}`}
      style={{ borderRadius: "255px 15px 225px 15px / 15px 225px 15px 255px" }}
    >
      {status}
    </span>
  )
}

function formatTimestamp(ts?: string): string {
  if (!ts) return ""
  try {
    return new Date(ts).toLocaleTimeString()
  } catch {
    return ts
  }
}

function EventRow({ event, index }: { event: TraceEvent; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const icon = KIND_ICON[event.kind] ?? "•"
  const agentLabel = event.agent || event.kind
  const actionLabel = event.action || ""

  // Payload: everything except kind, timestamp, agent, action, status
  const { kind, timestamp, agent, action, status, ...rest } = event
  const hasPayload = Object.keys(rest).length > 0

  return (
    <div
      className={`border-l-2 ${
        event.status === "error"
          ? "border-accent"
          : event.kind === "runner_complete"
          ? "border-blue-pen"
          : "border-muted-paper"
      } pl-3 py-1.5 group`}
    >
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => hasPayload && setExpanded(!expanded)}>
        {/* Step number */}
        <span className="w-6 h-6 rounded-full bg-postit border border-pencil flex items-center justify-center font-kalam text-xs font-bold text-pencil shrink-0">
          {index + 1}
        </span>

        {/* Icon + label */}
        <span className="text-sm">{icon}</span>
        <span className="font-patrick text-pencil font-medium text-sm">{agentLabel}</span>
        {actionLabel && (
          <span className="font-patrick text-pencil/60 text-sm">→ {actionLabel}</span>
        )}

        {/* Status badge */}
        {statusBadge(status as EventStatus)}

        {/* Timestamp */}
        <span className="ml-auto font-patrick text-pencil/40 text-xs shrink-0">
          {formatTimestamp(timestamp)}
        </span>

        {/* Expand toggle */}
        {hasPayload && (
          <button className="text-pencil/40 hover:text-pencil text-xs ml-1">
            {expanded ? "▲" : "▼"}
          </button>
        )}
      </div>

      {/* Collapsed payload */}
      {expanded && hasPayload && (
        <pre className="mt-2 ml-8 p-2 bg-paper border border-dashed border-muted-paper font-mono text-xs text-pencil/70 overflow-auto max-h-32">
          {JSON.stringify(rest, null, 2)}
        </pre>
      )}
    </div>
  )
}

export function AgentTracePanel({ events, sessionId, isLoading }: AgentTracePanelProps) {
  if (isLoading) {
    return (
      <div className="bg-white border-2 border-pencil p-6 shadow-hard text-center">
        <p className="font-patrick text-pencil/60 italic animate-pulse">
          Running investigation pipeline…
        </p>
      </div>
    )
  }

  if (!events || events.length === 0) {
    return (
      <div className="bg-paper border-2 border-dashed border-muted-paper p-6 text-center">
        <p className="font-patrick text-pencil/50 italic">No agent trace available.</p>
        <p className="font-patrick text-pencil/40 text-sm mt-1">
          Open the incident to run the investigation pipeline.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-postit border-2 border-pencil p-4 shadow-hard relative rotate-[0.2deg]">
      <div className="absolute -top-3 right-8 w-12 h-5 bg-paper border border-muted-paper rotate-[-1deg]" />

      <div className="flex items-center justify-between mb-4">
        <h3 className="font-kalam font-bold text-lg text-pencil">Agent Trace</h3>
        {sessionId && (
          <span className="font-mono text-pencil/40 text-xs bg-paper border border-muted-paper px-2 py-0.5 truncate max-w-[180px]">
            {sessionId}
          </span>
        )}
      </div>

      <div className="space-y-1">
        {events.map((event, i) => (
          <EventRow key={`${event.kind}-${i}`} event={event} index={i} />
        ))}
      </div>

      <p className="font-patrick text-pencil/40 text-xs mt-3 text-right">
        {events.length} events · Minimax + AgentCore Memory
      </p>
    </div>
  )
}
