"""Formato de números y mensajes de presentación, separado de las fórmulas."""

import math


def fmt(value):
    if value is None:
        return "∞"
    if not math.isfinite(float(value)):
        return "Fuera de rango"
    text = format(float(value), ".7g")
    return text.replace(".", ",")


def p_text(value):
    return "< 0,0000001" if value < 1e-7 else fmt(value)


def alternative(tail):
    return {"two": ("≠", "="), "left": ("<", "≥"), "right": (">", "≤")}[tail]
