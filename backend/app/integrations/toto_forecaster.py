"""Toto time-series foundation model integration.

Toto is Datadog's open-weights model for multi-variate time-series forecasting.
Model: Datadog/Toto-Open-Base-1.0 (~605 MB, Apache 2.0)
SDK:   pip install toto-ts

Pre-setup (run once before starting the backend):
    python -c "from toto.model.toto import Toto; Toto.from_pretrained('Datadog/Toto-Open-Base-1.0')"
"""
import threading
import logging
from typing import List, Optional
from datetime import datetime

from app.schemas.toto import TotoForecast

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_toto_model = None
_toto_forecaster_impl = None


def _load_model():
    """Lazy-load the Toto model from HuggingFace cache (thread-safe)."""
    global _toto_model, _toto_forecaster_impl
    if _toto_model is not None:
        return _toto_model, _toto_forecaster_impl
    with _lock:
        if _toto_model is not None:
            return _toto_model, _toto_forecaster_impl
        try:
            import torch
            from toto.model.toto import Toto
            from toto.inference.forecaster import TotoForecaster as _TF

            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Toto model on {device} ...")
            model = Toto.from_pretrained("Datadog/Toto-Open-Base-1.0").to(device)
            _toto_forecaster_impl = _TF(model.model)
            _toto_model = model
            logger.info("Toto model loaded successfully.")
        except Exception as exc:
            logger.warning(f"Toto model unavailable (install toto-ts to enable): {exc}")
    return _toto_model, _toto_forecaster_impl


class TotoForecaster:
    """Wrapper around the Toto foundation model for metric anomaly detection."""

    def forecast(
        self,
        values: List[float],
        interval_seconds: int,
        series_name: str = "metric",
        horizon: int = 60,
    ) -> Optional[TotoForecast]:
        """Run Toto inference on a metric time series.

        Args:
            values: Historical metric values (will be padded/truncated to 512).
            interval_seconds: Seconds between consecutive data points.
            series_name: Display name for the metric.
            horizon: Number of future time steps to forecast.

        Returns:
            TotoForecast or None if the model is unavailable.
        """
        if not values:
            return None

        model, forecaster = _load_model()
        if model is None or forecaster is None:
            return None

        try:
            import torch
            from toto.data.util.dataset import MaskedTimeseries

            device = next(model.model.parameters()).device

            # Pad/truncate to 512 points (model's context length)
            target_len = 512
            if len(values) >= target_len:
                series_values = list(values[-target_len:])
            else:
                pad_value = values[0]
                series_values = [pad_value] * (target_len - len(values)) + list(values)

            # Z-score normalise (avoids scale sensitivity)
            n = len(series_values)
            mean_val = sum(series_values) / n
            variance = sum((v - mean_val) ** 2 for v in series_values) / n
            std_val = max(variance ** 0.5, 1e-6)
            normalized = [(v - mean_val) / std_val for v in series_values]

            input_tensor = torch.tensor([normalized], dtype=torch.float32).to(device)
            ones = torch.ones_like(input_tensor, dtype=torch.bool)

            inputs = MaskedTimeseries(
                series=input_tensor,
                padding_mask=ones,
                id_mask=torch.zeros_like(input_tensor),
                timestamp_seconds=torch.zeros_like(input_tensor),
                time_interval_seconds=torch.full((1,), float(interval_seconds)).to(device),
            )

            with torch.no_grad():
                result = forecaster.forecast(
                    inputs,
                    prediction_length=horizon,
                    num_samples=64,
                    samples_per_batch=64,
                )

            def _denorm(tensor_1d) -> List[float]:
                return [round(float(v) * std_val + mean_val, 4) for v in tensor_1d]

            # result.median shape: [batch, channels, horizon] → take [0, 0]
            predicted_median = _denorm(result.median[0, 0])
            lower_bound = _denorm(result.quantile(0.1)[0, 0])
            upper_bound = _denorm(result.quantile(0.9)[0, 0])

            # Anomaly score: fraction of the last 5 actual values that exceed the upper bound
            last_actual = list(values[-5:])
            # Project the last 5 predicted upper bounds (first 5 forecast steps ≈ near-term)
            span = max(upper_bound[0] - lower_bound[0], 1e-6)
            deviations = []
            for i, actual in enumerate(last_actual):
                ub = upper_bound[i] if i < len(upper_bound) else upper_bound[-1]
                if actual > ub:
                    deviations.append(min((actual - ub) / span * 100, 100.0))
            anomaly_score = round(sum(deviations) / max(len(deviations), 1), 1) if deviations else 0.0

            return TotoForecast(
                series_name=series_name,
                historical=list(values[-60:]),
                predicted_median=predicted_median,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                anomaly_score=anomaly_score,
                is_anomalous=anomaly_score > 70.0,
                interval_seconds=interval_seconds,
            )
        except Exception as exc:
            logger.error(f"Toto inference failed for '{series_name}': {exc}")
            return None


# Module-level singleton
_instance: Optional[TotoForecaster] = None


def get_toto_forecaster() -> TotoForecaster:
    """Return the shared TotoForecaster instance."""
    global _instance
    if _instance is None:
        _instance = TotoForecaster()
    return _instance


def prewarm_toto() -> None:
    """Trigger model load in a background thread (call at startup)."""
    thread = threading.Thread(target=_load_model, daemon=True, name="toto-prewarm")
    thread.start()
    logger.info("Toto prewarm started in background thread.")
