import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def iris():
    from viewx.datasets import load_iris
    return load_iris()


@pytest.fixture
def sales_df():
    rng = np.random.default_rng(0)
    n = 300
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=n, freq="D"),
        "region": rng.choice(["North", "South", "East", "West"], size=n),
        "revenue": rng.lognormal(mean=8, sigma=0.4, size=n).round(2),
        "units": rng.integers(1, 200, size=n),
        "active": rng.choice([True, False], size=n),
    })


@pytest.fixture
def big_df():
    rng = np.random.default_rng(1)
    n = 30_000
    return pd.DataFrame({
        "x": np.arange(n),
        "y": rng.standard_normal(n).cumsum(),
        "cat": rng.choice(["a", "b", "c"], size=n),
    })
