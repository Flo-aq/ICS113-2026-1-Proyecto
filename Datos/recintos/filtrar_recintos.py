"""
Filtra los recintos deportivos operativos (estadios, polideportivos) por comunas
y los prepara como centros candidatos de triaje para el modelo de optimización.

La capacidad cap_j se toma directamente de la columna Capacidad_Personas del CSV,
ya que los recintos deportivos tienen aforo certificado (no requiere estimación normativa).
Los costos (f_j, o_j, req_j) escalan linealmente con cap_j usando tasas de referencia
para estadios. Ver Datos/parametros/costos_pma.md.

Edita los parámetros en el bloque __main__ y ejecuta:
    python Datos/recintos/filtrar_recintos.py
"""
import csv
import math
import os
import unicodedata
from collections import Counter

BASE          = os.path.dirname(os.path.abspath(__file__))
RECINTOS_CSV  = os.path.join(BASE, "infraestructura_deportiva_consolidada.csv")
SALIDA_CSV    = os.path.join(BASE, "recintos_filtrados.csv")

COLUMNAS_SALIDA = ["id", "nombre", "comuna", "lat", "lon", "cap_j", "f_j", "o_j", "req_j"]

# Costos por persona de capacidad — ver Datos/parametros/costos_pma.md
_CAP_REF  = 3000
_F_REF    = 58_000_000   # CLP fijo por apertura (referencia cap=3000)
_O_REF    =  6_200_000   # CLP operativo/día (referencia cap=3000)
_REQ_REF  = 6            # EES mínimos (referencia cap=3000)
_REQ_MIN  = 3            # Mínimo absoluto de equipos


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.upper().strip()


def _params_estadio(cap_j: int) -> tuple[int, int, int]:
    """Retorna (f_j, o_j, req_j) escalados linealmente con cap_j."""
    f_j   = round(_F_REF / _CAP_REF * cap_j)
    o_j   = round(_O_REF / _CAP_REF * cap_j)
    req_j = max(_REQ_MIN, math.ceil(_REQ_REF / _CAP_REF * cap_j))
    return f_j, o_j, req_j


def filtrar_recintos(
    comunas_nombres: list[str] | None = None,
    tipos: list[str] | None = None,
    salida: str = SALIDA_CSV,
) -> list[dict]:
    """
    Filtra los recintos deportivos operativos y escribe el CSV de salida.

    Parámetros
    ----------
    comunas_nombres  Lista de nombres de comunas (None = todas).
    tipos            Lista de tipos a incluir, e.g. ["Estadio", "Polideportivo"]
                     (None = todos los tipos).
    salida           Ruta del CSV de salida.

    Retorna
    -------
    Lista de dicts con las columnas de COLUMNAS_SALIDA.
    """
    nombres_filtro = (
        {normalize(c) for c in comunas_nombres} if comunas_nombres is not None else None
    )
    tipos_filtro = (
        {normalize(t) for t in tipos} if tipos is not None else None
    )

    recintos: list[dict] = []

    with open(RECINTOS_CSV, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("Estado", "").strip() != "Operativo":
                continue

            comuna_norm = normalize(row.get("Comuna", ""))
            if nombres_filtro is not None and comuna_norm not in nombres_filtro:
                continue

            tipo = row.get("Tipo_Recinto", "").strip()
            if tipos_filtro is not None and normalize(tipo) not in tipos_filtro:
                continue

            try:
                lat   = float(row["Coordenada_Lat"].replace(",", "."))
                lon   = float(row["Coordenada_Lon"].replace(",", "."))
                cap_j = int(row["Capacidad_Personas"])
            except (ValueError, KeyError):
                continue

            f_j, o_j, req_j = _params_estadio(cap_j)

            recintos.append({
                "id":    int(row["ID"]),
                "nombre": row["Nombre"].strip(),
                "comuna": row["Comuna"].strip(),
                "lat":   lat,
                "lon":   lon,
                "cap_j": cap_j,
                "f_j":   f_j,
                "o_j":   o_j,
                "req_j": req_j,
            })

    with open(salida, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_SALIDA)
        writer.writeheader()
        writer.writerows(recintos)

    print(f"Recintos escritos : {len(recintos)} → {salida}")
    if recintos:
        por_tipo = Counter(row.get("Tipo_Recinto", "?") for row in
                           csv.DictReader(open(RECINTOS_CSV, encoding="utf-8"))
                           if row.get("Estado", "").strip() == "Operativo"
                           and (nombres_filtro is None or normalize(row.get("Comuna","")) in nombres_filtro))
        for tipo, n in sorted(por_tipo.items()):
            print(f"  {tipo}: {n}")

    return recintos


if __name__ == "__main__":
    filtrar_recintos(
        comunas_nombres=None,   # None = todos; ejemplo: ["Viña del Mar", "Valparaíso"]
        tipos=None,             # None = todos; ejemplo: ["Estadio", "Polideportivo"]
    )
