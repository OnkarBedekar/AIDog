"use client"

import { useRouter } from "next/navigation"

interface AlertFeedProps {
  alerts: any[]
  incidents: any[]
}

function severityStyle(severity: string) {
  if (severity === "critical") return { bg: "bg-red-50 border-accent", text: "text-accent", badge: "bg-accent text-paper" }
  if (severity === "warning") return { bg: "bg-postit border-pencil", text: "text-pencil", badge: "bg-pencil text-paper" }
  return { bg: "bg-paper border-pencil", text: "text-pencil", badge: "bg-muted-paper text-pencil" }
}

function rotate(idx: number) {
  const rotations = ["rotate-[-0.5deg]", "rotate-[0.5deg]", "rotate-[-0.3deg]", "rotate-[0.3deg]", "rotate-0"]
  return rotations[idx % rotations.length]
}

export function AlertFeed({ alerts, incidents }: AlertFeedProps) {
  const router = useRouter()

  return (
    <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
      <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[-2deg]" />
      <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Active Alerts & Recent Incidents</h2>
      <div className="space-y-3">
        {alerts?.slice(0, 5).map((alert: any, idx: number) => {
          const s = severityStyle(alert.severity)
          return (
            <div
              key={idx}
              className={`p-4 ${s.bg} border-2 shadow-hard ${rotate(idx)} transition-all hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg`}
              style={{ borderRadius: '4px' }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-kalam text-pencil text-sm font-bold">{alert.name}</h3>
                  <p className="font-patrick text-pencil/60 text-xs mt-1">{alert.query}</p>
                </div>
                <span className={`px-2 py-1 ${s.badge} font-patrick text-xs border border-pencil`} style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}>
                  {alert.severity}
                </span>
              </div>
            </div>
          )
        })}
        {incidents?.slice(0, 3).map((incident: any, idx: number) => {
          const s = severityStyle(incident.severity)
          return (
            <div
              key={incident.id}
              onClick={() => router.push(`/incidents/${incident.id}`)}
              className={`p-4 ${s.bg} border-2 shadow-hard cursor-pointer ${rotate(idx + 2)} transition-all hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg`}
              style={{ borderRadius: '4px' }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-kalam text-pencil text-sm font-bold">{incident.title}</h3>
                  <p className="font-patrick text-pencil/60 text-xs mt-1">
                    {new Date(incident.started_at).toLocaleString()}
                  </p>
                </div>
                <span className={`px-2 py-1 ${s.badge} font-patrick text-xs border border-pencil`} style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}>
                  {incident.severity}
                </span>
              </div>
            </div>
          )
        })}
        {(!alerts?.length && !incidents?.length) && (
          <p className="font-patrick text-pencil/40 text-sm italic text-center py-4">
            No active alerts. Your system looks healthy!
          </p>
        )}
      </div>
    </div>
  )
}
