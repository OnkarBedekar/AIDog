"use client"

interface EvidenceViewProps {
  evidence: any
}

export function EvidenceView({ evidence }: EvidenceViewProps) {
  return (
    <div className="space-y-4">
      <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
        <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[-1deg]" />
        <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Traces</h2>
        <div className="space-y-2">
          {evidence?.traces?.slice(0, 5).map((trace: any, idx: number) => (
            <div key={idx} className="p-3 bg-paper border-2 border-dashed border-muted-paper font-mono">
              <div className="font-patrick text-pencil text-sm font-bold">{trace.service || trace.trace_id}</div>
              <div className="font-patrick text-pencil/60 text-xs">{trace.resource} — {trace.duration ? `${trace.duration}ms` : ''} {trace.status}</div>
            </div>
          ))}
          {(!evidence?.traces?.length) && (
            <p className="font-patrick text-pencil/40 text-sm italic">No traces available</p>
          )}
        </div>
      </div>

      <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
        <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[1deg]" />
        <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Logs</h2>
        <div className="space-y-2">
          {evidence?.logs?.slice(0, 5).map((log: any, idx: number) => (
            <div key={idx} className="p-3 bg-paper border-2 border-dashed border-muted-paper font-mono">
              <div className="flex items-center gap-2 mb-1">
                <span className={`px-2 py-0.5 text-xs font-patrick border border-pencil ${
                  log.level === 'error' ? 'bg-accent text-paper' :
                  log.level === 'warn' ? 'bg-postit text-pencil' :
                  'bg-muted-paper text-pencil'
                }`} style={{ borderRadius: '4px' }}>
                  {log.level || 'info'}
                </span>
                <span className="font-patrick text-pencil/50 text-xs">{log.service}</span>
              </div>
              <div className="font-patrick text-pencil text-sm">{log.message}</div>
            </div>
          ))}
          {(!evidence?.logs?.length) && (
            <p className="font-patrick text-pencil/40 text-sm italic">No logs available</p>
          )}
        </div>
      </div>

      {evidence?.metrics && (
        <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
          <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[-2deg]" />
          <h2 className="font-kalam font-bold text-xl text-pencil mb-4">Metrics</h2>
          <pre className="bg-paper border-2 border-dashed border-muted-paper p-4 text-xs font-mono text-pencil overflow-auto max-h-64">
            {JSON.stringify(evidence.metrics, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
