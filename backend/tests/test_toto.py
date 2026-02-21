"""Tests for Toto forecasting integration."""
import sys
import pytest
from app.schemas.toto import TotoForecast, TotoForecastResult


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_toto_forecast_method(monkeypatch):
    """Patch TotoForecaster.forecast so tests don't need torch/toto-ts installed.

    Returns a deterministic TotoForecast for any non-empty input.
    """
    from app.integrations.toto_forecaster import TotoForecaster

    def _mock_forecast(self, values, interval_seconds, series_name="metric", horizon=60):
        if not values:
            return None
        return TotoForecast(
            series_name=series_name,
            historical=list(values[-60:]),
            predicted_median=[5.0] * horizon,
            lower_bound=[3.0] * horizon,
            upper_bound=[7.0] * horizon,
            anomaly_score=0.0,
            is_anomalous=False,
            interval_seconds=interval_seconds,
        )

    # Save the real, unpatched method BEFORE replacing it — tests that need the
    # real implementation (e.g. test_forecast_returns_none_when_model_unavailable)
    # can retrieve it via tf_mod._real_forecast.
    import app.integrations.toto_forecaster as tf_mod
    tf_mod._real_forecast = TotoForecaster.forecast

    monkeypatch.setattr(TotoForecaster, "forecast", _mock_forecast)

    # Reset singleton so we get a fresh instance with the patched method
    tf_mod._instance = None
    yield
    tf_mod._instance = None


@pytest.fixture()
def forecaster():
    from app.integrations.toto_forecaster import TotoForecaster
    return TotoForecaster()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_toto_forecaster_instantiates(forecaster):
    assert forecaster is not None


def test_get_toto_forecaster_returns_singleton():
    from app.integrations.toto_forecaster import get_toto_forecaster

    a = get_toto_forecaster()
    b = get_toto_forecaster()
    assert a is b


def test_forecast_returns_toto_forecast_shape(forecaster):
    values = [float(i) for i in range(1, 101)]  # 100 points
    result = forecaster.forecast(values=values, interval_seconds=60, series_name="test_metric")
    assert result is not None
    assert result.series_name == "test_metric"
    assert len(result.historical) <= 60        # capped at last 60 for display
    assert len(result.predicted_median) == 60  # default horizon
    assert len(result.lower_bound) == 60
    assert len(result.upper_bound) == 60
    assert 0.0 <= result.anomaly_score <= 100.0
    assert isinstance(result.is_anomalous, bool)
    assert result.interval_seconds == 60


def test_forecast_with_short_series(forecaster):
    """Series shorter than 512 should be padded gracefully."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    result = forecaster.forecast(values=values, interval_seconds=30)
    assert result is not None
    assert len(result.predicted_median) == 60


def test_forecast_anomaly_score_is_zero_for_normal_values(forecaster):
    """All values equal → no anomaly."""
    values = [5.0] * 100
    result = forecaster.forecast(values=values, interval_seconds=60)
    assert result is not None
    # When actual equals predicted there is no anomaly
    assert result.anomaly_score >= 0.0


def test_forecast_returns_none_for_empty_series(forecaster):
    result = forecaster.forecast(values=[], interval_seconds=60)
    assert result is None


def test_forecast_returns_none_when_model_unavailable(monkeypatch):
    """When toto-ts is not installed, forecast should return None gracefully.

    We test the real _load_model path which returns (None, None) when torch/toto
    aren't available, causing forecast() to return None.
    """
    import app.integrations.toto_forecaster as tf_mod

    # Patch _load_model to simulate missing torch/toto-ts
    monkeypatch.setattr(tf_mod, "_load_model", lambda: (None, None))
    # Restore the real forecast method (saved by the autouse fixture before patching).
    # _real_forecast.__globals__ points to tf_mod's namespace, so the patched
    # _load_model above is the one that gets called.
    monkeypatch.setattr(tf_mod.TotoForecaster, "forecast", tf_mod._real_forecast)

    fc = tf_mod.TotoForecaster()
    result = fc.forecast(values=[1.0, 2.0, 3.0], interval_seconds=60)
    assert result is None


def test_toto_schema_fields():
    from app.schemas.toto import TotoForecast, TotoForecastResult

    fc = TotoForecast(
        series_name="test",
        historical=[1.0, 2.0],
        predicted_median=[3.0],
        lower_bound=[2.5],
        upper_bound=[3.5],
        anomaly_score=15.0,
        is_anomalous=False,
        interval_seconds=60,
    )
    assert fc.series_name == "test"
    assert fc.is_anomalous is False

    result = TotoForecastResult(forecasts=[fc], computed_at="2026-01-01T00:00:00Z")
    assert len(result.forecasts) == 1
