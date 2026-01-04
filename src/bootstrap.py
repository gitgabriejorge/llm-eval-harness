import numpy as np
import pandas as pd


def bootstrap_ci_mean(
    x: pd.Series,
    n_boot: int = 2000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """
    Calcula média e IC por bootstrap (percentil).
    Retorna (mean, lo, hi).
    """
    rng = np.random.default_rng(seed)

    values = x.dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return (float("nan"), float("nan"), float("nan"))

    mean = float(values.mean())

    boot_means = np.empty(n_boot, dtype=float)
    n = len(values)

    for i in range(n_boot):
        sample = rng.choice(values, size=n, replace=True)
        boot_means[i] = sample.mean()

    alpha = (1.0 - ci) / 2.0
    lo = float(np.quantile(boot_means, alpha))
    hi = float(np.quantile(boot_means, 1.0 - alpha))
    return mean, lo, hi
