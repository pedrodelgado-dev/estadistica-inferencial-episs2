"""API JSON: validar, calcular y preparar el resultado para la interfaz."""

import json

from flask import Blueprint, jsonify, request

from ..presentation import results
from ..services import comparisons, interpolation, sampling, statistics
from ..services.validation import InputError

api = Blueprint("api", __name__, url_prefix="/api")

# Una entrada por herramienta; las variantes se seleccionan en el formulario.
CALCULATORS = {
    "hypothesis": (statistics.hypothesis, results.hypothesis),
    "interval": (statistics.interval, results.interval),
    "sample": (statistics.sample_size, results.sample_size),
    "variance": (comparisons.variance, results.variance),
    "compare": (comparisons.compare, results.compare),
    "power": (comparisons.power, results.power),
    "sampling": (sampling.sampling, results.sampling),
    "interpolation": (interpolation.interpolate, results.interpolation),
}


@api.get("/health")
def health():
    return jsonify(ok=True, engine="Python + SciPy")


@api.post("/<tool>")
def calculate(tool):
    if tool not in CALCULATORS:
        return jsonify(ok=False, error="Herramienta no encontrada."), 404
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify(ok=False, error="Envía un objeto JSON con los datos del formulario."), 400
    compute, present = CALCULATORS[tool]
    try:
        numeric = compute(data)
        payload = {"ok": True, "result": numeric, "view": present(numeric)}
        # Impedir NaN/Infinity en JSON y gráficos, incluso para escalas extremas.
        json.dumps(payload, allow_nan=False)
    except InputError as error:
        return jsonify(ok=False, error=str(error)), 422
    except (OverflowError, ZeroDivisionError, FloatingPointError, ValueError):
        return jsonify(
            ok=False, error="La escala numérica no permite un resultado finito. Revisa tus datos."
        ), 422
    return jsonify(payload)
