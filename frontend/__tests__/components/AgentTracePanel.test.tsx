/**
 * Tests for AgentTracePanel — AgentCore session event timeline.
 */
import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { AgentTracePanel } from "../../src/components/AgentTracePanel"

const mockEvents = [
  {
    kind: "runner_start" as const,
    timestamp: "2026-01-01T10:00:00Z",
    incident_id: 1,
    tools_registered: 7,
  },
  {
    kind: "tool_call" as const,
    agent: "Datadog",
    action: "query_metrics",
    status: "complete" as const,
    timestamp: "2026-01-01T10:00:01Z",
    result_count: 3,
  },
  {
    kind: "agent_call" as const,
    agent: "IncidentSummarizer",
    action: "summarize",
    status: "complete" as const,
    timestamp: "2026-01-01T10:00:05Z",
    severity: "critical",
  },
  {
    kind: "runner_complete" as const,
    timestamp: "2026-01-01T10:00:10Z",
    incident_id: 1,
    guided_steps: 5,
  },
]

describe("AgentTracePanel", () => {
  test("renders trace steps", () => {
    render(<AgentTracePanel events={mockEvents} sessionId="session-123" />)
    expect(screen.getByText("Agent Trace")).toBeInTheDocument()
    // Should show all 4 step numbers
    expect(screen.getByText("1")).toBeInTheDocument()
    expect(screen.getByText("4")).toBeInTheDocument()
  })

  test("shows session ID", () => {
    render(<AgentTracePanel events={mockEvents} sessionId="incident-1-user-42" />)
    expect(screen.getByText(/incident-1-user-42/)).toBeInTheDocument()
  })

  test("renders 'No agent trace available' when events is empty", () => {
    render(<AgentTracePanel events={[]} />)
    expect(screen.getByText(/No agent trace available/i)).toBeInTheDocument()
  })

  test("shows loading state when isLoading is true", () => {
    render(<AgentTracePanel events={[]} isLoading={true} />)
    expect(screen.getByText(/Running investigation pipeline/i)).toBeInTheDocument()
  })

  test("shows status badge for complete events", () => {
    render(<AgentTracePanel events={mockEvents} />)
    const badges = screen.getAllByText("complete")
    expect(badges.length).toBeGreaterThanOrEqual(1)
  })

  test("clicking expand toggle shows payload", () => {
    render(<AgentTracePanel events={mockEvents} />)
    // First event with payload → click the ▼ button
    const toggles = screen.getAllByText("▼")
    fireEvent.click(toggles[0])
    // After expanding, should see ▲
    expect(screen.getAllByText("▲").length).toBeGreaterThanOrEqual(1)
  })

  test("shows correct event count in footer", () => {
    render(<AgentTracePanel events={mockEvents} />)
    expect(screen.getByText(/4 events/)).toBeInTheDocument()
  })
})
