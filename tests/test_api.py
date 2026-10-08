"""Entradas reales, errores, páginas y contratos de la API Python."""

import pytest

from episs import create_app


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


def test_stratified_summary_material_723(client):
    response = client.post('/api/sampling', json=dict(
        source='summary', method='stratified', allocation='proportional', n=600,
        strata='Públicos;6000\nPrivados parroquiales;3000\nPrivados no parroquiales;1000'))
    assert response.status_code == 200
    result, view = response.json['result'], response.json['view']
    assert result['N'] == 10000
    assert [g['n'] for g in result['allocation']] == [360, 180, 60]
    assert view['table']['rows'][-1] == ['Total', '10000', '100 %', '600']
    assert 'download' not in view
    assert 'selected' not in result


@pytest.mark.parametrize('strata,n,expected', [
    ('A;3\nB;3\nC;3', 5, [2, 2, 1]),
    ('A;1\nB;9', 10, [1, 9]),
    ('A;1\nB;99', 1, [0, 1]),
])
def test_summary_rounding(client, strata, n, expected):
    response = client.post('/api/sampling', json=dict(
        source='summary', method='stratified', strata=strata, n=n))
    assert response.status_code == 200
    groups = response.json['result']['allocation']
    assert [g['n'] for g in groups] == expected
    assert sum(g['n'] for g in groups) == n
    assert all(0 <= g['n'] <= g['N'] for g in groups)


@pytest.mark.parametrize('changes', [
    {'strata': ''}, {'strata': 'A;0'}, {'strata': 'A;-5'},
    {'strata': 'A;1.5'}, {'strata': 'A;100\na;100'},
    {'strata': 'A;100;2'}, {'strata': ';100'}, {'strata': None},
    {'n': 101}, {'n': 0}, {'n': 1.5},
    {'allocation': 'neyman'}, {'method': 'mas'},
])
def test_invalid_summary(client, changes):
    data = dict(source='summary', method='stratified', strata='A;100', n=10)
    data.update(changes)
    response = client.post('/api/sampling', json=data)
    assert response.status_code == 422
    assert response.json['error']


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
        ("hypothesis", {"method": "proportion", "n": 10, "success": 11, "confidence": 0.95}),
        ("hypothesis", {"method": "z", "n": 10, "mean": "NaN", "sd": 1, "confidence": 0.95}),
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
    assert response.status_code == (404 if tool in ("variance", "power") else 422)
    assert response.json["ok"] is False
    assert response.json["error"]


def test_invalid_requests(client):
    assert client.post("/api/hypothesis", json=[]).status_code == 400
    assert (
        client.post("/api/hypothesis", data="{", content_type="application/json").status_code == 400
    )
    assert client.post("/api/hypothesis", data="hola").status_code == 415
    assert client.post("/api/unknown", json={}).status_code == 404

@pytest.mark.parametrize('tool', ['variance', 'power', 'interval', 'proportions', 'proportion_interval'])
def test_removed_topics(client, tool):
    assert client.post('/api/' + tool, json={}).status_code == 404
    assert f'data-mode="{tool}"' not in client.get('/').text
    assert f'data-open="{tool}"' not in client.get('/').text


def test_material_bank_example(client):
    r = client.post('/api/hypothesis', json=dict(method='z_sample', n=200, mean=298.1,
        sd=97.3, confidence=.99, tail='two', nullValue=312)).json['result']
    assert r['statistic'] == pytest.approx(-2.0203, abs=.0001)
    assert r['reject'] is False


def test_material_sample_size(client):
    r = client.post('/api/sample', json=dict(parameter='mean', sd=45, error=10,
        confidence=.95)).json['result']
    assert r['n'] == 78






def test_new_z_and_finite_population(client):
    data = dict(method='proportion', n=250, success=25, nullValue=.05,
        confidence=.95, tail='right', population=2000)
    r=client.post('/api/hypothesis',json=data).json['result']
    assert r['statistic'] == pytest.approx(3.87685, abs=.0001)
    assert r['reject']
    data=dict(type='z', mean1=100, mean2=95, s1=10, s2=10, n1=50,n2=50,
        confidence=.95,tail='two',delta=0)
    response=client.post('/api/compare',json=data)
    assert response.status_code == 200
    assert response.json['result']['statistic']==2.5
    assert response.json['result']['df'] is None


