"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import * as Tabs from "@radix-ui/react-tabs"
import { GuidedSteps } from "./interactive/GuidedSteps"
import { EvidenceView } from "./EvidenceView"
import { RecommendationCard } from "./cards/RecommendationCard"
import { ForecastPanel } from "./ForecastPanel"
import { AgentTracePanel } from "./AgentTracePanel"
import { apiClient } from "@/lib/api"

interface IncidentRoomProps {
  data: any
  isLoading: boolean
  incidentId: string
}

const TABS = [
  { value: "overview", label: "Overview" },
  { value: "evidence", label: "Evidence" },
  { value: "forecast", label: "Forecast" },
  { value: "guided-steps", label: "Guided Steps" },
  { value: "recommendations", label: "Recommendations" },
  { value: "tests", label: "Tests" },
  { value: "memory", label: "Memory" },
]

export function IncidentRoom({ data, isLoading, incidentId }: IncidentRoomProps) {
  const [activeTab, setActiveTab] = useState("overview")
  const [showTrace, setShowTrace] = useState(false)

  const numericId = Number(incidentId)

  // Lazy-fetch forecast only when the Forecast tab is active
  const { data: forecastData, isLoading: forecastLoading } = useQuery({
    queryKey: ["incident-forecast", numericId],
    queryFn: () => apiClient.getIncidentForecast(numericId),
    enabled: activeTab === "forecast" && Boolean(numericId),
    staleTime: 5 * 60 * 1000, // 5 min — Toto is expensive
  })

  // Lazy-fetch agent trace when Guided Steps tab is active
  const { data: traceData, isLoading: traceLoading } = useQuery({
    queryKey: ["agent-trace", numericId],
    queryFn: () => apiClient.getAgentTrace(numericId),
    enabled: activeTab === "guided-steps" && Boolean(numericId),
    staleTime: 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="font-kalam text-pencil/50 text-xl">Loading incident...</div>
      </div>
    )
  }

  const {
    incident,
    envelope,
    evidence,
    guided_steps = [],
    recommendations = [],
  } = data || {}

  const severityColor =
    incident?.severity === "critical" ? "bg-accent text-paper" : "bg-postit text-pencil"

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border-2 border-pencil p-6 shadow-hard-lg relative rotate-[-0.3deg]">
        <div className="absolute -top-4 left-8 w-20 h-6 bg-postit border border-muted-paper rotate-[-2deg]" />
        <div className="flex items-center justify-between mb-4">
          <h1 className="font-kalam font-bold text-2xl text-pencil">{incident?.title}</h1>
          <span
            className={`px-4 py-1.5 ${severityColor} font-kalam font-bold border-2 border-pencil shadow-hard text-sm`}
            style={{ borderRadius: "255px 15px 225px 15px / 15px 225px 15px 255px" }}
          >
            {incident?.severity}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-4 text-sm border-t border-dashed border-muted-paper pt-4">
          <div>
            <span className="font-kalam text-pencil/60">Started:</span>{" "}
            <span className="font-patrick text-pencil">
              {new Date(incident?.started_at).toLocaleString()}
            </span>
          </div>
          <div>
            <span className="font-kalam text-pencil/60">Services:</span>{" "}
            <span className="font-patrick text-pencil">{incident?.services?.join(", ")}</span>
          </div>
          <div>
            <span className="font-kalam text-pencil/60">Blast Radius:</span>{" "}
            <span className="font-patrick text-pencil">{envelope?.blast_radius || "Unknown"}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
        <Tabs.List className="flex gap-1 border-b-2 border-pencil flex-wrap">
          {TABS.map((tab) => (
            <Tabs.Trigger
              key={tab.value}
              value={tab.value}
              className="px-4 py-2 font-kalam text-pencil/60 hover:text-pencil transition-colors data-[state=active]:text-pencil data-[state=active]:border-b-2 data-[state=active]:border-pencil data-[state=active]:mb-[-2px] data-[state=active]:bg-postit"
            >
              {tab.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        {/* Overview */}
        <Tabs.Content value="overview" className="mt-6">
          <div className="bg-white border-2 border-pencil p-6 shadow-hard">
            <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Description</h2>
            <p className="font-patrick text-pencil/80 leading-relaxed">
              {envelope?.description || "No description available."}
            </p>
            {envelope?.primary_symptom && (
              <div className="mt-4 p-3 bg-postit border-2 border-pencil shadow-hard inline-block rotate-[-0.5deg]">
                <span className="font-kalam text-pencil font-bold">Primary symptom: </span>
                <span className="font-patrick text-pencil">{envelope.primary_symptom}</span>
              </div>
            )}
          </div>
        </Tabs.Content>

        {/* Evidence */}
        <Tabs.Content value="evidence" className="mt-6">
          <EvidenceView evidence={evidence} />
        </Tabs.Content>

        {/* Forecast — new Toto tab */}
        <Tabs.Content value="forecast" className="mt-6">
          <ForecastPanel
            forecasts={forecastData?.forecasts ?? []}
            isLoading={forecastLoading}
          />
        </Tabs.Content>

        {/* Guided Steps + Agent Trace */}
        <Tabs.Content value="guided-steps" className="mt-6 space-y-6">
          <GuidedSteps steps={guided_steps} incidentId={incidentId} />

          {/* Agent Trace collapsible */}
          <div>
            <button
              className="flex items-center gap-2 font-kalam text-pencil/60 hover:text-pencil text-sm mb-3"
              onClick={() => setShowTrace((v) => !v)}
            >
              <span>{showTrace ? "▲" : "▼"}</span>
              Agent Trace (AgentCore session)
            </button>
            {showTrace && (
              <AgentTracePanel
                events={traceData?.events ?? []}
                sessionId={traceData?.session_id}
                isLoading={traceLoading}
              />
            )}
          </div>
        </Tabs.Content>

        {/* Recommendations */}
        <Tabs.Content value="recommendations" className="mt-6">
          <div className="space-y-4">
            {recommendations.length > 0 ? (
              recommendations.map((rec: any) => (
                <RecommendationCard key={rec.id} recommendation={rec} />
              ))
            ) : (
              <div className="bg-paper border-2 border-dashed border-muted-paper p-8 text-center">
                <p className="font-patrick text-pencil/50 italic">No recommendations yet</p>
              </div>
            )}
          </div>
        </Tabs.Content>

        {/* Tests */}
        <Tabs.Content value="tests" className="mt-6">
          <div className="bg-white border-2 border-pencil p-6 shadow-hard">
            <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Test Results</h2>
            <p className="font-patrick text-pencil/50 italic">
              Test results will appear here after running TestSprite
            </p>
          </div>
        </Tabs.Content>

        {/* Memory */}
        <Tabs.Content value="memory" className="mt-6">
          <div className="bg-white border-2 border-pencil p-6 shadow-hard">
            <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Memory Insights</h2>
            <p className="font-patrick text-pencil/50 italic">
              Memory insights will appear here as you investigate
            </p>
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
