"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { AppShell } from "@/components/AppShell"
import { useRouter } from "next/navigation"

function severityStyle(severity: string) {
  if (severity === "critical") return "bg-accent text-paper border-pencil"
  if (severity === "warning") return "bg-postit text-pencil border-pencil"
  return "bg-muted-paper text-pencil border-pencil"
}

function tapeColor(idx: number) {
  const colors = ["bg-postit", "bg-blue-pen/20", "bg-accent/10", "bg-muted-paper"]
  return colors[idx % colors.length]
}

export default function IncidentsPage() {
  const router = useRouter()
  const { data: incidents, isLoading } = useQuery({
    queryKey: ["incidents"],
    queryFn: () => apiClient.get("/incidents"),
  })

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="font-kalam font-bold text-4xl text-pencil">Incidents</h1>
          <span className="font-patrick text-pencil/50 text-sm">
            {incidents?.length || 0} total
          </span>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="font-kalam text-pencil/50 text-xl">Loading incidents...</div>
          </div>
        ) : (
          <div className="grid gap-4">
            {incidents?.map((incident: any, idx: number) => (
              <div
                key={incident.id}
                onClick={() => router.push(`/incidents/${incident.id}`)}
                className={`bg-white border-2 border-pencil p-6 shadow-hard cursor-pointer hover:translate-x-[-3px] hover:translate-y-[-3px] hover:shadow-hard-lg transition-all relative ${idx % 2 === 0 ? "rotate-[-0.3deg]" : "rotate-[0.3deg]"}`}
                style={{ borderRadius: '4px' }}
              >
                {/* Tape decoration */}
                <div className={`absolute -top-3 left-8 w-16 h-5 ${tapeColor(idx)} border border-muted-paper rotate-[-1deg]`} />

                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="font-kalam font-bold text-xl text-pencil mb-1">{incident.title}</h2>
                    <p className="font-patrick text-pencil/60 text-sm">
                      {incident.services?.join(", ")} · {new Date(incident.started_at).toLocaleString()}
                    </p>
                    <p className="font-patrick text-pencil/40 text-xs mt-1">
                      State: {incident.state}
                    </p>
                  </div>
                  <span
                    className={`px-4 py-1.5 ${severityStyle(incident.severity)} font-kalam font-bold border-2 shadow-hard text-sm`}
                    style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
                  >
                    {incident.severity}
                  </span>
                </div>
              </div>
            ))}
            {(!incidents?.length) && (
              <div className="bg-paper border-2 border-dashed border-muted-paper p-16 text-center">
                <p className="font-kalam text-pencil/40 text-2xl mb-2">All clear!</p>
                <p className="font-patrick text-pencil/40 text-sm">No incidents found. Your services are healthy.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  )
}
