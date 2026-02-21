"use client"

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts"

interface TotoForecast {
  series_name: string
  historical: number[]
  predicted_median: number[]
  lower_bound: number[]
  upper_bound: number[]
  anomaly_score: number
  is_anomalous: boolean
  interval_seconds: number
}

interface ForecastPanelProps {
  forecasts: TotoForecast[]
  isLoading?: boolean
}

function AnomalyBadge({ score }: { score: number }) {
  const color =
    score > 70
      ? "bg-accent text-paper border-accent"
      : score > 30
      ? "bg-postit text-pencil border-pencil"
      : "bg-paper text-pencil border-pencil"

  const label = score > 70 ? "Anomalous" : score > 30 ? "Watch" : "Normal"

  return (
    <span
      className={`px-3 py-1 text-xs font-kalam font-bold border-2 shadow-hard ${color}`}
      style={{ borderRadius: "255px 15px 225px 15px / 15px 225px 15px 255px" }}
    >
      {label} · {score.toFixed(0)}/100
    </span>
  )
}

function buildChartData(forecast: TotoForecast) {
  const { historical, predicted_median, lower_bound, upper_bound, interval_seconds } = forecast
  const now = Date.now()
  const histLen = historical.length
  const data: any[] = []

  // Historical points (negative time offsets)
  historical.forEach((val, i) => {
    const offsetSeconds = (i - histLen) * interval_seconds
    data.push({
      time: offsetSeconds,
      label: `${offsetSeconds}s`,
      actual: +val.toFixed(4),
    })
  })

  // Forecast points (positive time offsets)
  predicted_median.forEach((med, i) => {
    const offsetSeconds = i * interval_seconds
    data.push({
      time: offsetSeconds,
      label: `+${offsetSeconds}s`,
      predicted: +med.toFixed(4),
      lower: lower_bound[i] != null ? +lower_bound[i].toFixed(4) : undefined,
      upper: upper_bound[i] != null ? +upper_bound[i].toFixed(4) : undefined,
      // Anomaly marker: actual value exceeded upper bound
      anomaly:
        historical[histLen - 1] > (upper_bound[i] ?? Infinity)
          ? historical[histLen - 1]
          : undefined,
    })
  })

  return data
}

function ForecastChart({ forecast }: { forecast: TotoForecast }) {
  const data = buildChartData(forecast)
  const title = forecast.series_name.replace(/_/g, " ")

  return (
    <div className="bg-white border-2 border-pencil p-4 shadow-hard mb-4 last:mb-0">
      <div className="flex items-center justify-between mb-3">
        <span className="font-kalam font-bold text-pencil capitalize">{title}</span>
        <AnomalyBadge score={forecast.anomaly_score} />
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 8 }}>
          <CartesianGrid strokeDasharray="4 4" stroke="#e5e0d8" />
          <XAxis
            dataKey="label"
            tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11, fill: "#2d2d2d" }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontFamily: "'Patrick Hand', cursive", fontSize: 11, fill: "#2d2d2d" }}
            tickLine={false}
            axisLine={false}
            width={48}
          />
          <Tooltip
            contentStyle={{
              fontFamily: "'Patrick Hand', cursive",
              fontSize: 12,
              border: "2px solid #2d2d2d",
              borderRadius: 0,
              background: "#fdfbf7",
              boxShadow: "4px 4px 0 #2d2d2d",
            }}
          />
          <Legend
            wrapperStyle={{ fontFamily: "'Patrick Hand', cursive", fontSize: 12 }}
          />

          {/* Confidence band */}
          <Area
            dataKey="upper"
            data={data.filter((d) => d.upper != null)}
            fill="#e5e0d8"
            stroke="none"
            name="upper bound"
            legendType="none"
          />
          <Area
            dataKey="lower"
            data={data.filter((d) => d.lower != null)}
            fill="#fdfbf7"
            stroke="none"
            name="lower bound"
            legendType="none"
          />

          {/* Predicted median */}
          <Line
            dataKey="predicted"
            stroke="#2d5da1"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            name="predicted"
          />

          {/* Actual values */}
          <Line
            dataKey="actual"
            stroke="#2d2d2d"
            strokeWidth={2}
            dot={false}
            name="actual"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

export function ForecastPanel({ forecasts, isLoading }: ForecastPanelProps) {
  if (isLoading) {
    return (
      <div className="bg-white border-2 border-pencil p-8 shadow-hard text-center">
        <p className="font-patrick text-pencil/60 italic animate-pulse">
          Running Toto forecast… (this may take ~30s on first load)
        </p>
      </div>
    )
  }

  if (!forecasts || forecasts.length === 0) {
    return (
      <div className="bg-paper border-2 border-dashed border-muted-paper p-8 text-center">
        <p className="font-patrick text-pencil/50 italic">No forecast available yet.</p>
        <p className="font-patrick text-pencil/40 text-sm mt-1">
          Toto needs at least 10 metric data points to generate predictions.
        </p>
      </div>
    )
  }

  const hasAnomaly = forecasts.some((f) => f.is_anomalous)

  return (
    <div className="space-y-4">
      {/* Header card */}
      <div className="bg-white border-2 border-pencil p-4 shadow-hard-lg relative rotate-[-0.2deg]">
        <div className="absolute -top-3 left-6 w-16 h-5 bg-postit border border-muted-paper rotate-[1deg]" />
        <div className="flex items-center justify-between">
          <h2 className="font-kalam font-bold text-xl text-pencil">Toto Forecast</h2>
          {hasAnomaly && (
            <span className="font-patrick text-accent font-bold text-sm animate-pulse">
              ⚠ Anomaly detected
            </span>
          )}
        </div>
        <p className="font-patrick text-pencil/60 text-sm mt-1">
          Datadog&apos;s open-weights time-series model predicts expected behavior.
          Red zones show where actual values deviate from the predicted envelope.
        </p>
      </div>

      {/* Charts */}
      {forecasts.map((fc, i) => (
        <ForecastChart key={`${fc.series_name}-${i}`} forecast={fc} />
      ))}
    </div>
  )
}
