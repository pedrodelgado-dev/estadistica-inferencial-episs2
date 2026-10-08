"""Gráficos SVG calculados en Python; JavaScript solo dibuja estos elementos."""

from scipy import stats

from .formatting import fmt


class Chart:
    def __init__(self, label, note):
        self.data = {"elements": [], "label": label, "note": note}

    def add(self, tag, attrs, text=None):
        self.data["elements"].append({"tag": tag, "attrs": attrs, "text": text})

    def line(self, x1, y1, x2, y2, color="#264a77", **attrs):
        self.add("line", {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": color, **attrs})

    def text(self, x, y, text, **attrs):
        self.add("text", {"x": x, "y": y, "font-size": 13, "fill": "#526d83", **attrs}, text)


def path(points):
    return " ".join(f"{'M' if i == 0 else 'L'}{x:.5f} {y:.5f}" for i, (x, y) in enumerate(points))


def rejection_curve(r):
    df = r.get("df")
    distribution = stats.t(df) if df else stats.norm()
    extent = max(4.0, min(12.0, r["critical"] * 1.4))
    maximum = distribution.pdf(0)
    chart = Chart(
        f"Distribución {'t' if df else 'normal estándar'}, estadístico {fmt(r['statistic'])}.",
        "Naranja claro: región de rechazo. Naranja oscuro: estadístico observado. "
        + (
            f"Distribución t con {fmt(df)} grados de libertad."
            if df
            else "Distribución normal estándar."
        ),
    )

    def X(x):
        return 55 + (x + extent) / (2 * extent) * 590

    def Y(y):
        return 225 - y / maximum * 170

    points = [(-extent + 2 * extent * i / 280) for i in range(281)]
    curve = [(X(x), Y(float(distribution.pdf(x)))) for x in points]
    chart.add(
        "path", {"d": f"M55 225 {path(curve).replace('M', 'L', 1)} L645 225 Z", "fill": "#e5eef7"}
    )
    chunks, current = [], []
    for x, point in zip(points, curve):
        rejected = (
            abs(x) >= r["critical"]
            if r["tail"] == "two"
            else x >= r["critical"]
            if r["tail"] == "right"
            else x <= -r["critical"]
        )
        if rejected:
            current.append(point)
        elif current:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    for chunk in chunks:
        chart.add(
            "path",
            {
                "d": f"M{chunk[0][0]} 225 {path(chunk).replace('M', 'L', 1)} L{chunk[-1][0]} 225 Z",
                "fill": "#f2d2ad",
            },
        )
    chart.add("path", {"d": path(curve), "fill": "none", "stroke": "#264a77", "stroke-width": 2.5})
    chart.line(55, 225, 645, 225, "#8a9aab")
    for i in range(7):
        x = -extent + 2 * extent * i / 6
        chart.text(X(x), 250, fmt(x), **{"text-anchor": "middle"})
    criticals = (
        [-r["critical"], r["critical"]]
        if r["tail"] == "two"
        else [r["critical"] if r["tail"] == "right" else -r["critical"]]
    )
    for x in criticals:
        # Si el crítico t queda fuera de la escala, su posición se avisa en la nota.
        if abs(x) > extent:
            chart.data["note"] += f" Valor crítico {fmt(x)} fuera de escala."
            continue
        chart.line(X(x), 55, X(x), 225, "#a3662f", **{"stroke-dasharray": "4 4"})
        chart.text(X(x), 35, fmt(x), **{"text-anchor": "middle", "fill": "#a3662f"})
    clipped = max(-extent, min(extent, r["statistic"]))
    chart.line(X(clipped), 70, X(clipped), 225, "#ce7624", **{"stroke-width": 3})
    anchor = "end" if clipped > extent * 0.6 else "start" if clipped < -extent * 0.6 else "middle"
    label = (
        "Fuera de escala: " if abs(r["statistic"]) > extent else ""
    ) + f"{'t' if df else 'Z'} = {fmt(r['statistic'])}"
    chart.text(X(clipped), 67, label, **{"text-anchor": anchor, "fill": "#97551d"})
    return chart.data






def size_chart(r, selected=False):
    n = r["n"]
    summary = r.get("source") == "summary"
    total = r["N"] if selected else r.get("population", n)
    chart = Chart(
        f"{n} observaciones {'a distribuir' if summary else 'seleccionadas' if selected else 'requeridas'}.",
        "La tabla muestra la muestra asignada a cada estrato; no se han seleccionado personas individuales."
        if summary else "Vista previa: primeros 100 identificadores. El CSV contiene toda la selección."
        if selected
        else "Se redondea hacia arriba para alcanzar la precisión solicitada.",
    )
    chart.text(
        55,
        75,
        f"{n} / {total}" if selected else f"{n} observaciones requeridas",
        **{"font-size": 19},
    )
    chart.add("rect", {"x": 55, "y": 115, "width": 590, "height": 38, "rx": 8, "fill": "#e5eef7"})
    chart.add(
        "rect",
        {
            "x": 55,
            "y": 115,
            "width": min(590, 590 * n / total),
            "height": 38,
            "rx": 8,
            "fill": "#ce7624",
        },
    )
    chart.text(
        55,
        193,
        f"{fmt(n / total * 100)} % de {total} registros"
        if selected or r.get("finite")
        else "Población grande o de tamaño desconocido",
        **{"font-size": 15},
    )
    return chart.data




def interpolation_chart(r):
    xs, ys = [r["x1"], r["x2"], r["x"]], [r["y1"], r["y2"], r["y"]]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    dx, dy = xmax - xmin, ymax - ymin or max(1, abs(ymin) * 0.2)
    chart = Chart(
        f"Puntos ({fmt(r['x1'])}, {fmt(r['y1'])}) y ({fmt(r['x2'])}, {fmt(r['y2'])}). Resultado ({fmt(r['x'])}, {fmt(r['y'])}).",
        "La línea discontinua prolonga la recta fuera del intervalo."
        if r["outside"]
        else "La recta conecta los dos puntos conocidos.",
    )

    def X(x):
        return 90 + (x - xmin) / dx * 505

    def Y(y):
        return 265 - (y - ymin) / dy * 210

    for i in range(5):
        x, y = xmin + dx * i / 4, ymin + dy * i / 4
        chart.line(90, Y(y), 610, Y(y), "#e8eef5")
        chart.line(X(x), 40, X(x), 265, "#e8eef5")
        chart.text(80, Y(y) + 4, fmt(y), **{"text-anchor": "end", "font-size": 12})
        chart.text(X(x), 290, fmt(x), **{"text-anchor": "middle", "font-size": 12})
    chart.text(625, 289, "x", **{"font-size": 14})
    chart.text(75, 23, "y", **{"font-size": 14})
    if r["outside"]:
        i = 1 if abs(r["x"] - r["x1"]) < abs(r["x"] - r["x2"]) else 2
        chart.line(
            X(r[f"x{i}"]),
            Y(r[f"y{i}"]),
            X(r["x"]),
            Y(r["y"]),
            **{"stroke-width": 3, "stroke-dasharray": "7 6"},
        )
    chart.line(X(r["x1"]), Y(r["y1"]), X(r["x2"]), Y(r["y2"]), **{"stroke-width": 3})
    chart.line(X(r["x"]), Y(r["y"]), X(r["x"]), 265, "#ce7624", **{"stroke-dasharray": "4 5"})
    for i in (1, 2):
        chart.add(
            "circle",
            {
                "cx": X(r[f"x{i}"]),
                "cy": Y(r[f"y{i}"]),
                "r": 6,
                "fill": "#264a77",
                "stroke": "white",
                "stroke-width": 3,
            },
        )
    chart.add(
        "circle",
        {
            "cx": X(r["x"]),
            "cy": Y(r["y"]),
            "r": 8,
            "fill": "#ce7624",
            "stroke": "white",
            "stroke-width": 3,
        },
    )
    return chart.data
