"""Validaciones compartidas. Todos los servicios validan sus entradas en Python."""

import math
import re


class InputError(ValueError):
    """Datos que el usuario puede corregir en el formulario."""


NUMBER = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$", re.I)


def number(value, label, limit=1e12):
    if isinstance(value, bool) or value is None:
        raise InputError(f"{label}: introduce un número válido.")
    text = str(value).strip().replace(",", ".")
    if not NUMBER.fullmatch(text):
        raise InputError(f"{label}: introduce un número válido, sin separadores de miles.")
    result = float(text)
    if not math.isfinite(result) or abs(result) > limit:
        raise InputError(f"{label}: introduce un número finito de magnitud ≤ {limit:g}.")
    # Evitar aceptar un valor no nulo que se haya redondeado a cero por subdesbordamiento.
    if result == 0 and any(c in "123456789" for c in text.lower().split("e")[0]):
        raise InputError(f"{label}: el número es demasiado pequeño para esta precisión.")
    return result


def positive(value, label):
    result = number(value, label)
    if result <= 0:
        raise InputError(f"{label} debe ser mayor que cero.")
    return result


def count(value, label, minimum=1, maximum=1_000_000):
    result = number(value, label)
    if not result.is_integer() or not minimum <= result <= maximum:
        raise InputError(f"{label} debe ser un entero entre {minimum} y {maximum}.")
    return int(result)


def probability(value, label):
    result = number(value, label)
    if not 0 < result < 1:
        raise InputError(f"{label} debe estar entre 0 y 1, sin incluir los extremos.")
    return result


def choice(value, allowed, label):
    if value not in allowed:
        raise InputError(f"{label}: selecciona una opción válida.")
    return value


def level(value):
    confidence = number(value, "Nivel de confianza")
    choice(confidence, (0.90, 0.95, 0.99), "Nivel de confianza")
    return confidence, 1 - confidence


def tail(value):
    return choice(value, ("two", "left", "right"), "Hipótesis alternativa")


def observations(value, label="Observaciones"):
    if isinstance(value, str):
        value = re.split(r"[;\s]+", value.strip()) if value.strip() else []
    if not isinstance(value, list) or not 2 <= len(value) <= 10_000:
        raise InputError(f"{label}: ingresa entre 2 y 10 000 observaciones.")
    return [number(x, label) for x in value]


def finite_result(value):
    """Rechazar escalas imposibles antes de producir JSON o un gráfico."""
    if not math.isfinite(float(value)):
        raise InputError("Resultado fuera del rango numérico. Revisa la escala de tus datos.")
    return float(value)
