"""
parametrizar_hospitales.py
==========================
Lee establecimientos_valparaiso_vigentes.csv y calcula Cap_{k,t} para t=1..7
según las curvas de recuperación post-sismo documentadas en
Datos/parametros/capacidad_hospitalaria.md.

Uso standalone:
    python Datos/hospitales/parametrizar_hospitales.py

Salida:
    Datos/hospitales/hospitales_parametrizados.csv
"""
import csv
import math
import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_CSV  = os.path.join(BASE_DIR, "establecimientos_valparaiso_vigentes.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "hospitales_parametrizados.csv")

# ---------------------------------------------------------------------------
# Parámetros de clasificación
# Ver Datos/parametros/capacidad_hospitalaria.md
# ---------------------------------------------------------------------------

TSUNAMI_THRESHOLD = 30  # metros s.n.m. (cota 30, SENAPRED/SHOA)

# Hospitales con evacuación vertical a pesar de estar bajo cota 30
VERTICAL_EVAC = {
    "Hospital Carlos Van Buren (Valparaíso)",
    "Hospital Dr. Gustavo Fricke (Viña del Mar)",
}

# Hospitales modernos/base-isolated reconstruidos post-27F
HOSPITALES_MODERNOS = {
    "Hospital Dr. Gustavo Fricke (Viña del Mar)",
    "Hospital San Camilo de San Felipe",
    "Hospital San Juan de Dios (Los Andes)",
    "Hospital Biprovincial Quillota Petorca",
    "Hospital de Quilpué",
}

# Curvas de recuperación: fracción de Camas2023 por día t=1..7
# Fuente: Datos/parametros/capacidad_hospitalaria.md
CURVAS: dict[str, list[float]] = {
    "tsunami_flood":    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    "tsunami_vertical": [0.00, 0.00, 0.20, 0.30, 0.40, 0.50, 0.60],
    "moderno_alto":     [0.85, 0.88, 0.91, 0.94, 0.96, 0.98, 1.00],
    "antiguo_alto":     [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80],
    "bajo_publico":     [0.30, 0.38, 0.47, 0.55, 0.63, 0.70, 0.75],
    "privado":          [0.80, 0.85, 0.90, 0.95, 1.00, 1.00, 1.00],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).strip())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper()


def clasificar(nombre: str, altitud: float, tipo: str, nivel: str) -> str:
    """Asigna categoría a un hospital según las reglas del markdown."""
    if altitud < TSUNAMI_THRESHOLD:
        return "tsunami_vertical" if nombre in VERTICAL_EVAC else "tsunami_flood"
    if tipo == "Clínica":
        return "privado"
    if nombre in HOSPITALES_MODERNOS:
        return "moderno_alto"
    if "Alta" in nivel:
        return "antiguo_alto"
    return "bajo_publico"


def parametrizar(dias: int = 7) -> list[dict]:
    hospitales = []
    with open(INPUT_CSV, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=1):
            nombre   = row["EstablecimientoGlosa"].strip()
            comuna   = row["ComunaGlosa"].strip()
            lat      = float(row["Latitud"])
            lon      = float(row["Longitud"])
            camas    = int(float(row["Camas2023"]))
            altitud  = float(row["Altitud_m"])
            tipo     = row["TipoEstablecimientoGlosa"].strip()
            nivel    = row.get("NivelComplejidadEstabGlosa", "").strip()

            cat  = clasificar(nombre, altitud, tipo, nivel)
            curv = CURVAS[cat]
            caps = [max(0, math.floor(camas * curv[t])) for t in range(dias)]

            hospitales.append(dict(
                id=i,
                nombre=nombre,
                comuna=comuna,
                lat=lat,
                lon=lon,
                Camas2023=camas,
                Altitud_m=altitud,
                categoria=cat,
                **{f"Cap_{t+1}": caps[t] for t in range(dias)},
            ))

    return hospitales


def escribir_csv(hospitales: list[dict], dias: int = 7) -> None:
    cap_cols = [f"Cap_{t}" for t in range(1, dias + 1)]
    header = ["id", "nombre", "comuna", "lat", "lon",
              "Camas2023", "Altitud_m", "categoria"] + cap_cols
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for h in hospitales:
            w.writerow([h[c] for c in header])


def main() -> None:
    hospitales = parametrizar()
    escribir_csv(hospitales)

    print(f"hospitales_parametrizados.csv — {len(hospitales)} establecimientos\n")
    print(f"{'Nombre':<52} {'Cat':<18} {'Camas':>5} {'Cap1':>5} {'Cap7':>5}")
    print("-" * 85)
    for h in hospitales:
        print(f"{h['nombre']:<52} {h['categoria']:<18} "
              f"{h['Camas2023']:>5} {h['Cap_1']:>5} {h['Cap_7']:>5}")

    cats = {}
    for h in hospitales:
        cats[h["categoria"]] = cats.get(h["categoria"], 0) + 1
    print("\nDistribución por categoría:")
    for cat, n in sorted(cats.items()):
        print(f"  {cat:<20}: {n}")


if __name__ == "__main__":
    main()
