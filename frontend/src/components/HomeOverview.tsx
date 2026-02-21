"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { apiClient } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { LiveCharts } from "./charts/LiveCharts"
import { AlertFeed } from "./cards/AlertFeed"
import { RecommendationCard } from "./cards/RecommendationCard"

interface HomeOverviewProps {
  data: any
  isLoading: boolean
}

export function HomeOverview({ data, isLoading }: HomeOverviewProps) {
  const router = useRouter()
  const queryClient = useQueryClient()

  const simulateIncident = useMutation({
    mutationFn: async () => {
      return apiClient.post<any>("/incidents/detect")
    },
    onSuccess: (incident) => {
      queryClient.invalidateQueries({ queryKey: ["home-overview"] })
      router.push(`/incidents/${incident.id}`)
    },
    onError: (err: Error) => {
      alert(`Failed to detect incident: ${err.message}`)
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="font-kalam text-pencil/50 text-xl">Loading your dashboard...</div>
      </div>
    )
  }

  const {
    servicesYouTouch = [],
    topEndpoints = [],
    liveChartsData = {},
    activeAlerts = [],
    recentIncidents = [],
    learnedPatterns = [],
    suggestedImprovements = [],
  } = data || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-kalam font-bold text-4xl text-pencil mb-1">Your System View</h1>
          <p className="font-patrick text-pencil/60">Personalized dashboard for your services</p>
        </div>
        <button
          onClick={() => simulateIncident.mutate()}
          disabled={simulateIncident.isPending}
          className="px-6 py-3 bg-accent text-paper font-kalam font-bold text-lg border-2 border-pencil shadow-hard-red hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg transition-all active:translate-x-0 active:translate-y-0 active:shadow-none disabled:opacity-50"
          style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
        >
          {simulateIncident.isPending ? "Detecting..." : "Detect Live Incident"}
        </button>
      </div>

      {/* Three column layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left column */}
        <div className="col-span-3 space-y-6">
          <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
            <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[-2deg]" />
            <h2 className="font-kalam font-bold text-lg text-pencil mb-4">Services You Touch</h2>
            <div className="flex flex-wrap gap-2">
              {servicesYouTouch.length > 0 ? servicesYouTouch.map((service: string) => (
                <span
                  key={service}
                  className="px-3 py-1 bg-paper border-2 border-pencil font-patrick text-pencil text-sm shadow-hard"
                  style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                >
                  {service}
                </span>
              )) : (
                <span className="font-patrick text-pencil/40 text-sm italic">No services yet</span>
              )}
            </div>
          </div>

          <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
            <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[1deg]" />
            <h2 className="font-kalam font-bold text-lg text-pencil mb-4">Top Endpoints</h2>
            <div className="space-y-3">
              {topEndpoints.map((endpoint: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between border-b border-dashed border-muted-paper pb-2">
                  <span className="font-patrick text-pencil text-sm">{endpoint.name}</span>
                  <span className="font-patrick text-accent text-xs font-bold">
                    {endpoint.error_rate}% err
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
            <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[-1deg]" />
            <h2 className="font-kalam font-bold text-lg text-pencil mb-4">Learned Patterns</h2>
            <ul className="space-y-2">
              {learnedPatterns.length > 0 ? learnedPatterns.map((pattern: string, idx: number) => (
                <li key={idx} className="font-patrick text-pencil/70 text-sm flex gap-2">
                  <span className="text-blue-pen">•</span>
                  <span>{pattern}</span>
                </li>
              )) : (
                <li className="font-patrick text-pencil/40 text-sm italic">Patterns will appear as you investigate incidents</li>
              )}
            </ul>
          </div>
        </div>

        {/* Center column */}
        <div className="col-span-6 space-y-6">
          <LiveCharts data={liveChartsData} />
          <AlertFeed alerts={activeAlerts} incidents={recentIncidents} />
        </div>

        {/* Right column */}
        <div className="col-span-3 space-y-6">
          <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
            <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[2deg]" />
            <h2 className="font-kalam font-bold text-lg text-pencil mb-4">Suggested Improvements</h2>
            <div className="space-y-3">
              {suggestedImprovements.length > 0 ? suggestedImprovements.map((improvement: any) => (
                <RecommendationCard key={improvement.id} recommendation={improvement} />
              )) : (
                <p className="font-patrick text-pencil/40 text-sm italic">No suggestions yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
