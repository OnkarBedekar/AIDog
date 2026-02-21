"use client"

import { useState } from "react"
import { ConfidenceMeter } from "../interactive/ConfidenceMeter"
import { apiClient } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"

interface RecommendationCardProps {
  recommendation: any
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const [previewOpen, setPreviewOpen] = useState(false)
  const [testResults, setTestResults] = useState<any>(null)
  const queryClient = useQueryClient()

  const acceptMutation = useMutation({
    mutationFn: () => apiClient.post<any>(`/recommendations/${recommendation.id}/accept`),
    onSuccess: (data) => {
      queryClient.invalidateQueries()
      if (data?.test_results) setTestResults(data.test_results)
    },
  })

  const rejectMutation = useMutation({
    mutationFn: () => apiClient.post(`/recommendations/${recommendation.id}/reject`),
    onSuccess: () => queryClient.invalidateQueries(),
  })

  const accepted = acceptMutation.isSuccess
  const passed = testResults?.passed === true
  const testStatus = testResults?.status

  return (
    <div
      className="bg-postit border-2 border-pencil p-4 shadow-hard rotate-[-0.5deg] hover:rotate-0 transition-all"
      style={{ borderRadius: '4px' }}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 pr-2">
          <h3 className="font-kalam font-bold text-pencil text-sm">{recommendation.title || recommendation.type}</h3>
          <p className="font-patrick text-pencil/70 text-xs mt-1">
            {recommendation.description || recommendation.content?.description}
          </p>
        </div>
        <ConfidenceMeter value={recommendation.confidence || 0} />
      </div>

      {/* TestSprite results panel */}
      {accepted && (
        <div className={`mt-3 p-3 border-2 ${passed ? 'border-green-600 bg-green-50' : testStatus === 'error' ? 'border-accent bg-red-50' : 'border-blue-pen bg-blue-50'}`}
          style={{ borderRadius: '4px' }}>
          {acceptMutation.isPending || !testResults ? (
            <p className="font-patrick text-xs text-pencil/70">Running TestSprite tests...</p>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-1">
                <span className={`font-kalam font-bold text-sm ${passed ? 'text-green-700' : 'text-accent'}`}>
                  {passed ? 'Tests Passed' : testStatus === 'error' ? 'Test Error' : 'Tests Failed'}
                </span>
                <span className="font-patrick text-xs text-pencil/60">via TestSprite</span>
              </div>
              {testResults.total_tests > 0 && (
                <p className="font-patrick text-xs text-pencil/80">
                  {testResults.passed_tests}/{testResults.total_tests} tests passed
                </p>
              )}
              {testResults.error && (
                <p className="font-patrick text-xs text-accent">{testResults.error}</p>
              )}
            </>
          )}
        </div>
      )}

      <div className="flex gap-2 mt-3">
        <button
          onClick={() => setPreviewOpen(true)}
          className="flex-1 px-3 py-1.5 bg-paper border-2 border-pencil font-patrick text-pencil text-xs shadow-hard hover:translate-x-[-1px] hover:translate-y-[-1px] transition-all"
          style={{ borderRadius: '4px' }}
        >
          Preview
        </button>
        {!accepted ? (
          <>
            <button
              onClick={() => acceptMutation.mutate()}
              disabled={acceptMutation.isPending}
              className="flex-1 px-3 py-1.5 bg-blue-pen border-2 border-pencil text-paper font-patrick text-xs shadow-hard-blue hover:translate-x-[-1px] hover:translate-y-[-1px] transition-all disabled:opacity-50"
              style={{ borderRadius: '4px' }}
            >
              {acceptMutation.isPending ? 'Running...' : 'Accept + Test'}
            </button>
            <button
              onClick={() => rejectMutation.mutate()}
              className="flex-1 px-3 py-1.5 bg-paper border-2 border-pencil text-accent font-patrick text-xs shadow-hard hover:translate-x-[-1px] hover:translate-y-[-1px] transition-all"
              style={{ borderRadius: '4px' }}
            >
              Reject
            </button>
          </>
        ) : (
          <span className="flex-1 px-3 py-1.5 text-center font-patrick text-green-700 text-xs font-bold">
            Accepted
          </span>
        )}
      </div>

      {previewOpen && (
        <div className="fixed inset-0 bg-pencil/30 flex items-center justify-center z-50">
          <div className="bg-paper border-2 border-pencil p-6 max-w-2xl w-full max-h-[80vh] overflow-auto shadow-hard-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-kalam font-bold text-xl text-pencil">Preview</h2>
              <button onClick={() => setPreviewOpen(false)} className="font-patrick text-pencil/60 hover:text-pencil text-xl">
                ✕
              </button>
            </div>
            <pre className="bg-white border-2 border-dashed border-muted-paper p-4 text-xs font-mono text-pencil overflow-auto">
              {JSON.stringify(recommendation.content || recommendation, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
