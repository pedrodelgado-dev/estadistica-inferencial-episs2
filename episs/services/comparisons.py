"""Comparación de medias del material de clase."""

import math

from scipy import stats

from .statistics import p_value, summarize
from .validation import (
    InputError,
    choice,
    count,
    finite_result,
    level,
    number,
    positive,
    tail,
)




def compare(data):
    confidence, alpha = level(data.get("confidence"))
    alternative = tail(data.get("tail"))
    kind = choice(data.get("type"), ("z", "z_sample", "welch", "pooled", "paired"), "Diseño y método")
    delta = number(data.get("delta"), "Diferencia hipotética")
    if kind == "paired":
        a, b = data.get("a"), data.get("b")
        # El mismo parser valida y cuenta ambas listas, incluso si llegan como texto.
        from .validation import observations

        a, b = observations(a, "Grupo A"), observations(b, "Grupo B")
        if len(a) != len(b):
            raise InputError(
                "Las listas relacionadas deben tener la misma cantidad de observaciones."
            )
        differences = summarize([x - y for x, y in zip(a, b)])
        sd1 = positive(differences["sd"], "Desviación de las diferencias")
        estimate = differences["mean"]
        n1 = n2 = differences["n"]
        se = sd1 / math.sqrt(n1)
        df = n1 - 1
        mean1, mean2 = summarize(a)["mean"], summarize(b)["mean"]
        sd2 = None
    else:
        n1 = count(data.get("n1"), "n₁", 2)
        n2 = count(data.get("n2"), "n₂", 2)
        sd1 = positive(data.get("s1"), "s₁")
        sd2 = positive(data.get("s2"), "s₂")
        mean1 = number(data.get("mean1"), "Media A")
        mean2 = number(data.get("mean2"), "Media B")
        estimate = mean1 - mean2
        u, v = sd1**2 / n1, sd2**2 / n2
        if kind in ("z", "z_sample"):
            if kind == "z_sample" and min(n1, n2) < 30:
                raise InputError("Z con s requiere ambas muestras de al menos 30 observaciones.")
            se = math.sqrt(u + v)
            df = None
        elif kind == "pooled":
            df = n1 + n2 - 2
            pooled = ((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / df
            se = math.sqrt(pooled * (1 / n1 + 1 / n2))
        else:
            se = math.sqrt(u + v)
            df = (u + v) ** 2 / (u**2 / (n1 - 1) + v**2 / (n2 - 1))
    if se <= 0:
        raise InputError("La desviación produce un error estándar nulo.")
    if kind == "welch":
        df = max(1, math.floor(df + 0.5))  # El material redondea los grados de libertad.
    distribution = stats.t(finite_result(df)) if df else stats.norm()
    statistic = finite_result((estimate - delta) / se)
    p = p_value(distribution, statistic, alternative)
    return {
        "type": kind,
        "confidence": confidence,
        "alpha": alpha,
        "tail": alternative,
        "delta": delta,
        "estimate": estimate,
        "se": se,
        "df": df,
        "n1": n1,
        "n2": n2,
        "sd1": sd1,
        "sd2": sd2,
        "mean1": mean1,
        "mean2": mean2,
        "statistic": statistic,
        "p": p,
        "reject": p <= alpha,
        "critical": float(distribution.isf(alpha / (2 if alternative == "two" else 1))),
    }









