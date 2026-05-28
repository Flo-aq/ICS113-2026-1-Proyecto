"""
Filtra los N colegios con mayor matrícula por comuna de la Región 5 (Valparaíso)
y estima su capacidad como refugio de emergencia según OGUC / DS548 / Mineduc.

Edita los parámetros en el bloque __main__ y ejecuta:
    python Datos/colegios/filtrar_colegios.py

Archivos de referencia generados automáticamente si no existen:
    columnas_colegios.json  — mapa nombre↔índice de todas las columnas de Colegios.csv
    ../comunas.json         — mapa ID→nombre de todas las comunas de Región 5

Ver normativa_recintos_escolares.md para la justificación de los parámetros de capacidad.
"""
import csv
import json
import math
import os
import unicodedata
from collections import defaultdict

BASE          = os.path.dirname(os.path.abspath(__file__))
COLEGIOS_CSV  = os.path.join(BASE, "Colegios.csv")
COLUMNAS_JSON = os.path.join(BASE, "columnas_colegios.json")
COMUNAS_JSON  = os.path.join(os.path.dirname(BASE), "comunas.json")

# Parámetros normativos de capacidad (ver normativa_recintos_escolares.md)
AREA_AULA_M2_POR_ALUMNO   = 2.5   # Guía Mineduc (rango 2.0–3.2 m²/alumno)
AREA_PATIO_M2_POR_ALUMNO  = 2.5   # OGUC Art. 4.5.x (mín. ~2.5 m²/alumno)
AREA_MULTICANCHA_M2       = 540   # 18×30 m; OGUC exige si matrícula ≥ 135
FACTOR_USO_REFUGIO        = 0.65  # Fracción del área total usable como albergue
M2_POR_PERSONA            = 3.5   # Estándar SPHERE mínimo para refugio

# Costos por persona de capacidad — ver Datos/parametros/costos_pma.md
_CAP_REF  = 500
_F_REF    = 22_500_000   # CLP fijo por apertura (referencia cap=500)
_O_REF    =  2_800_000   # CLP operativo/día (referencia cap=500)
_REQ_REF  = 3            # EES mínimos (referencia cap=500)
_REQ_MIN  = 2            # Mínimo absoluto de equipos


# ---------------------------------------------------------------------------
# Utilidades (compatibles con generar_datos.py)
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def parse_coord(value: str) -> float:
    return float(str(value).replace(",", "."))


# ---------------------------------------------------------------------------
# Generación de JSONs de referencia
# ---------------------------------------------------------------------------

def _gen_columnas_json() -> dict:
    """Lee headers de Colegios.csv y escribe columnas_colegios.json."""
    with open(COLEGIOS_CSV, encoding="latin-1", newline="") as f:
        raw = next(csv.reader(f, delimiter=";"))
    headers = [h.strip() for h in raw if h.strip()]

    por_nombre = {h: i for i, h in enumerate(headers)}
    por_indice = {str(i): h for i, h in enumerate(headers)}
    utiles = ["RBD", "NOM_RBD", "COD_REG_RBD", "NOM_COM_RBD",
              "RURAL_RBD", "LATITUD", "LONGITUD", "MAT_TOTAL", "ESTADO_ESTAB"]
    columnas_utiles = [por_nombre[c] for c in utiles if c in por_nombre]

    data = {"por_nombre": por_nombre, "por_indice": por_indice,
            "columnas_utiles": columnas_utiles}
    with open(COLUMNAS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def _gen_comunas_json() -> dict:
    """Lee Colegios.csv y escribe comunas_region5.json con todas las comunas de Región 5."""
    vistas: dict[str, str] = {}
    with open(COLEGIOS_CSV, encoding="latin-1", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("COD_REG_RBD") != "5":
                continue
            nom = normalize(row.get("NOM_COM_RBD", ""))
            if nom and nom not in vistas:
                vistas[nom] = row.get("COD_COM_RBD", "")

    data = {
        str(i + 1): {"nombre": nom, "cod_com": vistas[nom]}
        for i, nom in enumerate(sorted(vistas))
    }
    with open(COMUNAS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


# ---------------------------------------------------------------------------
# Cálculo de capacidad y costos
# ---------------------------------------------------------------------------

def _params_colegio(cap_j: int) -> tuple[int, int, int]:
    """Retorna (f_j, o_j, req_j) escalados linealmente con cap_j."""
    f_j   = round(_F_REF / _CAP_REF * cap_j)
    o_j   = round(_O_REF / _CAP_REF * cap_j)
    req_j = max(_REQ_MIN, math.ceil(_REQ_REF / _CAP_REF * cap_j))
    return f_j, o_j, req_j

def _estimar_capacidad(matricula: int, holgura: float) -> tuple[int, int, int]:
    """
    Retorna (area_total_m2, cap_base, cap_con_holgura).

    holgura: porcentaje firmado.  +20 → 20% más capacidad.  -20 → 20% menos.
    """
    area_multicancha = AREA_MULTICANCHA_M2 if matricula >= 135 else 0
    area_total = (
        matricula * AREA_AULA_M2_POR_ALUMNO
        + matricula * AREA_PATIO_M2_POR_ALUMNO
        + area_multicancha
    )
    area_util  = area_total * FACTOR_USO_REFUGIO
    cap_base   = math.floor(area_util / M2_POR_PERSONA)
    cap_holgura = math.floor(cap_base * (1 + holgura / 100))
    return round(area_total), cap_base, cap_holgura


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def filtrar_colegios(
    n: int = 2,
    holgura: float = 0.0,
    comunas: list[int] | None = None,
    comunas_nombres: list[str] | None = None,
    columnas: list[int] | None = None,
    min_matricula: int = 300,
    salida: str = "colegios_filtrados.csv",
    regenerar_comunas: bool = False,
) -> None:
    """
    Filtra los N colegios más grandes por matrícula en las comunas indicadas y
    escribe un CSV con las columnas seleccionadas más estimaciones de capacidad.

    Parámetros
    ----------
    n               Top-N colegios por matrícula por comuna.
    holgura         % aplicado sobre cap_base: positivo → más, negativo → menos.
    comunas         IDs del JSON de comunas (None = todas las comunas de Región 5).
    comunas_nombres Nombres normalizados de comunas (alternativa a comunas por ID).
                    Si se pasa, tiene precedencia sobre comunas.
    columnas        Índices de columnas a incluir (None = columnas_utiles del JSON).
    min_matricula   Matrícula mínima para considerar un colegio.
    salida          Nombre del archivo CSV de salida (relativo a Datos/colegios/).
    regenerar_comunas  Fuerza regenerar comunas_region5.json aunque ya exista.
    """
    # 1. Cargar / generar JSONs de referencia
    if not os.path.exists(COLUMNAS_JSON):
        _gen_columnas_json()
    with open(COLUMNAS_JSON, encoding="utf-8") as f:
        col_map = json.load(f)

    if not os.path.exists(COMUNAS_JSON) or regenerar_comunas:
        _gen_comunas_json()
    with open(COMUNAS_JSON, encoding="utf-8") as f:
        comunas_map: dict[str, dict] = json.load(f)

    # Índices y nombres de columnas que irán al output
    col_indices = columnas if columnas is not None else col_map["columnas_utiles"]
    col_names   = [col_map["por_indice"][str(i)] for i in col_indices]

    # Nombres normalizados de las comunas a filtrar
    if comunas_nombres is not None:
        nombres_filtro = {normalize(n) for n in comunas_nombres}
    elif comunas is not None:
        nombres_filtro = {
            comunas_map[str(c)]["nombre"]
            for c in comunas
            if str(c) in comunas_map
        }
    else:
        nombres_filtro = {v["nombre"] for v in comunas_map.values()}

    idx = col_map["por_nombre"]   # alias corto

    # 2. Leer y filtrar Colegios.csv
    schools_by_com: dict[str, list] = defaultdict(list)
    with open(COLEGIOS_CSV, encoding="latin-1", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # saltar header
        for raw in reader:
            if len(raw) <= max(idx["COD_REG_RBD"], idx["ESTADO_ESTAB"],
                               idx["RURAL_RBD"], idx["NOM_COM_RBD"], idx["MAT_TOTAL"]):
                continue
            if raw[idx["COD_REG_RBD"]] != "5":
                continue
            if raw[idx["ESTADO_ESTAB"]] != "1":
                continue
            if raw[idx["RURAL_RBD"]] != "0":
                continue
            nom_com = normalize(raw[idx["NOM_COM_RBD"]])
            if nom_com not in nombres_filtro:
                continue
            try:
                matricula = int(raw[idx["MAT_TOTAL"]] or 0)
                parse_coord(raw[idx["LATITUD"]])
                parse_coord(raw[idx["LONGITUD"]])
            except (ValueError, IndexError):
                continue
            if matricula < min_matricula:
                continue
            schools_by_com[nom_com].append(raw)

    # 3. Top-N por matrícula por comuna
    selected: list[tuple[str, list]] = []
    for nom_com in sorted(schools_by_com):
        top = sorted(
            schools_by_com[nom_com],
            key=lambda r: int(r[idx["MAT_TOTAL"]] or 0),
            reverse=True,
        )
        for row in top[:n]:
            selected.append((nom_com, row))

    # 4. Escribir CSV de salida
    out_path = os.path.join(BASE, salida)
    # cap_j = cap_con_holgura (alias uniforme para construir_instancia.py)
    extra_headers = ["cap_area_m2", "cap_personas", "cap_j", "f_j", "o_j", "req_j"]

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(col_names + extra_headers)
        for _nom_com, row in selected:
            matricula = int(row[idx["MAT_TOTAL"]] or 0)
            area, cap_base, cap_j = _estimar_capacidad(matricula, holgura)
            f_j, o_j, req_j = _params_colegio(cap_j)
            subset = [row[i] if i < len(row) else "" for i in col_indices]
            writer.writerow(subset + [area, cap_base, cap_j, f_j, o_j, req_j])

    # 5. Resumen
    comunas_cubiertas = sorted({nom for nom, _ in selected})
    print(f"Colegios escritos : {len(selected)}")
    print(f"Comunas cubiertas : {len(comunas_cubiertas)}")
    print(f"Holgura aplicada  : {holgura:+.1f}%")
    print(f"Archivo generado  : {out_path}")
    print(f"Columnas output   : {col_names + extra_headers}")


# ---------------------------------------------------------------------------
# Punto de entrada — edita los parámetros aquí
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    filtrar_colegios(
        n=2,
        holgura=0.0,
        comunas=None,       # None = todas las comunas de Región 5
                            # Ejemplo solo 5 comunas del modelo: [8, 27, 35, 36, 37]
        columnas=None,      # None = columnas_utiles del JSON
                            # Ejemplo personalizado: [1, 3, 11, 17, 18, 40]
        min_matricula=300,
        salida="colegios_filtrados.csv",
    )
