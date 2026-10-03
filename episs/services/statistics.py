"""Media, desviación, pruebas de una muestra, intervalos y tamaño muestral."""

import math
import statistics as descriptive

from scipy import stats

from .validation import (
    InputError,
    choice,
    count,
    finite_result,
    level,
    number,
    observations,
    positive,
    probability,
    tail,
)


def summarize(values):
    values = observations(values)
    return {"n": len(values), "mean": descriptive.mean(values), "sd": descriptive.stdev(values)}


def prepare(data, hypothesis=False):
    method = choice(data.get("method"), ("z", "t", "proportion"), "Método")
    confidence, alpha = level(data.get("confidence"))
    result = {"method": method, "confidence": confidence, "alpha": alpha}
    if method == "proportion":
        result["n"] = count(data.get("n"), "n")
        result["success"] = count(data.get("success"), "Éxitos", 0, result["n"])
    else:
        source = choice(data.get("source", "summary"), ("summary", "raw"), "Entrada de datos")
        if source == "raw":
            result.update(summarize(data.get("raw")))
            if method == "z":
                result["sd"] = positive(data.get("sd"), "σ poblacional")
            else:
                result["sd"] = positive(result["sd"], "Desviación muestral s")
        else:
            result.update(
                n=count(data.get("n"), "n", 2),
                mean=number(data.get("mean"), "Media"),
                sd=positive(data.get("sd"), "Desviación"),
            )
    if hypothesis:
        result["tail"] = tail(data.get("tail"))
        result["nullValue"] = (
            probability(data.get("nullValue"), "p₀")
            if method == "proportion"
            else number(data.get("nullValue"), "μ₀")
        )
    return result


def wilson(success, n, alpha):
    estimate = success / n
    q = float(stats.norm.isf(alpha / 2))
    denominator = 1 + q * q / n
    center = (estimate + q * q / (2 * n)) / denominator
    margin = q * math.sqrt(estimate * (1 - estimate) / n + q * q / (4 * n * n)) / denominator
    return {
        "estimate": estimate,
        "q": q,
        "center": center,
        "margin": margin,
        "ci": [max(0.0, center - margin), min(1.0, center + margin)],
        "methodLabel": "Wilson",
        "formula": "Centro = (p̂ + z²/2n)/(1 + z²/n); semiancho = z·√[p̂(1−p̂)/n + z²/4n²]/(1 + z²/n)",
    }


def p_value(distribution, statistic, alternative):
    if alternative == "two":
        value = 2 * distribution.sf(abs(statistic))
    elif alternative == "left":
        value = distribution.cdf(statistic)
    else:
        value = distribution.sf(statistic)
    return finite_result(min(1.0, max(0.0, float(value))))


def interval(data):
    d = prepare(data)
    if d["method"] == "proportion":
        return {**d, **wilson(d["success"], d["n"], d["alpha"])}
    df = d["n"] - 1 if d["method"] == "t" else None
    distribution = stats.t(df) if df else stats.norm()
    q = float(distribution.isf(d["alpha"] / 2))
    se = finite_result(d["sd"] / math.sqrt(d["n"]))
    margin = finite_result(q * se)
    return {
        **d,
        "estimate": d["mean"],
        "center": d["mean"],
        "q": q,
        "margin": margin,
        "df": df,
        "se": se,
        "ci": [d["mean"] - margin, d["mean"] + margin],
        "methodLabel": "t de Student" if df else "Z",
        "formula": "IC = x̄ ± valor crítico × desviación / √n",
    }


def hypothesis(data):
    d = prepare(data, hypothesis=True)
    confidence_interval = interval(d)
    df = d["n"] - 1 if d["method"] == "t" else None
    distribution = stats.t(df) if df else stats.norm()
    warnings = ["Supuestos: muestra aleatoria y observaciones independientes."]
    adequate = True
    if d["method"] == "proportion":
        estimate = d["success"] / d["n"]
        se = math.sqrt(d["nullValue"] * (1 - d["nullValue"]) / d["n"])
        adequate = d["n"] * d["nullValue"] >= 10 and d["n"] * (1 - d["nullValue"]) >= 10
        formula = "Z = (p̂ − p₀) / √[p₀(1 − p₀)/n]"
        substitution = f"({estimate:g} − {d['nullValue']:g}) / √[{d['nullValue']:g} × {1 - d['nullValue']:g} / {d['n']}]"
        if not adequate:
            warnings.append(
                "La aproximación Z no es adecuada: n·p₀ y n·(1−p₀) deben ser al menos 10. Se necesita una prueba binomial exacta para una conclusión definitiva."
            )
    else:
        estimate = d["mean"]
        se = d["sd"] / math.sqrt(d["n"])
        symbol = "t" if df else "Z"
        deviation = "s" if df else "σ"
        formula = f"{symbol} = (x̄ − μ₀) / ({deviation} / √n)"
        substitution = f"({d['mean']:g} − {d['nullValue']:g}) / ({d['sd']:g} / √{d['n']})"
        if d["n"] < 30:
            warnings.append(
                "Muestra pequeña: comprueba normalidad aproximada y ausencia de valores atípicos importantes."
            )
    if se <= 0:
        raise InputError("El error estándar es cero. Revisa la desviación o la proporción.")
    statistic = finite_result((estimate - d["nullValue"]) / se)
    p = p_value(distribution, statistic, d["tail"])
    return {
        **d,
        "df": df,
        "estimate": estimate,
        "se": se,
        "statistic": statistic,
        "p": p,
        "reject": p <= d["alpha"],
        "adequate": adequate,
        "critical": float(distribution.isf(d["alpha"] / (2 if d["tail"] == "two" else 1))),
        "ci": confidence_interval["ci"],
        "formula": formula,
        "substitution": substitution,
        "warnings": warnings,
    }


def sample_size(data):
    confidence, alpha = level(data.get("confidence"))
    parameter = choice(data.get("parameter"), ("mean", "proportion"), "Parámetro")
    error = positive(data.get("error"), "Margen de error E")
    finite = data.get("finite", False)
    if not isinstance(finite, bool):
        raise InputError("La opción de población finita debe ser verdadera o falsa.")
    result = {
        "confidence": confidence,
        "alpha": alpha,
        "parameter": parameter,
        "error": error,
        "finite": finite,
    }
    if parameter == "proportion":
        p = probability(data.get("p"), "Proporción prevista p")
        if error >= 1:
            raise InputError("El margen de error de una proporción debe ser menor que 1.")
        variance = p * (1 - p)
        result["p"] = p
    else:
        result["sd"] = positive(data.get("sd"), "Desviación prevista σ")
        variance = result["sd"] ** 2
    z = float(stats.norm.isf(alpha / 2))
    n0 = finite_result(z * z * variance / error**2)
    if n0 > 1e12:
        raise InputError("El tamaño supera el rango admitido; revisa el margen de error.")
    exact = n0
    if finite:
        result["population"] = count(data.get("population"), "Población N", 2, 10**12)
        exact = n0 / (1 + (n0 - 1) / result["population"])
    return {
        **result,
        "z": z,
        "n0": n0,
        "exact": exact,
        "n": max(1, math.ceil(exact)),
        "formula": "n₀ = z² · p(1−p) / E²" if parameter == "proportion" else "n₀ = z² · σ² / E²",
    }
