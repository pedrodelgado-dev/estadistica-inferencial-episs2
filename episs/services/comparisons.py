"""Pruebas χ² y F, comparación de medias y potencia de una prueba Z."""

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
    probability,
    tail,
)


def variance(data):
    confidence, alpha = level(data.get("confidence"))
    alternative = tail(data.get("tail"))
    kind = choice(data.get("type"), ("chi", "f"), "Contraste")
    n1 = count(data.get("n1"), "n₁", 2, 100_000)
    s1 = positive(data.get("s1"), "s₁")
    d1, d2 = n1 - 1, None
    result = {
        "type": kind,
        "confidence": confidence,
        "alpha": alpha,
        "tail": alternative,
        "n1": n1,
        "s1": s1,
    }
    if kind == "chi":
        v0 = positive(data.get("v0"), "Varianza hipotética σ₀²")
        statistic = finite_result(d1 * s1**2 / v0)
        distribution = stats.chi2(d1)
        estimate = s1**2
        result["v0"] = v0
        ci = [
            d1 * estimate / distribution.isf(alpha / 2),
            d1 * estimate / distribution.ppf(alpha / 2),
        ]
    else:
        n2 = count(data.get("n2"), "n₂", 2, 100_000)
        s2 = positive(data.get("s2"), "s₂")
        d2 = n2 - 1
        statistic = finite_result(s1**2 / s2**2)
        distribution = stats.f(d1, d2)
        ci = [statistic / distribution.isf(alpha / 2), statistic / distribution.ppf(alpha / 2)]
        result.update(n2=n2, s2=s2)
    if statistic <= 0:
        raise InputError("Resultado fuera del rango numérico.")
    left, right = float(distribution.cdf(statistic)), float(distribution.sf(statistic))
    p = (
        min(1.0, 2 * min(left, right))
        if alternative == "two"
        else left
        if alternative == "left"
        else right
    )
    low = (
        0.0
        if alternative == "right"
        else float(distribution.ppf(alpha / (2 if alternative == "two" else 1)))
    )
    # null representa un límite superior ilimitado en JSON, nunca Infinity.
    high = (
        None
        if alternative == "left"
        else float(distribution.isf(alpha / (2 if alternative == "two" else 1)))
    )
    return {
        **result,
        "statistic": statistic,
        "d1": d1,
        "d2": d2,
        "p": p,
        "low": low,
        "high": high,
        "ci": [finite_result(x) for x in ci],
        "reject": p <= alpha,
    }


def compare(data):
    confidence, alpha = level(data.get("confidence"))
    alternative = tail(data.get("tail"))
    kind = choice(data.get("type"), ("welch", "pooled", "paired"), "Diseño y método")
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
        if kind == "pooled":
            df = n1 + n2 - 2
            pooled = ((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / df
            se = math.sqrt(pooled * (1 / n1 + 1 / n2))
        else:
            se = math.sqrt(u + v)
            df = (u + v) ** 2 / (u**2 / (n1 - 1) + v**2 / (n2 - 1))
    if se <= 0:
        raise InputError("La desviación produce un error estándar nulo.")
    distribution = stats.t(finite_result(df))
    statistic = finite_result((estimate - delta) / se)
    p = p_value(distribution, statistic, alternative)
    q = float(distribution.isf(alpha / 2))
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
        "ci": [finite_result(estimate - q * se), finite_result(estimate + q * se)],
    }


def power_at(n, sd, delta, alternative, critical):
    shift = delta * math.sqrt(n) / sd
    if alternative == "two":
        return float(stats.norm.sf(critical - shift) + stats.norm.sf(critical + shift))
    if alternative == "right":
        return float(stats.norm.sf(critical - shift))
    return float(stats.norm.sf(critical + shift))


def power(data):
    confidence, alpha = level(data.get("confidence"))
    alternative = tail(data.get("tail"))
    sd = positive(data.get("sd"), "σ poblacional conocida")
    delta = number(data.get("delta"), "Efecto μ₁ − μ₀")
    n = count(data.get("n"), "n", 2)
    target = probability(data.get("target"), "Potencia objetivo")
    if target <= alpha:
        raise InputError("La potencia objetivo debe ser mayor que α.")
    q = float(stats.norm.isf(alpha / (2 if alternative == "two" else 1)))

    def at(size):
        return power_at(size, sd, delta, alternative, q)

    value, required = at(n), None
    suitable = delta != 0 and (
        alternative == "two"
        or alternative == "right"
        and delta > 0
        or alternative == "left"
        and delta < 0
    )
    if suitable:
        lo, hi = 2, 2
        while at(hi) < target and hi < 1_000_000:
            hi = min(1_000_000, hi * 2)
        if at(hi) >= target:
            while lo < hi:
                middle = (lo + hi) // 2
                if at(middle) >= target:
                    hi = middle
                else:
                    lo = middle + 1
            required = lo
    return {
        "confidence": confidence,
        "alpha": alpha,
        "tail": alternative,
        "sd": sd,
        "delta": delta,
        "n": n,
        "target": target,
        "q": q,
        "value": value,
        "beta": 1 - value,
        "required": required,
        "shift": delta * math.sqrt(n) / sd,
    }
