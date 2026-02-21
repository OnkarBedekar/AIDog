"""Pydantic schemas for Toto forecast results."""
from pydantic import BaseModel
from typing import List


class TotoForecast(BaseModel):
    """Result of a Toto time-series forecast for a single metric."""

    series_name: str
    historical: List[float]        # Last 60 actual values used for display
    predicted_median: List[float]  # Point forecast (horizon steps)
    lower_bound: List[float]       # 10th percentile
    upper_bound: List[float]       # 90th percentile
    anomaly_score: float           # 0–100; > 70 = anomalous
    is_anomalous: bool             # anomaly_score > 70
    interval_seconds: int          # Time interval between data points


class TotoForecastResult(BaseModel):
    """Container for multiple metric forecasts from an incident."""

    forecasts: List[TotoForecast]
    computed_at: str               # ISO timestamp
