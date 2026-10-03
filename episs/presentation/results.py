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
        else f"x̄ = {fmt(r['mean'])}; {'s' if r['df'] else 'σ'} = {fmt(r['sd'])}."
    )
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
        (
            "Intervalo bilateral complementario",
            f"IC del {fmt(r['confidence'] * 100)} %: [{fmt(r['ci'][0])}; {fmt(r['ci'][1])}]. "
            + ("Método de Wilson. " if prop else "")
            + "Para una prueba unilateral este intervalo bilateral no es su regla de decisión equivalente.",
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


def interval(r):
    prop = r["method"] == "proportion"
    return base(
        f"INTERVALO BILATERAL · {r['methodLabel']}",
        f"[{fmt(r['ci'][0])}; {fmt(r['ci'][1])}]",
        f"Intervalo de confianza del {fmt(r['confidence'] * 100)} % para {'la proporción poblacional' if prop else 'la media poblacional'}.",
        [
            ("Estimación", fmt(r["estimate"])),
            ("Valor crítico", fmt(r["q"])),
            ("Semiancho", fmt(r["margin"])),
        ],
        [
            (
                "Datos",
                f"n = {r['n']}; estimación = {fmt(r['estimate'])}; confianza = {fmt(r['confidence'] * 100)} %. "
                + (f"Éxitos = {r['success']}." if prop else f"Desviación = {fmt(r['sd'])}."),
            ),
            ("Fórmula", r["formula"]),
            (
                "Sustituir y calcular",
                f"Valor crítico = {fmt(r['q'])}; centro = {fmt(r['center'])}; semiancho = {fmt(r['margin'])}. Límites: {fmt(r['center'])} ± {fmt(r['margin'])}.",
            ),
            (
                "Interpretar",
                f"En muestreos repetidos, aproximadamente el {fmt(r['confidence'] * 100)} % de los intervalos construidos por este procedimiento cubrirían el parámetro poblacional. No es la probabilidad de que el parámetro fijo esté en este intervalo.",
            ),
        ],
        [
            "Supone muestreo aleatorio e independencia. Para medias con muestras pequeñas, se requiere normalidad aproximada y ausencia de valores atípicos importantes."
        ],
        "Intervalo estimado",
        charts.interval_chart(r),
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


def variance(r):
    op, h0 = alternative(r["tail"])
    chi = r["type"] == "chi"
    return base(
        "UNA VARIANZA · χ²" if chi else "RAZÓN DE VARIANZAS · F",
        decision(r),
        decision_text(r),
        test_metrics(r),
        [
            (
                "Plantear la alternativa",
                f"H₀: σ² {h0} {fmt(r['v0'])}. H₁: σ² {op} {fmt(r['v0'])}. Se evalúa en la frontera."
                if chi
                else f"H₀: σ₁²/σ₂² {h0} 1. H₁: σ₁²/σ₂² {op} 1.",
            ),
            (
                "Calcular",
                f"χ² = (n − 1)s²/σ₀² = {r['d1']} × {fmt(r['s1'] ** 2)} / {fmt(r['v0'])} = {fmt(r['statistic'])}."
                if chi
                else f"F = s₁²/s₂² = {fmt(r['s1'] ** 2)} / {fmt(r['s2'] ** 2)} = {fmt(r['statistic'])}. Se conserva el orden A/B.",
            ),
            (
                "Grados de libertad y región",
                f"gl₁ = {r['d1']}"
                + (f"; gl₂ = {r['d2']}" if r["d2"] else "")
                + f". Rechazar por debajo de {fmt(r['low'])} o por encima de {fmt(r['high'])}; 0 o ∞ no añaden una cola de rechazo.",
            ),
            (
                "Intervalo bilateral",
                f"IC {fmt(r['confidence'] * 100)} % para {'σ²' if chi else 'σ₁²/σ₂²'}: [{fmt(r['ci'][0])}; {fmt(r['ci'][1])}]. No equivale a la decisión unilateral.",
            ),
            (
                "Decisión",
                f"Comparar p = {p_text(r['p'])} con α = {fmt(r['alpha'])}. {decision(r)}.",
            ),
        ],
        [
            "Requiere poblaciones normales, muestreo aleatorio e independencia. Estas pruebas son sensibles a la falta de normalidad."
        ],
        "Distribución nula y rechazo",
        charts.variance_curve(r),
    )


def compare(r):
    op, h0 = alternative(r["tail"])
    kind = r["type"]
    labels = {
        "paired": "MEDIAS RELACIONADAS · t",
        "pooled": "MEDIAS INDEPENDIENTES · t COMBINADA",
        "welch": "MEDIAS INDEPENDIENTES · WELCH",
    }
    error = {
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
                "Estadístico t",
                f"t = ({fmt(r['estimate'])} − {fmt(r['delta'])}) / {fmt(r['se'])} = {fmt(r['statistic'])}; gl = {fmt(r['df'])}.",
            ),
            (
                "Intervalo bilateral para μA − μB",
                f"[{fmt(r['ci'][0])}; {fmt(r['ci'][1])}], confianza {fmt(r['confidence'] * 100)} %. No equivale a una regla unilateral.",
            ),
            ("Decisión", f"p {'≤' if r['reject'] else '>'} α. {decision(r)}."),
        ],
        warnings,
        "Comparación y región de rechazo",
        charts.rejection_curve(r),
    )


def power(r):
    conclusion = (
        f"Se requieren al menos {r['required']} observaciones para una potencia de {fmt(r['target'] * 100)} % bajo este efecto y modelo."
        if r["required"]
        else "No se alcanza la potencia objetivo entre 2 y 1 000 000 observaciones. Revisa el efecto y la dirección de H₁."
    )
    return base(
        "PLANIFICACIÓN · POTENCIA Z",
        f"Potencia: {fmt(r['value'] * 100)} %",
        conclusion,
        [
            ("Error tipo I · α", fmt(r["alpha"])),
            ("Error tipo II · β", fmt(r["beta"])),
            ("n mínimo", str(r["required"]) if r["required"] else "No alcanzable"),
        ],
        [
            (
                "Definir el efecto",
                f"μ₁ − μ₀ = {fmt(r['delta'])}; σ = {fmt(r['sd'])}; n = {r['n']}.",
            ),
            (
                "Desplazamiento",
                f"λ = (μ₁−μ₀)√n/σ = {fmt(r['shift'])}. Valor crítico = {fmt(r['q'])}.",
            ),
            (
                "Potencia y errores",
                f"Potencia = P(rechazar H₀ | efecto indicado) = {fmt(r['value'])}. β = 1 − potencia = {fmt(r['beta'])}. α es la probabilidad de falso positivo bajo H₀.",
            ),
            (
                "Optimizar n",
                f"Se busca el menor entero n ≥ 2 que cumple la potencia objetivo, con límite de 1 000 000. Resultado: {r['required'] or 'no alcanzable'}.",
            ),
        ],
        [
            "Cálculo para una media, σ conocida e independencia. La potencia depende del efecto elegido; no es la probabilidad de que H₁ sea verdadera."
        ],
        "Potencia según tamaño de muestra",
        charts.power_chart(r),
    )


def sampling(r):
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
