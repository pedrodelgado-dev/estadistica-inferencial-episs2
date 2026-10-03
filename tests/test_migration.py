"""Regresión numérica frente a 120 casos de la versión JavaScript original."""

import json
from pathlib import Path

import pytest

from episs import create_app

CASES = json.loads(Path(__file__).with_name("legacy_cases.json").read_text())


@pytest.fixture(scope="module")
def client():
    return create_app({"TESTING": True}).test_client()


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["tool"])
def test_original_results(client, case):
    response = client.post("/api/" + case["tool"], json=case["data"])
    assert response.status_code == 200, response.json
    result = response.json["result"]
    for key, expected in case["expected"].items():
        if key == "selectedIds":
            assert [row["id"] for row in result["selected"]] == expected
        elif isinstance(expected, bool) or expected is None:
            assert result[key] is expected
        elif isinstance(expected, (int, float, list)):
            assert result[key] == pytest.approx(expected, rel=2e-6, abs=2e-8)
        else:
            assert result[key] == expected
    assert response.json["view"]["steps"]
    assert response.json["view"]["chart"]["elements"]
    # JSON estándar, sin Infinity/NaN de SciPy ni de cálculos extremos.
    json.dumps(response.json, allow_nan=False)
