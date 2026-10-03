"""Entradas reales, errores, páginas y contratos de la API Python."""

import pytest

from episs import create_app
from episs.services.comparisons import power_at


@pytest.fixture()
def client():
    return create_app({"TESTING": True}).test_client()


def test_pages_and_assets(client):
    for path in (
        "/",
        "/index.html",
        "/interpolacion.html",
        "/static/js/app.js",
        "/static/css/unaj.css",
        "/static/img/logo-unaj.svg",
    ):
        assert client.get(path).status_code == 200
    assert "Palaco Charaja Edgar Whashigton" in client.get("/").text
    assert client.get("/api/health").json["engine"] == "Python + SciPy"


def test_raw_data_and_decimal_comma(client):
    response = client.post(
        "/api/hypothesis",
        json={
            "method": "t",
            "source": "raw",
            "raw": "1,5; 2,5\n3,5",
            "confidence": "0.95",
            "tail": "two",
            "nullValue": "2,5",
        },
    )
    assert response.status_code == 200
    result = response.json["result"]
    assert result["n"] == 3
    assert result["mean"] == 2.5
    assert result["sd"] == 1
    assert result["statistic"] == 0
    assert result["p"] == 1


def test_small_proportion_warning(client):
    response = client.post(
        "/api/hypothesis",
        json={
            "method": "proportion",
            "n": 10,
            "success": 0,
            "confidence": 0.95,
            "tail": "two",
            "nullValue": 0.5,
        },
    )
    assert response.status_code == 200
    assert response.json["result"]["adequate"] is False
    assert response.json["view"]["headline"] == "Aproximación Z no adecuada"


def test_wilson_zero_success(client):
    result = client.post(
        "/api/interval", json={"method": "proportion", "n": 10, "success": 0, "confidence": 0.95}
    ).json["result"]
    assert result["ci"][0] == 0
    assert result["ci"][1] == pytest.approx(0.2775328, abs=1e-7)


def test_power_returns_smallest_n(client):
    result = client.post(
        "/api/power",
        json={"sd": 15, "delta": 5, "n": 50, "target": 0.8, "confidence": 0.95, "tail": "two"},
    ).json["result"]
    assert power_at(result["required"], 15, 5, "two", result["q"]) >= 0.8
    assert power_at(result["required"] - 1, 15, 5, "two", result["q"]) < 0.8


def test_unilateral_variance_has_json_null_limit(client):
    response = client.post(
        "/api/variance",
        json={"type": "chi", "n1": 25, "s1": 6, "v0": 25, "confidence": 0.95, "tail": "left"},
    )
    assert response.status_code == 200
    assert response.json["result"]["high"] is None
    assert "∞" in str(response.json["view"]["steps"])


@pytest.mark.parametrize("x,y,outside", [(15, 150, False), (25, 250, True), (10, 100, False)])
def test_interpolation(client, x, y, outside):
    response = client.post(
        "/api/interpolation", json={"x1": 10, "y1": 100, "x2": 20, "y2": 200, "x": x}
    )
    assert response.status_code == 200
    assert response.json["result"]["y"] == y
    assert response.json["result"]["outside"] is outside


def test_csv_and_reproducible_sampling(client):
    data = {
        "records": "=1;A;1\n2;A;2\n3;B;3\n4;B;4",
        "n": "4",
        "seed": "2026",
        "method": "stratified",
        "allocation": "neyman",
    }
    first = client.post("/api/sampling", json=data).json
    second = client.post("/api/sampling", json=data).json
    assert first == second
    assert len({row["id"] for row in first["result"]["selected"]}) == 4
    assert first["view"]["download"]["content"].startswith("\ufeff")
    assert "'=1" in first["view"]["download"]["content"]


@pytest.mark.parametrize(
    "tool,data",
    [
        (
            "hypothesis",
            {
                "method": "t",
                "n": 1,
                "mean": 52,
                "sd": 5,
                "confidence": 0.95,
                "tail": "two",
                "nullValue": 50,
            },
        ),
        (
            "hypothesis",
            {
                "method": "t",
                "source": "raw",
                "raw": "1;1;1",
                "confidence": 0.95,
                "tail": "two",
                "nullValue": 1,
            },
        ),
        ("interval", {"method": "proportion", "n": 10, "success": 11, "confidence": 0.95}),
        ("interval", {"method": "z", "n": 10, "mean": "NaN", "sd": 1, "confidence": 0.95}),
        ("sample", {"parameter": "proportion", "p": 0.5, "error": 0, "confidence": 0.95}),
        (
            "variance",
            {"type": "chi", "n1": 25, "s1": -1, "v0": 25, "confidence": 0.95, "tail": "two"},
        ),
        (
            "compare",
            {
                "type": "paired",
                "a": "1;2",
                "b": "1;2;3",
                "delta": 0,
                "confidence": 0.95,
                "tail": "two",
            },
        ),
        (
            "power",
            {"n": 50, "sd": 15, "delta": 5, "target": 0.01, "confidence": 0.95, "tail": "two"},
        ),
        ("sampling", {"records": "A\nA", "n": 1, "seed": 0, "method": "mas"}),
        (
            "sampling",
            {
                "records": "A;X;\nB;X;",
                "n": 1,
                "seed": 0,
                "method": "stratified",
                "allocation": "neyman",
            },
        ),
        ("interpolation", {"x1": 10, "y1": 100, "x2": 10, "y2": 200, "x": 15}),
    ],
)
def test_invalid_input(client, tool, data):
    response = client.post("/api/" + tool, json=data)
    assert response.status_code == 422
    assert response.json["ok"] is False
    assert response.json["error"]


def test_invalid_requests(client):
    assert client.post("/api/interval", json=[]).status_code == 400
    assert (
        client.post("/api/interval", data="{", content_type="application/json").status_code == 400
    )
    assert client.post("/api/interval", data="hola").status_code == 415
    assert client.post("/api/unknown", json={}).status_code == 404
