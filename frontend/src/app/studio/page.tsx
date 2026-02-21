"use client"

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/lib/api"
import { AppShell } from "@/components/AppShell"

export default function StudioPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["memory-profile"],
    queryFn: () => apiClient.get("/memory/profile"),
  })

  return (
    <AppShell>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-white">Personalization Studio</h1>

        {isLoading ? (
          <div className="text-slate-400">Loading...</div>
        ) : (
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Preferences</h2>
              <pre className="text-xs text-slate-300 overflow-auto">
                {JSON.stringify(data?.preferences || {}, null, 2)}
              </pre>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Patterns</h2>
              <div className="space-y-2">
                {data?.patterns?.map((pattern: any, idx: number) => (
                  <div key={idx} className="p-3 bg-slate-900/50 rounded border border-slate-700">
                    <p className="text-sm text-white">{pattern.description}</p>
                    <p className="text-xs text-slate-400">Confidence: {pattern.confidence}%</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
