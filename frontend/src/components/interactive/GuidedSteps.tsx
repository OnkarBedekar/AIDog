"use client"

import { apiClient } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"

interface GuidedStepsProps {
  steps: any[]
  incidentId: string
}

export function GuidedSteps({ steps, incidentId }: GuidedStepsProps) {
  const queryClient = useQueryClient()

  const executeMutation = useMutation({
    mutationFn: (stepId: string) =>
      apiClient.post(`/incidents/${incidentId}/steps/execute`, { step_id: stepId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incident", incidentId] })
    },
  })

  if (!steps.length) {
    return (
      <div className="bg-paper border-2 border-dashed border-muted-paper p-8 text-center">
        <p className="font-patrick text-pencil/50 italic">No investigation steps generated yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {steps.map((step, idx) => (
        <div
          key={step.id || idx}
          className={`bg-white border-2 border-pencil p-5 shadow-hard relative transition-all ${idx % 2 === 0 ? "rotate-[-0.3deg]" : "rotate-[0.3deg]"}`}
          style={{ borderRadius: '4px' }}
        >
          {/* Step number */}
          <div className="absolute -left-3 -top-3 w-8 h-8 bg-postit border-2 border-pencil rounded-full flex items-center justify-center font-kalam font-bold text-pencil text-sm shadow-hard">
            {idx + 1}
          </div>

          <div className="flex items-start justify-between gap-4 ml-4">
            <div className="flex-1">
              <h3 className="font-kalam font-bold text-pencil text-base mb-1">{step.title}</h3>
              <p className="font-patrick text-pencil/70 text-sm mb-2">{step.description}</p>
              {step.rationale && (
                <p className="font-patrick text-pencil/50 text-xs italic border-l-2 border-muted-paper pl-2">
                  {step.rationale}
                </p>
              )}
            </div>
            <div className="flex flex-col items-end gap-2">
              <span className="px-2 py-1 bg-blue-pen text-paper font-patrick text-xs border border-pencil shadow-hard-blue" style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}>
                Priority {step.priority || 5}
              </span>
              <button
                onClick={() => executeMutation.mutate(step.id)}
                disabled={executeMutation.isPending}
                className="px-4 py-2 bg-accent text-paper font-kalam font-bold text-sm border-2 border-pencil shadow-hard-red hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-hard-lg transition-all active:translate-x-0 active:translate-y-0 active:shadow-none disabled:opacity-50"
                style={{ borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px' }}
              >
                {executeMutation.isPending ? "Running..." : "Execute"}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
