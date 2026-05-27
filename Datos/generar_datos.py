"""Genera instancia reducida alineada al modelo del Informe 2 (G = {leve, moderado})."""
import csv
import math
import os
import unicodedata
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
COLEGIOS_PATH = os.path.join(BASE, "Colegios.csv")

DIAS = 7
T_MAX = 30
TAU_TOTAL = 0.005  # 5 heridos / 1000 hab. (MMI VIII, Tabla Mercalli)
PROP = {"leve": 0.74, "moderado": 0.26}  # 70/25 
PHI = [0.25, 0.20, 0.15, 0.12, 0.10, 0.10, 0.08]
FACTOR_CAMAS = 0.907 * 0.85
VEL_KMH = 25
FACTOR_VIAL = 1.35
ESCUELAS_POR_COMUNA = 2   # Top 2 colegios urbanos por matricula en cada comuna (MINEDUC) 
#PARA GENERAR MAS DATOS SE PUEDE CAMBIAR A 3 O MAS :)
MAT_MIN = 300

COMUNAS_META = [
    {
        "id": 1,
        "nombre": "Vina del Mar",
        "poblacion": 334871,
        "aliases": ["VIÑA DEL MAR", "VINA DEL MAR"],
    },
    {
        "id": 2,
        "nombre": "Valparaiso",
        "poblacion": 284938,
        "aliases": ["VALPARAÍSO", "VALPARAISO"],
    },
    {
        "id": 3,
        "nombre": "Quilpue",
        "poblacion": 162559,
        "aliases": ["QUILPUÉ", "QUILPUE"],
    },
    {
        "id": 4,
        "nombre": "Villa Alemana",
        "poblacion": 139571,
        "aliases": ["VILLA ALEMANA"],
    },
    {
        "id": 5,
        "nombre": "Concon",
        "poblacion": 48294,
        "aliases": ["CONCÓN", "CONCON"],
    },
]

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

MAXC_POR_DIA = [6, 6, 6, 5, 5, 5, 6]
H_POR_DIA = [50, 48, 45, 45, 42, 42, 44]
CAP_HOSP_VAR = [1.0, 0.95, 0.90, 0.88, 0.85, 0.85, 0.90]


def normalize(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def parse_coord(value):
    return float(str(value).replace(",", "."))


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def tiempo_min(lat1, lon1, lat2, lon2):
    km = haversine_km(lat1, lon1, lat2, lon2) * FACTOR_VIAL
    return max(1, round(km / VEL_KMH * 60))


def write_csv(filename, header, rows):
    path = os.path.join(DATA, filename)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def load_schools_by_commune():
    alias_to_id = {}
    for comuna in COMUNAS_META:
        for alias in comuna["aliases"]:
            alias_to_id[normalize(alias)] = comuna["id"]

    schools = defaultdict(list)
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
            if matricula < MAT_MIN:
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

    for comuna in COMUNAS_META:
        if not schools[comuna["id"]]:
            raise ValueError(f"Sin colegios urbanos para {comuna['nombre']}")
    return schools


def weighted_centroid(records):
    total = sum(r["matricula"] for r in records)
    lat = sum(r["matricula"] * r["lat"] for r in records) / total
    lon = sum(r["matricula"] * r["lon"] for r in records) / total
    return lat, lon


def select_centers(schools_by_commune):
    centros = []
    for comuna in COMUNAS_META:
        top = sorted(schools_by_commune[comuna["id"]], key=lambda s: s["matricula"], reverse=True)
        selected = top[:ESCUELAS_POR_COMUNA]
        for school in selected:
            mat = school["matricula"]
            cap_j = round(mat * 0.6)
            if mat >= 1500:
                f_j, o_j, req_j = 250, 30, 4
            elif mat >= 1200:
                f_j, o_j, req_j = 220, 25, 3
            else:
                f_j, o_j, req_j = 180, 20, 2
            centros.append(
                {
                    "rbd": school["rbd"],
                    "nombre": school["nombre"],
                    "comuna": comuna["nombre"],
                    "comuna_id": comuna["id"],
                    "lat": school["lat"],
                    "lon": school["lon"],
                    "matricula": mat,
                    "cap_j": cap_j,
                    "f_j": f_j,
                    "o_j": o_j,
                    "req_j": req_j,
                }
            )
    for idx, centro in enumerate(centros, 1):
        centro["id"] = idx
    return centros


def build_comunas(schools_by_commune):
    comunas = []
    for meta in COMUNAS_META:
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


def distribute_demand(comunas):
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


def print_coverage_report(comunas, centros, tiempos_ij, tiempos_ik):
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


def main():
    os.makedirs(DATA, exist_ok=True)

    schools_by_commune = load_schools_by_commune()
    comunas = build_comunas(schools_by_commune)
    centros = select_centers(schools_by_commune)
    demanda = distribute_demand(comunas)

    write_csv(
        "nodos_comunas.csv",
        ["id", "nombre", "lat", "lon", "poblacion"],
        [(c["id"], c["nombre"], c["lat"], c["lon"], c["poblacion"]) for c in comunas],
    )

    write_csv(
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
    write_csv("tiempos_ij.csv", ["i", "j", "minutos"], tiempos_ij)

    tiempos_ik = []
    for comuna in comunas:
        for hospital in HOSPITALES:
            mins = tiempo_min(comuna["lat"], comuna["lon"], hospital["lat"], hospital["lon"])
            tiempos_ik.append((comuna["id"], hospital["id"], mins))
    write_csv("tiempos_ik.csv", ["i", "k", "minutos"], tiempos_ik)

    cobertura_ij = [(i, j, 1 if m <= T_MAX else 0) for i, j, m in tiempos_ij]
    cobertura_ik = [(i, k, 1 if m <= T_MAX else 0) for i, k, m in tiempos_ik]
    write_csv("cobertura_ij.csv", ["i", "j", "A_ij"], cobertura_ij)
    write_csv("cobertura_ik.csv", ["i", "k", "A_ik"], cobertura_ik)

    write_csv(
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
        "demanda_max.csv",
        ["i", "g", "D_i_g_max"],
        [(comuna["id"], g, dmax[(comuna["id"], g)]) for comuna in comunas for g in PROP],
    )

    write_csv("personal_dia.csv", ["t", "H_t"], [(t, h) for t, h in enumerate(H_POR_DIA, 1)])
    write_csv("max_centros_dia.csv", ["t", "MaxC_t"], [(t, m) for t, m in enumerate(MAXC_POR_DIA, 1)])

    pres = round(sum(c["f_j"] for c in centros) * 0.65)
    params = [
        ("T_max", T_MAX, "minutos", "Tiempo maximo de viaje permitido (supuesto informe)"),
        ("Pres", pres, "UF", "Presupuesto total (65% costo fijo abrir todos los centros)"),
        ("L", 3, "dias", "Dias minimos de operacion de un centro abierto"),
        ("P_leve", 1, "peso", "Peso prioridad pacientes leves"),
        ("P_moderado", 10, "peso", "Peso prioridad pacientes moderados"),
        ("ratio_leve", 20, "pacientes/equipo/dia", "Capacidad atencion leves por equipo"),
        ("ratio_moderado", 10, "pacientes/equipo/dia", "Capacidad atencion moderados por equipo"),
        ("horizonte_dias", DIAS, "dias", "Horizonte temporal T"),
        ("tau_total_heridos", TAU_TOTAL, "por_mil", "Tasa heridos leves+moderados (MMI VIII, Tabla Mercalli)"),
        ("prop_leve", PROP["leve"], "proporcion", "Fraccion leve sobre demanda modelada"),
        ("prop_moderado", PROP["moderado"], "proporcion", "Fraccion moderado sobre demanda modelada"),
        ("factor_camas_post_desastre", round(FACTOR_CAMAS, 4), "proporcion", "Camas operativas post 27-F (90.7% x 85%)"),
        ("velocidad_emergencia_kmh", VEL_KMH, "km/h", "Velocidad prudente en emergencia"),
        ("factor_vial", FACTOR_VIAL, "adimensional", "Factor correccion Haversine a ruta real"),
        ("escuelas_por_comuna", ESCUELAS_POR_COMUNA, "centros", "Muestra MINEDUC: top matricula por comuna"),
    ]
    write_csv("parametros.csv", ["parametro", "valor", "unidad", "descripcion"], params)

    print("Archivos generados en:", DATA)
    for fn in sorted(os.listdir(DATA)):
        with open(os.path.join(DATA, fn), encoding="utf-8") as f:
            rows = sum(1 for _ in f) - 1
        print(f"  {fn}: {rows} filas")

    total_demanda = sum(demanda.values())
    print(f"\nDemanda total (leve+moderado, 7 dias): {total_demanda}")
    print_coverage_report(comunas, centros, tiempos_ij, tiempos_ik)


if __name__ == "__main__":
    main()
