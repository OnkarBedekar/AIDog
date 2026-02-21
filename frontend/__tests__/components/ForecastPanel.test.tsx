/**
 * Tests for ForecastPanel — Toto forecast visualization component.
 */
import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { ForecastPanel } from "../../src/components/ForecastPanel"

// Recharts uses ResizeObserver — mock it
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

const mockForecast = {
  series_name: "error_rate",
  historical: Array.from({ length: 60 }, (_, i) => i * 0.1),
  predicted_median: Array.from({ length: 60 }, () => 3.0),
  lower_bound: Array.from({ length: 60 }, () => 2.0),
  upper_bound: Array.from({ length: 60 }, () => 4.0),
  anomaly_score: 85,
  is_anomalous: true,
  interval_seconds: 60,
}

const normalForecast = {
  ...mockForecast,
  anomaly_score: 10,
  is_anomalous: false,
  series_name: "p95_latency",
}

describe("ForecastPanel", () => {
  test("renders with forecast data", () => {
    render(<ForecastPanel forecasts={[mockForecast]} />)
    expect(screen.getByText("Toto Forecast")).toBeInTheDocument()
  })

  test("shows 'Anomalous' badge for high anomaly score", () => {
    render(<ForecastPanel forecasts={[mockForecast]} />)
    expect(screen.getByText(/Anomalous/i)).toBeInTheDocument()
  })

  test("shows 'Normal' badge for low anomaly score", () => {
    render(<ForecastPanel forecasts={[normalForecast]} />)
    expect(screen.getByText(/Normal/i)).toBeInTheDocument()
  })

  test("renders 'No forecast available' when forecasts is empty", () => {
    render(<ForecastPanel forecasts={[]} />)
    expect(screen.getByText(/No forecast available/i)).toBeInTheDocument()
  })

  test("shows loading state when isLoading is true", () => {
    render(<ForecastPanel forecasts={[]} isLoading={true} />)
    expect(screen.getByText(/Running Toto forecast/i)).toBeInTheDocument()
  })

  test("shows anomaly warning banner when any forecast is anomalous", () => {
    render(<ForecastPanel forecasts={[mockForecast]} />)
    expect(screen.getByText(/Anomaly detected/i)).toBeInTheDocument()
  })

  test("renders metric name in chart header", () => {
    render(<ForecastPanel forecasts={[normalForecast]} />)
    // series_name "p95_latency" → "p95 latency"
    expect(screen.getByText(/p95 latency/i)).toBeInTheDocument()
  })
})
