"""Núcleo compartido para generar instancias del modelo de triaje post-sismo."""
from __future__ import annotations

import csv
import math
import os
import random
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field

BASE = os.path.dirname(os.path.abspath(__file__))
COLEGIOS_PATH = os.path.join(BASE, "Colegios.csv")
POBLACION_PATH = os.path.join(BASE, "poblacion_comunas_censo2024_consolidado.csv")

DIAS = 7
T_MAX = 30
TAU_TOTAL = 0.005
PROP = {"leve": 0.74, "moderado": 0.26}
PHI = [0.25, 0.20, 0.15, 0.12, 0.10, 0.10, 0.08]
FACTOR_CAMAS = 0.907 * 0.85
VEL_KMH = 25
FACTOR_VIAL = 1.35
MAT_MIN_DEFAULT = 300

# Nombres en Colegios.csv -> clave en poblacion_comunas_censo2024_consolidado.csv
POBLACION_ALIASES = {
    "CALERA": "LA CALERA",
    "LLAILLAY": "LLAY LLAY",
}

HOSPITALES = [
    {
        "id": 1,
        "nombre": "Hospital Carlos Van Buren",
        "comuna": "Valparaiso",
        "lat": -33.0472,
        "lon": -71.6054,
        "camas_base": 400,
    },
    {
        "id": 2,
        "nombre": "Hospital Eduardo Pereira",
        "comuna": "Valparaiso",
        "lat": -33.0401,
        "lon": -71.6210,
        "camas_base": 350,
    },
    {
        "id": 3,
        "nombre": "Hospital Gustavo Fricke",
        "comuna": "Vina del Mar",
        "lat": -33.0245,
        "lon": -71.5568,
        "camas_base": 450,
    },
]

# Instancia reducida original (Informe 2)
COMUNAS_INFORME2 = [
    {"nombre": "Vina del Mar", "poblacion": 334871, "aliases": ["VIÑA DEL MAR", "VINA DEL MAR"]},
    {"nombre": "Valparaiso", "poblacion": 284938, "aliases": ["VALPARAÍSO", "VALPARAISO"]},
    {"nombre": "Quilpue", "poblacion": 162559, "aliases": ["QUILPUÉ", "QUILPUE"]},
    {"nombre": "Villa Alemana", "poblacion": 139571, "aliases": ["VILLA ALEMANA"]},
    {"nombre": "Concon", "poblacion": 48294, "aliases": ["CONCÓN", "CONCON"]},
]


@dataclass
class InstanceConfig:
    """Parámetros de una corrida del generador."""

    output_dir: str
    comunas_meta: list[dict] = field(default_factory=list)
    escuelas_por_comuna: int | None = 2
    mat_min: int = MAT_MIN_DEFAULT
    seed: int | None = None
    etiqueta: str = "instancia"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def display_name(raw_name: str) -> str:
    """Nombre legible sin tildes forzadas (consistente con CSVs actuales)."""
    key = normalize(raw_name)
    mapping = {
        "VINA DEL MAR": "Vina del Mar",
        "VALPARAISO": "Valparaiso",
        "QUILPUE": "Quilpue",
        "VILLA ALEMANA": "Villa Alemana",
        "CONCON": "Concon",
        "SAN ANTONIO": "San Antonio",
        "QUILLOTA": "Quillota",
        "SAN FELIPE": "San Felipe",
        "LOS ANDES": "Los Andes",
        "LIMACHE": "Limache",
        "LA CALERA": "La Calera",
        "CALERA": "La Calera",
        "CONCÓN": "Concon",
        "QUINTERO": "Quintero",
        "CASABLANCA": "Casablanca",
        "CABILDO": "Cabildo",
        "LA LIGUA": "La Ligua",
        "NOGALES": "Nogales",
        "PUCHUNCAVI": "Puchuncavi",
        "OLMUE": "Olmué",
        "EL QUISCO": "El Quisco",
        "LLAY LLAY": "Llay Llay",
        "LLAILLAY": "Llay Llay",
        "PUTAENDO": "Putaendo",
        "EL TABO": "El Tabo",
        "CARTAGENA": "Cartagena",
        "PETORCA": "Petorca",
        "PAPUDO": "Papudo",
        "ZAPALLAR": "Zapallar",
        "ALGARROBO": "Algarrobo",
        "SANTO DOMINGO": "Santo Domingo",
        "ISLA DE PASCUA": "Isla de Pascua",
        "JUAN FERNANDEZ": "Juan Fernandez",
        "CALLE LARGA": "Calle Larga",
        "CATEMU": "Catemu",
        "HIJUELAS": "Hijuelas",
        "LA CRUZ": "La Cruz",
        "PANQUEHUE": "Panquehue",
        "RINCONADA": "Rinconada",
        "SAN ESTEBAN": "San Esteban",
        "SANTA MARIA": "Santa Maria",
    }
    if key in mapping:
        return mapping[key]
    return raw_name.strip().title()


def parse_coord(value) -> float:
    return float(str(value).replace(",", "."))


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def tiempo_min(lat1, lon1, lat2, lon2) -> int:
    km = haversine_km(lat1, lon1, lat2, lon2) * FACTOR_VIAL
    return max(1, round(km / VEL_KMH * 60))


def write_csv(output_dir: str, filename: str, header: list, rows: list) -> None:
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def load_poblacion_censo() -> dict[str, int]:
    poblacion = {}
    if not os.path.isfile(POBLACION_PATH):
        return poblacion
    with open(POBLACION_PATH, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            comuna = row.get("Comuna", "").strip()
            raw = row.get("Población_2024", row.get("Poblacion_2024", "0"))
            try:
                pob = int(str(raw).replace(",", "").replace(".", ""))
            except ValueError:
                continue
            poblacion[normalize(comuna)] = pob
    return poblacion


def poblacion_para_comuna(norm_key: str, matricula_total: int, poblacion_censo: dict[str, int]) -> int:
    if norm_key in poblacion_censo:
        return poblacion_censo[norm_key]
    alias = POBLACION_ALIASES.get(norm_key)
    if alias and normalize(alias) in poblacion_censo:
        return poblacion_censo[normalize(alias)]
    # Estimación: ~3.2 habitantes por alumno matriculado (aprox. cobertura escolar regional)
    return max(matricula_total * 3, 5000)


def load_all_schools_by_commune(mat_min: int) -> dict[str, list[dict]]:
    """Agrupa colegios urbanos activos región 5 por nombre de comuna normalizado."""
    schools: dict[str, list[dict]] = defaultdict(list)
    with open(COLEGIOS_PATH, encoding="latin-1", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("COD_REG_RBD") != "5":
                continue
            if row.get("ESTADO_ESTAB") != "1" or row.get("RURAL_RBD") != "0":
                continue
            try:
                matricula = int(row["MAT_TOTAL"] or 0)
                lat = parse_coord(row["LATITUD"])
                lon = parse_coord(row["LONGITUD"])
            except (TypeError, ValueError, KeyError):
                continue
            if matricula < mat_min:
                continue
            norm_key = normalize(row.get("NOM_COM_RBD", ""))
            if not norm_key:
                continue
            schools[norm_key].append(
                {
                    "rbd": row["RBD"],
                    "nombre": row["NOM_RBD"].strip(),
                    "comuna_raw": row["NOM_COM_RBD"],
                    "norm_key": norm_key,
                    "matricula": matricula,
                    "lat": lat,
                    "lon": lon,
                }
            )
    return dict(schools)


def comunas_meta_from_keys(
    norm_keys: list[str],
    schools_by_commune: dict[str, list[dict]],
    poblacion_override: dict[str, int] | None = None,
) -> list[dict]:
    poblacion_censo = load_poblacion_censo()
    if poblacion_override:
        poblacion_censo.update(poblacion_override)

    meta = []
    for idx, norm_key in enumerate(norm_keys, 1):
        records = schools_by_commune.get(norm_key, [])
        if not records:
            raise ValueError(f"Sin colegios para comuna '{norm_key}'")
        mat_total = sum(r["matricula"] for r in records)
        nombre = display_name(records[0]["comuna_raw"])
        pob = poblacion_para_comuna(norm_key, mat_total, poblacion_censo)
        meta.append(
            {
                "id": idx,
                "nombre": nombre,
                "norm_key": norm_key,
                "poblacion": pob,
                "aliases": list({norm_key, normalize(records[0]["comuna_raw"])}),
            }
        )
    return meta


def comunas_meta_informe2() -> list[dict]:
    """Las 5 comunas fijas del script original."""
    meta = []
    for idx, c in enumerate(COMUNAS_INFORME2, 1):
        meta.append(
            {
                "id": idx,
                "nombre": c["nombre"],
                "norm_key": normalize(c["aliases"][0]),
                "poblacion": c["poblacion"],
                "aliases": [normalize(a) for a in c["aliases"]],
            }
        )
    return meta


def load_schools_for_meta(comunas_meta: list[dict], mat_min: int) -> dict[int, list[dict]]:
    alias_to_id: dict[str, int] = {}
    for comuna in comunas_meta:
        for alias in comuna["aliases"]:
            alias_to_id[normalize(alias)] = comuna["id"]
        alias_to_id[normalize(comuna["nombre"])] = comuna["id"]
        if "norm_key" in comuna:
            alias_to_id[comuna["norm_key"]] = comuna["id"]

    schools: dict[int, list[dict]] = defaultdict(list)
    with open(COLEGIOS_PATH, encoding="latin-1", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("COD_REG_RBD") != "5":
                continue
            if row.get("ESTADO_ESTAB") != "1" or row.get("RURAL_RBD") != "0":
                continue
            comuna_id = alias_to_id.get(normalize(row.get("NOM_COM_RBD", "")))
            if comuna_id is None:
                continue
            try:
                matricula = int(row["MAT_TOTAL"] or 0)
                lat = parse_coord(row["LATITUD"])
                lon = parse_coord(row["LONGITUD"])
            except (TypeError, ValueError):
                continue
            if matricula < mat_min:
                continue
            schools[comuna_id].append(
                {
                    "rbd": row["RBD"],
                    "nombre": row["NOM_RBD"].strip(),
                    "comuna_raw": row["NOM_COM_RBD"],
                    "matricula": matricula,
                    "lat": lat,
                    "lon": lon,
                }
            )

    for comuna in comunas_meta:
        if not schools[comuna["id"]]:
            raise ValueError(f"Sin colegios urbanos para {comuna['nombre']}")
    return schools


def weighted_centroid(records: list[dict]) -> tuple[float, float]:
    total = sum(r["matricula"] for r in records)
    lat = sum(r["matricula"] * r["lat"] for r in records) / total
    lon = sum(r["matricula"] * r["lon"] for r in records) / total
    return lat, lon


def centro_params(mat: int) -> tuple[int, int, int, int]:
    cap_j = round(mat * 0.6)
    if mat >= 1500:
        return cap_j, 250, 30, 4
    if mat >= 1200:
        return cap_j, 220, 25, 3
    return cap_j, 180, 20, 2


def select_centers(
    comunas_meta: list[dict],
    schools_by_commune: dict[int, list[dict]],
    escuelas_por_comuna: int | None,
) -> list[dict]:
    centros = []
    for comuna in comunas_meta:
        top = sorted(schools_by_commune[comuna["id"]], key=lambda s: s["matricula"], reverse=True)
        if escuelas_por_comuna is None:
            selected = top
        else:
            selected = top[:escuelas_por_comuna]
        for school in selected:
            cap_j, f_j, o_j, req_j = centro_params(school["matricula"])
            centros.append(
                {
                    "rbd": school["rbd"],
                    "nombre": school["nombre"],
                    "comuna": comuna["nombre"],
                    "comuna_id": comuna["id"],
                    "lat": school["lat"],
                    "lon": school["lon"],
                    "matricula": school["matricula"],
                    "cap_j": cap_j,
                    "f_j": f_j,
                    "o_j": o_j,
                    "req_j": req_j,
                }
            )
    for idx, centro in enumerate(centros, 1):
        centro["id"] = idx
    return centros


def build_comunas(comunas_meta: list[dict], schools_by_commune: dict[int, list[dict]]) -> list[dict]:
    comunas = []
    for meta in comunas_meta:
        lat, lon = weighted_centroid(schools_by_commune[meta["id"]])
        comunas.append(
            {
                "id": meta["id"],
                "nombre": meta["nombre"],
                "poblacion": meta["poblacion"],
                "lat": round(lat, 6),
                "lon": round(lon, 6),
            }
        )
    return comunas


def distribute_demand(comunas: list[dict]) -> dict:
    raw = defaultdict(float)
    totals_ig = defaultdict(float)
    for comuna in comunas:
        total_inj = comuna["poblacion"] * TAU_TOTAL
        for gravedad, prop in PROP.items():
            totals_ig[(comuna["id"], gravedad)] = total_inj * prop
            for t, phi in enumerate(PHI, 1):
                raw[(comuna["id"], t, gravedad)] = total_inj * prop * phi

    demanda = {}
    for comuna in comunas:
        for gravedad in PROP:
            target = round(totals_ig[(comuna["id"], gravedad)])
            keys = [(comuna["id"], t, gravedad) for t in range(1, DIAS + 1)]
            rounded = [int(raw[k]) for k in keys]
            diff = target - sum(rounded)
            fracs = sorted(zip(keys, [raw[k] - int(raw[k]) for k in keys]), key=lambda x: -x[1])
            for k in range(abs(diff)):
                key = fracs[k % len(keys)][0]
                pos = keys.index(key)
                rounded[pos] += 1 if diff > 0 else -1
            for t, val in enumerate(rounded, 1):
                demanda[(comuna["id"], t, gravedad)] = max(0, val)
    return demanda


def operational_params(num_centros: int, num_comunas: int) -> tuple[list[int], list[int]]:
    maxc = max(3, min(num_centros, round(num_centros * 0.65)))
    maxc_por_dia = [maxc, maxc, maxc, max(3, maxc - 1), max(3, maxc - 1), max(3, maxc - 1), maxc]
    h_base = max(30, 25 + num_comunas * 2)
    h_por_dia = [
        h_base,
        h_base - 2,
        h_base - 5,
        h_base - 5,
        h_base - 8,
        h_base - 8,
        h_base - 6,
    ]
    return maxc_por_dia, h_por_dia


CAP_HOSP_VAR = [1.0, 0.95, 0.90, 0.88, 0.85, 0.85, 0.90]


def print_coverage_report(comunas: list[dict], centros: list[dict]) -> None:
    print("\nCobertura triaje (A_ij=1 si tiempo <= T_max):")
    for comuna in comunas:
        reachable = sum(
            1
            for centro in centros
            if tiempo_min(comuna["lat"], comuna["lon"], centro["lat"], centro["lon"]) <= T_MAX
        )
        print(f"  {comuna['nombre']}: {reachable}/{len(centros)} centros")

    print("Cobertura hospitalaria (A_ik=1 si tiempo <= T_max):")
    for comuna in comunas:
        reachable = sum(
            1
            for hospital in HOSPITALES
            if tiempo_min(comuna["lat"], comuna["lon"], hospital["lat"], hospital["lon"]) <= T_MAX
        )
        print(f"  {comuna['nombre']}: {reachable}/{len(HOSPITALES)} hospitales")


def list_communes_available(mat_min: int) -> list[str]:
    schools = load_all_schools_by_commune(mat_min)
    return sorted(schools.keys(), key=lambda k: display_name(schools[k][0]["comuna_raw"]))


def sample_communes(n: int, mat_min: int, seed: int | None) -> list[str]:
    available = list_communes_available(mat_min)
    if n > len(available):
        raise ValueError(
            f"Solo hay {len(available)} comunas con colegios (mat>={mat_min}); "
            f"se pidieron {n}."
        )
    rng = random.Random(seed)
    return sorted(rng.sample(available, n), key=lambda k: display_name(k))


def generate_instance(config: InstanceConfig) -> None:
    os.makedirs(config.output_dir, exist_ok=True)

    schools_by_commune = load_schools_for_meta(config.comunas_meta, config.mat_min)
    comunas = build_comunas(config.comunas_meta, schools_by_commune)
    centros = select_centers(config.comunas_meta, schools_by_commune, config.escuelas_por_comuna)
    demanda = distribute_demand(comunas)
    maxc_por_dia, h_por_dia = operational_params(len(centros), len(comunas))

    write_csv(
        config.output_dir,
        "nodos_comunas.csv",
        ["id", "nombre", "lat", "lon", "poblacion"],
        [(c["id"], c["nombre"], c["lat"], c["lon"], c["poblacion"]) for c in comunas],
    )

    write_csv(
        config.output_dir,
        "nodos_centros.csv",
        ["id", "rbd", "nombre", "comuna", "lat", "lon", "matricula", "cap_j", "f_j", "o_j", "req_j"],
        [
            (
                c["id"],
                c["rbd"],
                c["nombre"],
                c["comuna"],
                round(c["lat"], 6),
                round(c["lon"], 6),
                c["matricula"],
                c["cap_j"],
                c["f_j"],
                c["o_j"],
                c["req_j"],
            )
            for c in centros
        ],
    )

    write_csv(
        config.output_dir,
        "nodos_hospitales.csv",
        ["id", "nombre", "comuna", "lat", "lon", "camas_base", "cap_k"],
        [
            (
                h["id"],
                h["nombre"],
                h["comuna"],
                h["lat"],
                h["lon"],
                h["camas_base"],
                round(h["camas_base"] * FACTOR_CAMAS),
            )
            for h in HOSPITALES
        ],
    )

    write_csv(
        config.output_dir,
        "cap_hospital_dia.csv",
        ["k", "t", "cap_k_t"],
        [
            (h["id"], t, round(h["camas_base"] * FACTOR_CAMAS * CAP_HOSP_VAR[t - 1]))
            for h in HOSPITALES
            for t in range(1, DIAS + 1)
        ],
    )

    tiempos_ij = []
    for comuna in comunas:
        for centro in centros:
            mins = tiempo_min(comuna["lat"], comuna["lon"], centro["lat"], centro["lon"])
            tiempos_ij.append((comuna["id"], centro["id"], mins))
    write_csv(config.output_dir, "tiempos_ij.csv", ["i", "j", "minutos"], tiempos_ij)

    tiempos_ik = []
    for comuna in comunas:
        for hospital in HOSPITALES:
            mins = tiempo_min(comuna["lat"], comuna["lon"], hospital["lat"], hospital["lon"])
            tiempos_ik.append((comuna["id"], hospital["id"], mins))
    write_csv(config.output_dir, "tiempos_ik.csv", ["i", "k", "minutos"], tiempos_ik)

    cobertura_ij = [(i, j, 1 if m <= T_MAX else 0) for i, j, m in tiempos_ij]
    cobertura_ik = [(i, k, 1 if m <= T_MAX else 0) for i, k, m in tiempos_ik]
    write_csv(config.output_dir, "cobertura_ij.csv", ["i", "j", "A_ij"], cobertura_ij)
    write_csv(config.output_dir, "cobertura_ik.csv", ["i", "k", "A_ik"], cobertura_ik)

    write_csv(
        config.output_dir,
        "demanda.csv",
        ["i", "t", "g", "D_i_t_g"],
        [
            (comuna["id"], t, g, demanda[(comuna["id"], t, g)])
            for comuna in comunas
            for t in range(1, DIAS + 1)
            for g in PROP
        ],
    )

    dmax = defaultdict(int)
    for (i, t, g), val in demanda.items():
        dmax[(i, g)] = max(dmax[(i, g)], val)

    write_csv(
        config.output_dir,
        "demanda_max.csv",
        ["i", "g", "D_i_g_max"],
        [(comuna["id"], g, dmax[(comuna["id"], g)]) for comuna in comunas for g in PROP],
    )

    write_csv(config.output_dir, "personal_dia.csv", ["t", "H_t"], [(t, h) for t, h in enumerate(h_por_dia, 1)])
    write_csv(
        config.output_dir,
        "max_centros_dia.csv",
        ["t", "MaxC_t"],
        [(t, m) for t, m in enumerate(maxc_por_dia, 1)],
    )

    pres = round(sum(c["f_j"] for c in centros) * 0.65)
    escuelas_label = (
        "todos"
        if config.escuelas_por_comuna is None
        else str(config.escuelas_por_comuna)
    )
    params = [
        ("T_max", T_MAX, "minutos", "Tiempo maximo de viaje permitido (supuesto informe)"),
        ("Pres", pres, "UF", "Presupuesto total (65% costo fijo abrir todos los centros)"),
        ("L", 3, "dias", "Dias minimos de operacion de un centro abierto"),
        ("P_leve", 1, "peso", "Peso prioridad pacientes leves"),
        ("P_moderado", 10, "peso", "Peso prioridad pacientes moderados"),
        ("ratio_leve", 20, "pacientes/equipo/dia", "Capacidad atencion leves por equipo"),
        ("ratio_moderado", 10, "pacientes/equipo/dia", "Capacidad atencion moderados por equipo"),
        ("horizonte_dias", DIAS, "dias", "Horizonte temporal T"),
        ("tau_total_heridos", TAU_TOTAL, "por_mil", "Tasa heridos leves+moderados (MMI VIII)"),
        ("prop_leve", PROP["leve"], "proporcion", "Fraccion leve sobre demanda modelada"),
        ("prop_moderado", PROP["moderado"], "proporcion", "Fraccion moderado sobre demanda modelada"),
        ("factor_camas_post_desastre", round(FACTOR_CAMAS, 4), "proporcion", "Camas operativas post 27-F"),
        ("velocidad_emergencia_kmh", VEL_KMH, "km/h", "Velocidad prudente en emergencia"),
        ("factor_vial", FACTOR_VIAL, "adimensional", "Factor correccion Haversine a ruta real"),
        ("escuelas_por_comuna", escuelas_label, "centros", "Centros candidatos por comuna"),
        ("mat_min", config.mat_min, "alumnos", "Matricula minima para considerar colegio"),
        ("instancia", config.etiqueta, "texto", "Tipo de instancia generada"),
        ("num_comunas", len(comunas), "comunas", "Comunas en la instancia"),
        ("num_centros", len(centros), "centros", "Centros de triaje candidatos"),
        ("seed", config.seed if config.seed is not None else "", "entero", "Semilla aleatoria (si aplica)"),
    ]
    write_csv(config.output_dir, "parametros.csv", ["parametro", "valor", "unidad", "descripcion"], params)

    print(f"\n=== {config.etiqueta} ===")
    print("Salida:", config.output_dir)
    print(f"Comunas: {len(comunas)} | Centros: {len(centros)} | Hospitales: {len(HOSPITALES)}")
    if config.seed is not None:
        print(f"Semilla: {config.seed}")
    print("\nComunas incluidas:")
    for c in comunas:
        n_centros = sum(1 for centro in centros if centro["comuna_id"] == c["id"])
        print(f"  [{c['id']}] {c['nombre']} (pob={c['poblacion']:,}, centros={n_centros})")

    for fn in sorted(os.listdir(config.output_dir)):
        with open(os.path.join(config.output_dir, fn), encoding="utf-8") as f:
            rows = sum(1 for _ in f) - 1
        print(f"  {fn}: {rows} filas")

    total_demanda = sum(demanda.values())
    print(f"\nDemanda total (leve+moderado, 7 dias): {total_demanda}")
    print_coverage_report(comunas, centros)
