import numpy as np
from sklearn.ensemble import IsolationForest

_model: IsolationForest | None = None


def _generate_synthetic_baseline(n_samples: int = 2000, seed: int = 42) -> np.ndarray:
    """Generates a synthetic baseline of 'normal' transaction amounts to fit the
    anomaly model on, so the base project works out of the box with no historical
    data. In production this trains on real historical transactions instead."""
    rng = np.random.default_rng(seed)
    normal_amounts = rng.normal(loc=150, scale=80, size=n_samples)
    normal_amounts = np.clip(normal_amounts, 1, None)
    hour_of_day = rng.integers(0, 24, size=n_samples)
    return np.column_stack([normal_amounts, hour_of_day])


def get_model() -> IsolationForest:
    global _model
    if _model is None:
        baseline = _generate_synthetic_baseline()
        _model = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42,
        )
        _model.fit(baseline)
    return _model


def score_transaction(amount: float, hour_of_day: int) -> float:
    """Returns a risk score in [0, 1], where higher = more anomalous."""
    model = get_model()
    features = np.array([[abs(amount), hour_of_day]])
    # decision_function: higher = more normal. Flip and normalize to a 0-1 risk score.
    raw_score = model.decision_function(features)[0]
    risk_score = 1 / (1 + np.exp(raw_score * 5))  # squash into (0, 1), tuned empirically
    return float(np.clip(risk_score, 0.0, 1.0))
