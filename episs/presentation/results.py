"""Convertir resultados numéricos en explicaciones educativas y gráficos."""

from ..services.sampling import csv_export
from . import charts
from .formatting import alternative, fmt, p_text


def base(label, headline, conclusion, metrics, steps, warnings, graph_title, chart):
    return {
        "label": label,
        "headline": headline,
        "conclusion": conclusion,
        "metrics": metrics,
        "steps": steps,
        "warnings": warnings,
        "graphTitle": graph_title,
        "chart": chart,
    }


def decision(r):
    return "Se rechaza H₀" if r["reject"] else "No se rechaza H₀"


def test_metrics(r):
    return [
        ("Estadístico", fmt(r["statistic"])),
        ("Valor p", p_text(r["p"])),
        ("Significancia α", fmt(r["alpha"])),
    ]


def decision_text(r):
    return f"{'Hay' if r['reject'] else 'No hay'} evidencia suficiente para la alternativa indicada al {fmt(r['alpha'] * 100)} % de significancia. No rechazar H₀ no demuestra que sea verdadera."


def hypothesis(r):
    op, h0 = alternative(r["tail"])
    prop = r["method"] == "proportion"
    symbol = "p" if prop else "μ"
    kind = "t DE STUDENT" if r["method"] == "t" else "Z"
    headline = decision(r) if r["adequate"] else "Aproximación Z no adecuada"
    conclusion = (
        f"{'Hay' if r['reject'] else 'No hay'} evidencia estadística suficiente al {fmt(r['alpha'] * 100)} % de significancia para afirmar que {symbol} {op} {fmt(r['nullValue'])}. No rechazar H₀ no demuestra que sea verdadera."
        if r["adequate"]
        else "No uses esta aproximación para una conclusión definitiva; se necesita una prueba binomial exacta."
    )
    rule = (
        f"Rechazar si |{'t' if r['df'] else 'Z'}| ≥ {fmt(r['critical'])}."
        if r["tail"] == "two"
        else f"Rechazar si el estadístico {'≥' if r['tail'] == 'right' else '≤'} {fmt(r['critical'] if r['tail'] == 'right' else -r['critical'])}."
    )
    data = f"n = {r['n']}; " + (
        f"éxitos = {r['success']}; p̂ = {fmt(r['estimate'])}."
        if prop
        else f"x̄ = {fmt(r['mean'])}; {'s' if r['method'] in ('t', 'z_sample') else 'σ'} = {fmt(r['sd'])}."
    )
    if r.get("population"):
        data += f" Población N = {r['population']}."
    if r["df"]:
        data += f" Grados de libertad = n − 1 = {r['df']}."
    steps = [
        ("Identificar los datos", data),
        (
            "Plantear las hipótesis",
            f"H₀: {symbol} {h0} {fmt(r['nullValue'])}. H₁: {symbol} {op} {fmt(r['nullValue'])}. La distribución nula se evalúa en el valor frontera.",
        ),
        (
            "Fijar el nivel y la regla",
            f"α = 1 − {fmt(r['confidence'])} = {fmt(r['alpha'])}. {rule}",
        ),
        (
            "Calcular el estadístico",
            f"{r['formula']}. Sustitución: {r['substitution']} = {fmt(r['statistic'])}; error estándar = {fmt(r['se'])}.",
        ),
        (
            "Comparar el valor p",
            f"p = {p_text(r['p'])}; α = {fmt(r['alpha'])}. "
            + (
                decision(r) + "."
                if r["adequate"]
                else "No emitir una decisión definitiva: la aproximación no cumple los requisitos."
            ),
        ),
    ]
    return base(
        f"PRUEBA {kind} · UNA {'PROPORCIÓN' if prop else 'MEDIA'}",
        headline,
        conclusion,
        test_metrics(r),
        steps,
        r["warnings"],
        "Distribución y región de rechazo",
        charts.rejection_curve(r),
    )




def sample_size(r):
    prop = r["parameter"] == "proportion"
    margin = (
        f"{fmt(r['error'] * 100)} puntos porcentuales" if prop else f"{fmt(r['error'])} unidades"
    )
    data = f"Confianza = {fmt(r['confidence'] * 100)} %; E = {fmt(r['error'])}; " + (
        f"p = {fmt(r['p'])}; q = {fmt(1 - r['p'])}." if prop else f"σ prevista = {fmt(r['sd'])}."
    )
    if r["finite"]:
        data += f" N = {r['population']}."
    return base(
        "TAMAÑO DE MUESTRA · " + ("PROPORCIÓN" if prop else "MEDIA"),
        f"n = {r['n']} observaciones",
        f"Para una confianza del {fmt(r['confidence'] * 100)} % y un margen de error de {margin}.",
        [
            ("Valor crítico Z", fmt(r["z"])),
            ("n₀ sin corrección", fmt(r["n0"])),
            ("n sin redondear", fmt(r["exact"])),
        ],
        [
            ("Datos del problema", data),
            ("Tamaño inicial", f"{r['formula']}. z = {fmt(r['z'])} → n₀ = {fmt(r['n0'])}."),
            (
                "Corrección por población finita",
                f"n = n₀ / [1 + (n₀ − 1)/N] = {fmt(r['exact'])}. Se supone muestreo sin reemplazo."
                if r["finite"]
                else "No se aplica: población grande o de tamaño desconocido.",
            ),
            ("Redondear hacia arriba", f"n = techo({fmt(r['exact'])}) = {r['n']}."),
        ],
        [
            "Esta planificación no incorpora no respuesta, efecto de diseño ni potencia de una prueba. Para una media utiliza una desviación poblacional conocida o una estimación previa razonable."
        ],
        "Muestra requerida",
        charts.size_chart(r),
    )




def compare(r):
    op, h0 = alternative(r["tail"])
    kind = r["type"]
    labels = {
        "z": "MEDIAS INDEPENDIENTES · Z (σ conocidas)",
        "z_sample": "MEDIAS INDEPENDIENTES · Z (muestras grandes)",
        "paired": "MEDIAS RELACIONADAS · t",
        "pooled": "MEDIAS INDEPENDIENTES · t COMBINADA",
        "welch": "MEDIAS INDEPENDIENTES · WELCH",
    }
    error = {
        "z": f"EE = √(σA²/nA + σB²/nB) = {fmt(r['se'])}.",
        "z_sample": f"EE = √(sA²/nA + sB²/nB) = {fmt(r['se'])}; ambas muestras ≥ 30.",
        "paired": f"Se calculan diferencias pareja a pareja. EE = sD/√n = {fmt(r['se'])}.",
        "welch": f"EE = √(sA²/nA + sB²/nB) = {fmt(r['se'])}. Grados de libertad de Welch–Satterthwaite.",
        "pooled": f"sp² = [(nA−1)sA² + (nB−1)sB²]/(nA+nB−2); EE = sp√(1/nA+1/nB) = {fmt(r['se'])}.",
    }[kind]
    warnings = [
        "Pares correctamente alineados e independientes entre sí; diferencias aproximadamente normales para muestras pequeñas."
        if kind == "paired"
        else "Grupos independientes; normalidad aproximada o muestras suficientes sin valores atípicos graves."
    ]
    if kind == "pooled":
        warnings.append(
            "Este método supone varianzas poblacionales iguales. Si no puedes justificarlo, utiliza Welch."
        )
    return base(
        labels[kind],
        decision(r),
        decision_text(r),
        test_metrics(r),
        [
            (
                "Definir el contraste",
                f"H₀: μA − μB {h0} {fmt(r['delta'])}. H₁: μA − μB {op} {fmt(r['delta'])}. Diferencia observada A − B = {fmt(r['estimate'])}.",
            ),
            ("Error estándar", error),
            (
                "Estadístico Z" if kind in ("z", "z_sample") else "Estadístico t",
                f"{'t' if r['df'] else 'Z'} = ({fmt(r['estimate'])} − {fmt(r['delta'])}) / {fmt(r['se'])} = {fmt(r['statistic'])}; gl = {fmt(r['df']) if r['df'] else 'no aplica'}.",
            ),
            ("Decisión", f"p {'≤' if r['reject'] else '>'} α. {decision(r)}."),
        ],
        warnings,
        "Comparación y región de rechazo",
        charts.rejection_curve(r),
    )




def sampling(r):
    if r.get("source") == "summary":
        warnings = []
        if any(group["n"] == 0 for group in r["allocation"]):
            warnings.append("Hay estratos con muestra cero. Revisa n si necesitas representar todos los estratos.")
        result = base(
            "AFIJACIÓN PROPORCIONAL",
            f"{r['n']} personas distribuidas entre {len(r['allocation'])} estratos",
            "Se calcula cuántas personas corresponden a cada estrato. Para elegir personas concretas, usa Registros individuales.",
            [("Población N", str(r["N"])), ("Muestra n", str(r["n"])),
             ("Fracción de muestreo", fmt(r["n"] / r["N"] * 100) + " %")],
            [("Población total", "N = " + " + ".join(str(g["N"]) for g in r["allocation"]) + f" = {r['N']}"),
             ("Fórmula", "nₕ = (Nₕ / N) × n"),
             *[(g["name"], f"({g['N']} / {r['N']}) × {r['n']} = {fmt(g['quota'])}; muestra asignada: {g['n']}.") for g in r["allocation"]],
             ("Redondeo", "Si las cuotas tienen decimales, se toman sus partes enteras y las plazas restantes se asignan a los mayores restos. Los empates siguen el orden ingresado. La suma final es exactamente n.")],
            warnings, "Fracción de la población a muestrear", charts.size_chart(r, selected=True),
        )
        result["table"] = {
            "headers": ["Estrato", "Población Nₕ", "Proporción", "Muestra nₕ"],
            "rows": [[g["name"], str(g["N"]), fmt(g["proportion"] * 100) + " %", str(g["n"])] for g in r["allocation"]]
                    + [["Total", str(r["N"]), "100 %", str(r["n"])]]
        }
        return result
    method = r["method"]
    algorithm = (
        "Fisher–Yates parcial: en cada paso se elige uniformemente un registro de los que quedan."
    )
    if method == "systematic":
        algorithm = f"Intervalo k = N/n = {fmt(r['k'])}. Inicio uniforme en [0,k): {fmt(r['start'])}. Índices base 0: piso(inicio + i × k)."
    elif method == "stratified":
        algorithm = f"Asignación {'Nₕ × sₕ (Neyman)' if r['allocationType'] == 'neyman' else 'proporcional a Nₕ'}, redondeo por restos mayores y redistribución si un estrato alcanza su capacidad. MAS dentro de cada estrato."
    warnings = [
        "Revisa el orden de la base: la periodicidad puede afectar la representatividad."
        if method == "systematic"
        else "La base debe cubrir la población de interés; la selección aleatoria no corrige sesgos de cobertura."
    ]
    if any(group["n"] == 0 for group in r["allocation"]):
        warnings.append(
            "Hay estratos sin representación. Aumenta n o revisa la asignación antes de inferir sobre toda la población."
        )
    if r["allocationType"] == "neyman":
        warnings.append("Neyman supone costos iguales y dispersiones auxiliares representativas.")
    result = base(
        "MUESTREO SIN REEMPLAZO",
        f"{r['n']} registros seleccionados",
        "La misma base, orden, método y semilla producen la misma selección.",
        [
            ("Población N", str(r["N"])),
            ("Fracción de muestreo", fmt(r["n"] / r["N"] * 100) + " %"),
            ("Semilla", str(r["seed"])),
        ],
        [
            (
                "Preparar la base",
                f"{r['N']} identificadores únicos. Semilla pseudoaleatoria {r['seed']}.",
            ),
            ("Algoritmo", algorithm),
            (
                "Resultado",
                " · ".join(
                    f"{group['name']}: {group['n']} de {group['N']}" for group in r["allocation"]
                )
                if r["allocation"]
                else "Selección sin duplicados. Descarga todos los registros con el botón CSV.",
            ),
        ],
        warnings,
        "Registros de la muestra",
        charts.size_chart(r, selected=True),
    )
    result["preview"] = " · ".join(row["id"] for row in r["selected"][:100])
    result["download"] = {"filename": "muestra-episs.csv", "content": csv_export(r["selected"])}
    return result


def interpolation(r):
    return {
        "label": "RESULTADO · " + ("EXTRAPOLACIÓN" if r["outside"] else "INTERPOLACIÓN"),
        "headline": f"y ≈ {r['y']:.12g}".replace(".", ","),
        "conclusion": f"Para x = {fmt(r['x'])}. "
        + (
            "Aviso: está fuera del intervalo conocido."
            if r["outside"]
            else "Dentro del intervalo conocido."
        ),
        "steps": [
            (
                "Sustituir los datos",
                f"y = ({fmt(r['y1'])}) + [({fmt(r['x'])} − ({fmt(r['x1'])})) / ({fmt(r['x2'])} − ({fmt(r['x1'])}))] × ({fmt(r['y2'])} − ({fmt(r['y1'])}))",
            ),
            ("Calcular la proporción", f"(x − x₁) / (x₂ − x₁) ≈ {fmt(r['t'])}"),
            ("Obtener el resultado", f"y ≈ {r['y']:.12g}".replace(".", ",")),
        ],
        "chart": charts.interpolation_chart(r),
    }



