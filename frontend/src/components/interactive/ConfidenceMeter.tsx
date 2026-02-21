"use client"

interface ConfidenceMeterProps {
  value: number
}

export function ConfidenceMeter({ value }: ConfidenceMeterProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-slate-400 w-8">{value}%</span>
    </div>
  )
}
