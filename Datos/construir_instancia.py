"""
construir_instancia.py
======================
Script maestro que combina colegios y recintos deportivos para generar
todos los CSVs de entrada del modelo Gurobi (en Datos/data/).

Uso directo:
    python Datos/construir_instancia.py

Uso desde código Gurobi:
    import sys; sys.path.insert(0, "Datos")
    from construir_instancia import cargar_comunas, cargar_centros, calcular_tiempos, ...

Ver Datos/parametros/ para la justificación de cada parámetro.
"""
import csv
import importlib.util
import json
import math
import os
import unicodedata
from collections import defaultdict

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BASE          = os.path.dirname(os.path.abspath(__file__))
COLEGIOS_CSV  = os.path.join(BASE, "colegios", "Colegios.csv")   # solo para cargar_comunas (centroide)
POBLACION_CSV = os.path.join(BASE, "poblacion_comunas_censo2024_consolidado.csv")
COL_JSON      = os.path.join(BASE, "colegios", "columnas_colegios.json")
COMUNAS_JSON       = os.path.join(BASE, "comunas.json")
COLEGIOS_FILTRADOS = os.path.join(BASE, "colegios", "colegios_filtrados.csv")
RECINTOS_FILTRADOS = os.path.join(BASE, "recintos", "recintos_filtrados.csv")
DATA_DIR           = os.path.join(BASE, "data")

# ---------------------------------------------------------------------------
# Carga de módulos específicos por tipo de recinto
# ---------------------------------------------------------------------------

def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_mod_col = _load_module(os.path.join(BASE, "colegios", "filtrar_colegios.py"), "filtrar_colegios")
_mod_rec = _load_module(os.path.join(BASE, "recintos", "filtrar_recintos.py"), "filtrar_recintos")

# ---------------------------------------------------------------------------
# Escenarios de recursos humanos
# Ver Datos/parametros/personal_y_capacidad.md
# ---------------------------------------------------------------------------
_ESCENARIOS = {
    1: dict(  # conservador (fuente: research_claude.md)
        H_t=[8, 12, 18, 24, 26, 28, 28],
        MaxC_t=[4, 5, 7, 8, 9, 10, 10],
        ratio_leve=25,
        ratio_moderado=10,
    ),
    2: dict(  # intermedio — default
        H_t=[10, 17, 29, 41, 49, 55, 59],
        MaxC_t=[2, 4, 6, 8, 10, 10, 10],
        ratio_leve=30,
        ratio_moderado=12,
    ),
    3: dict(  # optimista (fuente: research_gemini.md)
        H_t=[12, 22, 40, 58, 72, 82, 90],
        MaxC_t=[2, 4, 6, 10, 14, 16, 16],
        ratio_leve=96,
        ratio_moderado=36,
    ),
}

# ---------------------------------------------------------------------------
# Utilidades geográficas
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def parse_coord(value: str) -> float:
    return float(str(value).replace(",", "."))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def tiempo_min(lat1: float, lon1: float, lat2: float, lon2: float,
               factor_vial: float = 1.35, vel_kmh: float = 25) -> int:
    km = haversine_km(lat1, lon1, lat2, lon2) * factor_vial
    return max(1, round(km / vel_kmh * 60))


# ---------------------------------------------------------------------------
# Carga de comunas
# ---------------------------------------------------------------------------

def cargar_comunas(comunas_filtro: list[str] | None = None) -> list[dict]:
    """
    Lee las comunas de Región 5 desde el CSV de población y calcula
    el centroide ponderado por matrícula de colegios para cada una.

    Parámetros
    ----------
    comunas_filtro  Lista de nombres de comunas a incluir (None = todas las que
                    aparezcan en el CSV de población y tengan colegios válidos).

    Retorna
    -------
    Lista de dicts: id, nombre, lat, lon, poblacion
    """
    # 1. Leer población del CSV
    pop_map: dict[str, int] = {}
    with open(POBLACION_CSV, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            nombre = normalize(row["Comuna"])
            try:
                pop = int(str(row["Población_2024"]).replace(",", "").replace(".", "").strip())
            except ValueError:
                continue
            pop_map[nombre] = pop

    nombres_objetivo = (
        {normalize(c) for c in comunas_filtro}
        if comunas_filtro is not None
        else set(pop_map.keys())
    )

    # 2. Cargar columna JSON para acceder a Colegios.csv por índice
    with open(COL_JSON, encoding="utf-8") as f:
        col_map = json.load(f)
    idx = col_map["por_nombre"]

    # 3. Calcular centroide ponderado por matrícula para cada comuna objetivo
    schools: dict[str, list[tuple[float, float, int]]] = defaultdict(list)
    with open(COLEGIOS_CSV, encoding="latin-1", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for raw in reader:
            if len(raw) <= max(idx["COD_REG_RBD"], idx["MAT_TOTAL"], idx["LATITUD"], idx["LONGITUD"]):
                continue
            if raw[idx["COD_REG_RBD"]] != "5":
                continue
            if raw[idx["ESTADO_ESTAB"]] != "1" or raw[idx["RURAL_RBD"]] != "0":
                continue
            nom = normalize(raw[idx["NOM_COM_RBD"]])
            if nom not in nombres_objetivo:
                continue
            try:
                mat = int(raw[idx["MAT_TOTAL"]] or 0)
                lat = parse_coord(raw[idx["LATITUD"]])
                lon = parse_coord(raw[idx["LONGITUD"]])
            except (ValueError, IndexError):
                continue
            if mat < 1:
                continue
            schools[nom].append((lat, lon, mat))

    comunas: list[dict] = []
    for i, nom in enumerate(sorted(nombres_objetivo), start=1):
        if nom not in pop_map:
            continue
        pts = schools.get(nom, [])
        if not pts:
            print(f"  [ADVERTENCIA] Sin colegios para centroide de {nom} — commune omitida")
            continue
        total_mat = sum(m for _, _, m in pts)
        lat_c = sum(lat * m for lat, _, m in pts) / total_mat
        lon_c = sum(lon * m for _, lon, m in pts) / total_mat
        comunas.append(dict(id=i, nombre=nom, lat=round(lat_c, 6),
                            lon=round(lon_c, 6), poblacion=pop_map[nom]))

    return comunas


# ---------------------------------------------------------------------------
# Carga de centros (delega en filtrar_colegios.py y filtrar_recintos.py)
# ---------------------------------------------------------------------------

def cargar_centros(
    comunas: list[dict],
    n_colegios: int = 2,
    min_mat: int = 300,
    holgura: float = 0.0,
) -> list[dict]:
    """
    Llama a filtrar_colegios y filtrar_recintos para generar sus CSVs,
    luego los lee y combina en una lista unificada con IDs consecutivos.

    Parámetros
    ----------
    comunas     Lista devuelta por cargar_comunas().
    n_colegios  Top-N colegios por matrícula por comuna.
    min_mat     Matrícula mínima para considerar un colegio.
    holgura     % sobre cap_j de colegios (positivo → más capacidad).

    Retorna
    -------
    Lista de dicts: id, nombre, comuna, tipo, lat, lon, cap_j, f_j, o_j, req_j
    """
    nombres = [c["nombre"] for c in comunas]

    # Genera los CSVs intermedios (cada script maneja su lógica propia)
    _mod_col.filtrar_colegios(
        n=n_colegios, min_matricula=min_mat, holgura=holgura,
        comunas_nombres=nombres,
    )
    _mod_rec.filtrar_recintos(comunas_nombres=nombres)

    centros: list[dict] = []

    # Lee colegios_filtrados.csv
    with open(COLEGIOS_FILTRADOS, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            centros.append(dict(
                nombre=row["NOM_RBD"],
                comuna=row["NOM_COM_RBD"],
                tipo="colegio",
                lat=float(row["LATITUD"].replace(",", ".")),
                lon=float(row["LONGITUD"].replace(",", ".")),
                cap_j=int(row["cap_j"]),
                f_j=int(row["f_j"]),
                o_j=int(row["o_j"]),
                req_j=int(row["req_j"]),
            ))

    # Lee recintos_filtrados.csv
    with open(RECINTOS_FILTRADOS, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            centros.append(dict(
                nombre=row["nombre"],
                comuna=row["comuna"],
                tipo="estadio",
                lat=float(row["lat"]),
                lon=float(row["lon"]),
                cap_j=int(row["cap_j"]),
                f_j=int(row["f_j"]),
                o_j=int(row["o_j"]),
                req_j=int(row["req_j"]),
            ))

    for i, c in enumerate(centros, start=1):
        c["id"] = i

    return centros


# ---------------------------------------------------------------------------
# Tiempos y cobertura
# ---------------------------------------------------------------------------

def calcular_tiempos(
    comunas: list[dict],
    centros: list[dict],
    factor_vial: float = 1.35,
    vel_kmh: float = 25,
) -> dict[tuple[int, int], int]:
    """Retorna {(i_id, j_id): minutos} para cada par comuna–centro."""
    return {
        (i["id"], j["id"]): tiempo_min(i["lat"], i["lon"], j["lat"], j["lon"],
                                        factor_vial, vel_kmh)
        for i in comunas
        for j in centros
    }


def calcular_cobertura(
    tiempos: dict[tuple[int, int], int],
    t_max: int = 30,
) -> dict[tuple[int, int], int]:
    """Retorna {(i_id, j_id): 1|0} según tiempo ≤ t_max."""
    return {par: (1 if mins <= t_max else 0) for par, mins in tiempos.items()}


# ---------------------------------------------------------------------------
# Demanda
# ---------------------------------------------------------------------------

def calcular_demanda(
    comunas: list[dict],
    tau: float = 0.005,
    prop: dict[str, float] | None = None,
    phi: list[float] | None = None,
    dias: int = 7,
) -> dict[tuple[int, int, str], int]:
    """
    Calcula D_i,t,g = pop_i × tau × prop_g × phi_t.

    Retorna {(i_id, t, g): valor} con t ∈ {1..dias} y g ∈ prop.keys().
    Garantiza que la suma diaria por (i,g) cuadra exactamente con el total
    mediante ajuste de decimales.
    """
    if prop is None:
        prop = {"leve": 0.74, "moderado": 0.26}
    if phi is None:
        phi = [0.25, 0.20, 0.15, 0.12, 0.10, 0.10, 0.08]

    assert abs(sum(phi) - 1.0) < 1e-9, "PHI debe sumar 1"
    assert abs(sum(prop.values()) - 1.0) < 1e-9, "PROP debe sumar 1"
    phi = phi[:dias]

    demanda: dict[tuple[int, int, str], int] = {}
    for c in comunas:
        for g, pg in prop.items():
            total_g = c["poblacion"] * tau * pg
            raw = [total_g * p for p in phi]
            rounded = [int(v) for v in raw]
            diff = round(total_g) - sum(rounded)
            fracs = sorted(enumerate(raw), key=lambda x: -(x[1] % 1))
            for k in range(abs(diff)):
                pos = fracs[k % len(fracs)][0]
                rounded[pos] += 1 if diff > 0 else -1
            for t, val in enumerate(rounded, start=1):
                demanda[(c["id"], t, g)] = max(0, val)

    return demanda


# ---------------------------------------------------------------------------
# Parámetros escalares del modelo
# ---------------------------------------------------------------------------

def generar_parametros_escalares(
    centros: list[dict],
    escenario: int = 2,
    t_max: int = 30,
    l_min: int = 3,
    tau: float = 0.005,
    prop: dict[str, float] | None = None,
    phi: list[float] | None = None,
    dias: int = 7,
    pres: int | None = None,
    p_g: dict[str, int] | None = None,
) -> dict:
    """
    Genera el diccionario de parámetros escalares listos para el modelo.

    escenario   1=conservador, 2=intermedio (default), 3=optimista.
                Ver Datos/parametros/personal_y_capacidad.md.
    pres        Presupuesto total CLP. None → 1,200,000,000 CLP (Gemini).
    """
    if prop is None:
        prop = {"leve": 0.74, "moderado": 0.26}
    if phi is None:
        phi = [0.25, 0.20, 0.15, 0.12, 0.10, 0.10, 0.08]
    if p_g is None:
        p_g = {"leve": 1, "moderado": 10}
    if pres is None:
        pres = 1_200_000_000

    esc = _ESCENARIOS[escenario]

    return dict(
        T_max=t_max,
        L=l_min,
        Pres=pres,
        horizonte_dias=dias,
        escenario=escenario,
        tau_total=tau,
        prop=prop,
        phi=phi[:dias],
        p_g=p_g,
        ratio_leve=esc["ratio_leve"],
        ratio_moderado=esc["ratio_moderado"],
        H_t=esc["H_t"][:dias],
        MaxC_t=esc["MaxC_t"][:dias],
        factor_vial=1.35,
        vel_kmh=25,
    )


# ---------------------------------------------------------------------------
# Escritura de CSVs (nombres del modelo)
# ---------------------------------------------------------------------------

def escribir_csvs(
    output_dir: str,
    comunas: list[dict],
    centros: list[dict],
    tiempos: dict,
    cobertura: dict,
    demanda: dict,
    params: dict,
) -> None:
    """Escribe todos los CSVs en output_dir con los nombres del modelo E2."""
    os.makedirs(output_dir, exist_ok=True)

    def w(filename, header, rows):
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(header)
            csv.writer(f).writerows(rows)

    w("nodos_comunas.csv",
      ["id", "nombre", "lat", "lon", "poblacion"],
      [(c["id"], c["nombre"], c["lat"], c["lon"], c["poblacion"]) for c in comunas])

    w("nodos_centros.csv",
      ["id", "nombre", "comuna", "tipo", "lat", "lon", "cap_j", "f_j", "o_j", "req_j"],
      [(c["id"], c["nombre"], c["comuna"], c["tipo"],
        round(c["lat"], 6), round(c["lon"], 6),
        c["cap_j"], c["f_j"], c["o_j"], c["req_j"]) for c in centros])

    dias = params["horizonte_dias"]
    w("tiempos_ij.csv",
      ["i", "j", "minutos"],
      [(i, j, m) for (i, j), m in sorted(tiempos.items())])

    w("cobertura_ij.csv",
      ["i", "j", "A_ij"],
      [(i, j, a) for (i, j), a in sorted(cobertura.items())])

    gravs = list(params["prop"].keys())
    w("demanda.csv",
      ["i", "t", "g", "D_i_t_g"],
      [(i, t, g, v) for (i, t, g), v in sorted(demanda.items())])

    dmax: dict[tuple[int, str], int] = defaultdict(int)
    for (i, t, g), v in demanda.items():
        dmax[(i, g)] = max(dmax[(i, g)], v)
    w("demanda_max.csv",
      ["i", "g", "D_i_g_max"],
      [(i, g, v) for (i, g), v in sorted(dmax.items())])

    w("personal_dia.csv",
      ["t", "H_t"],
      [(t + 1, h) for t, h in enumerate(params["H_t"])])

    w("max_centros_dia.csv",
      ["t", "MaxC_t"],
      [(t + 1, m) for t, m in enumerate(params["MaxC_t"])])

    param_rows = [
        ("T_max",         params["T_max"],         "minutos",    "Tiempo máximo de viaje al PMA"),
        ("L",             params["L"],              "días",       "Mínimo días de operación continua"),
        ("Pres",          params["Pres"],           "CLP",        "Presupuesto total red de PMAs 7 días"),
        ("escenario",     params["escenario"],      "-",          "1=conservador 2=intermedio 3=optimista"),
        ("tau_total",     params["tau_total"],      "por_hab",    "Heridos/habitante (MMI VIII)"),
        ("prop_leve",     params["prop"]["leve"],   "proporcion", "Fracción heridos leves"),
        ("prop_moderado", params["prop"]["moderado"],"proporcion","Fracción heridos moderados"),
        ("P_leve",        params["p_g"]["leve"],    "peso",       "Peso prioridad leves en FO"),
        ("P_moderado",    params["p_g"]["moderado"],"peso",       "Peso prioridad moderados en FO"),
        ("ratio_leve",    params["ratio_leve"],     "pac/EES/día","Pacientes leves por equipo por día"),
        ("ratio_moderado",params["ratio_moderado"], "pac/EES/día","Pacientes moderados por equipo por día"),
        ("factor_vial",   params["factor_vial"],    "adimensional","Corrección Haversine → distancia real"),
        ("vel_kmh",       params["vel_kmh"],        "km/h",       "Velocidad emergencia post-terremoto"),
    ]
    w("parametros.csv",
      ["parametro", "valor", "unidad", "descripcion"],
      param_rows)

    print(f"\nArchivos generados en: {output_dir}")
    for fn in sorted(os.listdir(output_dir)):
        with open(os.path.join(output_dir, fn), encoding="utf-8") as f:
            rows = sum(1 for _ in f) - 1
        print(f"  {fn}: {rows} filas")


# ---------------------------------------------------------------------------
# Función principal — edita aquí los parámetros
# ---------------------------------------------------------------------------

def main(
    comunas_ids: list[int] | None = None,
    n_colegios: int = 2,
    holgura: float = 0.0,
    escenario: int = 2,
) -> None:
    """
    Construye la instancia completa del modelo y escribe todos los CSVs en data/.

    comunas_ids     Lista de IDs enteros de comunas.json (None = todas).
                    Ver comunas.json para el mapeo ID → nombre.
                    Ejemplo 5 comunas del modelo: [8, 27, 35, 36, 37]
                    (Concón=8, Quilpué=27, Valparaíso=35, Villa Alemana=36, Viña=37)
    n_colegios      Top-N colegios por matrícula por comuna.
    holgura         % sobre cap_j de colegios.
    escenario       1=conservador, 2=intermedio (default), 3=optimista.
    """
    with open(COMUNAS_JSON, encoding="utf-8") as f:
        com_map = json.load(f)

    if comunas_ids is not None:
        comunas_filtro = [com_map[str(i)]["nombre"] for i in comunas_ids if str(i) in com_map]
    else:
        comunas_filtro = None

    print("── Cargando comunas...")
    comunas = cargar_comunas(comunas_filtro)
    print(f"   {len(comunas)} comunas cargadas")

    print("── Cargando centros (colegios + recintos)...")
    centros = cargar_centros(comunas, n_colegios=n_colegios, holgura=holgura)
    n_col = sum(1 for c in centros if c["tipo"] == "colegio")
    n_rec = len(centros) - n_col
    print(f"   {len(centros)} centros ({n_col} colegios, {n_rec} recintos)")

    print("── Calculando tiempos y cobertura...")
    tiempos   = calcular_tiempos(comunas, centros)
    cobertura = calcular_cobertura(tiempos)
    n_cub = sum(v for v in cobertura.values())
    print(f"   {n_cub}/{len(cobertura)} pares cubiertos (tiempo ≤ 30 min)")

    print("── Calculando demanda...")
    demanda = calcular_demanda(comunas)
    total_d = sum(demanda.values())
    print(f"   Demanda total (leve+moderado, {len(set(t for _,t,_ in demanda.keys()))} días): {total_d}")

    print(f"── Generando parámetros (escenario={escenario})...")
    params = generar_parametros_escalares(centros, escenario=escenario)

    print("── Escribiendo CSVs...")
    escribir_csvs(DATA_DIR, comunas, centros, tiempos, cobertura, demanda, params)


if __name__ == "__main__":
    # IDs de comunas.json: Concón=8, Quilpué=27, Valparaíso=35, Villa Alemana=36, Viña del Mar=37
    main(
        comunas_ids=[8, 27, 35, 36, 37],
        n_colegios=2,
        holgura=0.0,
        escenario=2,
    )
