"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface LiveChartsProps {
  data: any
}

function parseSeriesData(series: any) {
  if (!series) return []
  const raw = series.series || series
  if (Array.isArray(raw)) {
    return raw.map(([ts, value]: [number, number]) => ({
      time: new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      value: Math.round((value || 0) * 100) / 100,
    }))
  }
  return []
}

export function LiveCharts({ data }: LiveChartsProps) {
  const errorRateData = parseSeriesData(data?.error_rate)
  const latencyData = parseSeriesData(data?.p95_latency)
  const throughputData = parseSeriesData(data?.throughput)

  const chartProps = {
    stroke: "#e5e0d8",
    strokeDasharray: "4 4",
  }

  const tooltipStyle = {
    backgroundColor: "#fdfbf7",
    border: "2px solid #2d2d2d",
    borderRadius: "4px",
    fontFamily: "'Patrick Hand', cursive",
    color: "#2d2d2d",
  }

  return (
    <div className="bg-white border-2 border-pencil p-6 shadow-hard relative">
      <div className="absolute -top-3 left-4 w-12 h-5 bg-postit border border-muted-paper rotate-[-1deg]" />
      <h2 className="font-kalam font-bold text-xl text-pencil mb-6">Live Health</h2>
      <div className="grid grid-cols-1 gap-6">
        <div>
          <h3 className="font-kalam text-pencil/70 mb-2">Error Rate</h3>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={errorRateData}>
              <CartesianGrid {...chartProps} />
              <XAxis dataKey="time" stroke="#2d2d2d" tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11 }} />
              <YAxis stroke="#2d2d2d" tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="value" stroke="#ff4d4d" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h3 className="font-kalam text-pencil/70 mb-2">P95 Latency (ms)</h3>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={latencyData}>
              <CartesianGrid {...chartProps} />
              <XAxis dataKey="time" stroke="#2d2d2d" tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11 }} />
              <YAxis stroke="#2d2d2d" tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="value" stroke="#2d5da1" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {throughputData.length > 0 && (
          <div>
            <h3 className="font-kalam text-pencil/70 mb-2">Throughput (req/s)</h3>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={throughputData}>
                <CartesianGrid {...chartProps} />
                <XAxis dataKey="time" stroke="#2d2d2d" tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11 }} />
                <YAxis stroke="#2d2d2d" tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="value" stroke="#2d2d2d" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  )
}
