"""Interpolación y extrapolación lineal entre dos puntos."""

from .validation import InputError, finite_result, number


def interpolate(data):
    result = {key: number(data.get(key), key, 1e100) for key in ("x1", "y1", "x2", "y2", "x")}
    if any(value != 0 and abs(value) < 1e-100 for value in result.values()):
        raise InputError("Usa números entre 1e−100 y 1e100 en valor absoluto, o cero.")
    if result["x1"] == result["x2"]:
        raise InputError("x₁ y x₂ deben ser distintos. No se puede dividir entre cero.")
    t = (result["x"] - result["x1"]) / (result["x2"] - result["x1"])
    y = finite_result(result["y1"] + t * (result["y2"] - result["y1"]))
    return {
        **result,
        "t": finite_result(t),
        "y": y,
        "outside": not min(result["x1"], result["x2"])
        <= result["x"]
        <= max(result["x1"], result["x2"]),
    }
