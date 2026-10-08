"""Selección sin reemplazo y asignación estratificada reproducible."""

import csv
import io
import math
import statistics

from .validation import InputError, choice, count, number


class Mulberry32:
    """Conservar la semilla y las selecciones de la versión JavaScript anterior."""

    def __init__(self, seed):
        self.state = seed

    def random(self):
        mask = 0xFFFFFFFF
        self.state = (self.state + 0x6D2B79F5) & mask
        value = self.state
        value = ((value ^ (value >> 15)) * (value | 1)) & mask
        value ^= (value + ((value ^ (value >> 7)) * (value | 61) & mask)) & mask
        return ((value ^ (value >> 14)) & mask) / 4294967296


def parse_records(records):
    if isinstance(records, str):
        rows = []
        for line in records.splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split(";")]
            if len(parts) > 3 or not parts[0]:
                raise InputError("Usa identificador;estrato;valor, sin encabezado.")
            rows.append(
                {
                    "id": parts[0],
                    "stratum": parts[1] if len(parts) > 1 else "",
                    "value": parts[2] if len(parts) > 2 and parts[2] else None,
                }
            )
    else:
        rows = records
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100_000:
        raise InputError("La base debe contener entre 1 y 100 000 registros.")
    result = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise InputError("Cada registro necesita un identificador de texto.")
        stratum = row.get("stratum", "")
        if not isinstance(stratum, str):
            raise InputError("El estrato debe ser texto.")
        value = row.get("value")
        result.append(
            {
                "id": row["id"].strip(),
                "stratum": stratum.strip(),
                "value": number(value, "Valor auxiliar") if value is not None else None,
            }
        )
    if len({row["id"] for row in result}) != len(result):
        raise InputError("Los identificadores deben ser únicos.")
    return result


def shuffle_pick(rows, n, random):
    pool = list(rows)
    for i in range(n):
        j = i + math.floor(random() * (len(pool) - i))
        pool[i], pool[j] = pool[j], pool[i]
    return pool[:n]


def allocate(groups, n, neyman=False):
    """Restos mayores, redistribuyendo estratos que alcanzan su capacidad."""
    allocation = [0] * len(groups)
    remaining, active = n, list(range(len(groups)))
    while remaining and active:
        sizes = {i: groups[i]["N"] if "N" in groups[i] else len(groups[i]["rows"]) for i in active}
        weights = [sizes[i] * (groups[i]["sd"] if neyman else 1) for i in active]
        if all(weight == 0 for weight in weights):
            weights = [sizes[i] for i in active]
        total = sum(weights)
        shares = [
            {
                "i": i,
                "quota": remaining * weights[j] / total,
                "cap": sizes[i] - allocation[i],
            }
            for j, i in enumerate(active)
        ]
        saturated = [share for share in shares if share["quota"] >= share["cap"]]
        if saturated:
            for share in saturated:
                allocation[share["i"]] += share["cap"]
                remaining -= share["cap"]
            active = [i for i in active if i not in {share["i"] for share in saturated}]
            continue
        for share in shares:
            amount = math.floor(share["quota"])
            allocation[share["i"]] += amount
            remaining -= amount
        shares.sort(key=lambda share: (-(share["quota"] % 1), share["i"]))
        for share in shares:
            if remaining == 0:
                break
            if allocation[share["i"]] < sizes[share["i"]]:
                allocation[share["i"]] += 1
                remaining -= 1
        break
    return allocation


def summary_allocation(data):
    """Afijación proporcional con totales: nₕ = (Nₕ / N) × n.

    Los restos mayores conservan exactamente n al repartir cuotas no enteras.
    No se crean personas ficticias ni se seleccionan registros individuales.
    """
    choice(data.get("method"), ("stratified",), "Método para datos resumidos")
    choice(data.get("allocation", "proportional"), ("proportional",), "Asignación con totales")
    raw = data.get("strata")
    if not isinstance(raw, str):
        raise InputError("Introduce un estrato por línea: nombre;cantidad.")
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not 1 <= len(lines) <= 1000:
        raise InputError("Introduce entre 1 y 1000 estratos.")
    groups, names = [], set()
    for line in lines:
        parts = [part.strip() for part in line.split(";")]
        if len(parts) != 2 or not parts[0]:
            raise InputError("Usa nombre;cantidad, sin encabezado, en cada línea.")
        name = parts[0]
        if name.casefold() in names:
            raise InputError("Cada estrato debe tener un nombre diferente.")
        names.add(name.casefold())
        groups.append({"name": name, "N": count(parts[1], f"Población de {name}")})
    total = sum(group["N"] for group in groups)
    n = count(data.get("n"), "Tamaño de la muestra n", 1, total)
    amounts = allocate(groups, n)
    for group, amount in zip(groups, amounts):
        group.update(n=amount, proportion=group["N"] / total, quota=group["N"] * n / total)
    return {"source": "summary", "method": "stratified", "allocationType": "proportional",
            "N": total, "n": n, "allocation": groups}


def sampling(data):
    source = choice(data.get("source", "records"), ("records", "summary"), "Tipo de datos")
    if source == "summary":
        return summary_allocation(data)
    rows = parse_records(data.get("records", data.get("rows")))
    n = count(data.get("n"), "Tamaño n", 1, len(rows))
    seed = count(data.get("seed"), "Semilla", 0, 2**32 - 1)
    method = choice(data.get("method"), ("mas", "systematic", "stratified"), "Método de muestreo")
    random = Mulberry32(seed).random
    N = len(rows)
    allocation, k, start = [], None, None
    assignment = None
    if method == "mas":
        selected = shuffle_pick(rows, n, random)
    elif method == "systematic":
        k = N / n
        start = random() * k
        selected = [rows[math.floor(start + i * k)] for i in range(n)]
    else:
        assignment = choice(
            data.get("allocation", "proportional"), ("proportional", "neyman"), "Asignación"
        )
        grouped = {}
        for row in rows:
            if not row["stratum"]:
                raise InputError("Cada registro necesita un estrato.")
            grouped.setdefault(row["stratum"], []).append(row)
        groups = []
        for name, members in grouped.items():
            sd = None
            if assignment == "neyman":
                if any(row["value"] is None for row in members):
                    raise InputError("Neyman requiere valores numéricos en todos los registros.")
                sd = statistics.stdev(row["value"] for row in members) if len(members) > 1 else 0.0
            groups.append({"name": name, "rows": members, "sd": sd})
        sizes = allocate(groups, n, assignment == "neyman")
        selected = []
        for group, size in zip(groups, sizes):
            selected.extend(shuffle_pick(group["rows"], size, random))
            allocation.append(
                {"name": group["name"], "N": len(group["rows"]), "n": size, "sd": group["sd"]}
            )
    return {
        "selected": selected,
        "N": N,
        "n": n,
        "seed": seed,
        "method": method,
        "allocationType": assignment,
        "allocation": allocation,
        "k": k,
        "start": start,
    }


def csv_export(selected):
    """CSV UTF-8 para Excel; neutralizar campos que parezcan fórmulas."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writerow(["identificador", "estrato", "valor"])
    for row in selected:
        cells = []
        for key in ("id", "stratum", "value"):
            value = "" if row.get(key) is None else str(row[key])
            if value.lstrip().startswith(("=", "+", "-", "@")):
                value = "'" + value
            cells.append(value)
        writer.writerow(cells)
    return "\ufeff" + output.getvalue()
