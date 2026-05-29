import unicodedata
import pandas as pd
import pdfplumber
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helpers de normalización
# ---------------------------------------------------------------------------

def norm_str(s):
    """Quita tildes, pasa a minúsculas y elimina espacios extra para comparar strings."""
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    # Descompone caracteres Unicode y elimina las marcas de acento (categoría Mn)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s

def norm_coord(s, decimals=3):
    """Redondea coordenada a `decimals` decimales para join espacial (~111m por decimal)."""
    try:
        return round(float(str(s).strip()), decimals)
    except (ValueError, TypeError):
        return None


def make_addr_key(df, com_col, num_col):
    """Clave compuesta: ComunaCodigo + '_' + Numero (normalizados)."""
    return df[com_col].map(norm_str) + "_" + df[num_col].map(norm_str)

def make_coord_key(df, lat_col, lon_col):
    """Clave compuesta: lat_3dec + '_' + lon_3dec."""
    lat = df[lat_col].map(norm_coord)
    lon = df[lon_col].map(norm_coord)
    valid = lat.notna() & lon.notna()
    key = pd.Series("", index=df.index)
    key[valid] = lat[valid].astype(str) + "_" + lon[valid].astype(str)
    return key


# ---------------------------------------------------------------------------
# Join en cascada con tres estrategias
# ---------------------------------------------------------------------------

def cascade_merge(df_base, df_src, extra_cols, label,
                  base_cod, src_cod,
                  base_com, src_com, base_num, src_num,
                  base_lat, src_lat, base_lon, src_lon):
    """
    Merge por tres estrategias en cascada:
      1. Código de establecimiento (exacto)
      2. ComunaCodigo + Numero (normalizado)
      3. Latitud + Longitud (redondeado a 3 decimales)

    Agrega las columnas `extra_cols` de df_src al df_base.
    Imprime cuántos registros matchearon en cada estrategia.
    """
    for col in extra_cols:
        df_base[col] = pd.NA

    # Índice del src para búsqueda eficiente
    src = df_src.copy()
    src[src_cod] = src[src_cod].map(norm_str)
    src["_addr_key"] = make_addr_key(src, src_com, src_num)
    src["_coord_key"] = make_coord_key(src, src_lat, src_lon)

    # Índices: código → fila src
    idx_cod   = src.set_index(src_cod)[extra_cols]
    idx_addr  = src.drop_duplicates("_addr_key").set_index("_addr_key")[extra_cols]
    idx_coord = src[src["_coord_key"] != ""].drop_duplicates("_coord_key").set_index("_coord_key")[extra_cols]

    df_base[base_cod] = df_base[base_cod].map(norm_str)
    df_base["_addr_key"]  = make_addr_key(df_base, base_com, base_num)
    df_base["_coord_key"] = make_coord_key(df_base, base_lat, base_lon)

    stats = {"codigo": 0, "direccion": 0, "coordenadas": 0, "sin_match": 0}

    for i, row in df_base.iterrows():
        # 1. Por código
        cod_val = row[base_cod]
        if cod_val and cod_val in idx_cod.index:
            for col in extra_cols:
                df_base.at[i, col] = idx_cod.at[cod_val, col]
            stats["codigo"] += 1
            continue

        # 2. Por dirección: ComunaCodigo + Numero
        addr_val = row["_addr_key"]
        if addr_val and addr_val != "_" and addr_val in idx_addr.index:
            for col in extra_cols:
                df_base.at[i, col] = idx_addr.at[addr_val, col]
            stats["direccion"] += 1
            continue

        # 3. Por coordenadas
        coord_val = row["_coord_key"]
        if coord_val and coord_val in idx_coord.index:
            for col in extra_cols:
                df_base.at[i, col] = idx_coord.at[coord_val, col]
            stats["coordenadas"] += 1
            continue

        stats["sin_match"] += 1

    total = len(df_base)
    print(f"[{label}] matches — codigo: {stats['codigo']} | "
          f"direccion: {stats['direccion']} | "
          f"coordenadas: {stats['coordenadas']} | "
          f"sin_match: {stats['sin_match']} / {total} total")

    df_base.drop(columns=["_addr_key", "_coord_key"], inplace=True)
    return df_base


# ---------------------------------------------------------------------------
# Carga de fuentes
# ---------------------------------------------------------------------------

def load_base():
    """establecimientos_20260526.csv — fuente principal (más reciente)."""
    path = os.path.join(BASE_DIR, "establecimientos_20260526.csv")
    df = pd.read_csv(path, sep=";", encoding="utf-8", dtype=str)
    df = df[
        (df["RegionCodigo"].str.strip() == "05") &
        (df["EstadoFuncionamiento"].str.contains("Vigente", case=False, na=False))
    ].copy().reset_index(drop=True)
    print(f"[base] {len(df)} registros vigentes Valparaiso | {len(df.columns)} columnas")
    return df


def load_old_csv():
    """Establecimientos_de_Salud_de_Chile.csv — ya filtrado a Valparaíso."""
    path = os.path.join(BASE_DIR, "Establecimientos_de_Salud_de_Chile.csv")
    df = pd.read_csv(path, encoding="utf-8", dtype=str)
    df = df[df["ESTADO"].str.contains("Vigente", case=False, na=False)].copy()
    extra = [c for c in ["F_REAPER", "F_CAMBIO", "TIPO_CAMB", "COORD_X", "COORD_Y"] if c in df.columns]
    print(f"[csv_old] {len(df)} registros | cols extra: {extra}")
    return df, extra


def load_excel():
    """Base_Establecimientos_ChileDEIS_MINSAL(23-01-2019).xlsx — Alias, Observación, Tipo Estrategia."""
    path = os.path.join(BASE_DIR, "Base_Establecimientos_ChileDEIS_MINSAL(23-01-2019).xlsx")
    df = pd.read_excel(path, dtype=str)

    # Mapear columnas por posición (estructura fija del archivo MINSAL)
    col_names = list(df.columns)
    # col 0: Código Antiguo, 1: Código nuevo, 4: Código Región, 14: Alias,
    # 15: Código Comuna, 18: Número, 25: Clasificación SAPU, 26: Fecha Cambio,
    # 27: Observación, 28: LONGITUD, 29: LATITUD
    # Usamos posiciones para evitar problemas de encoding en nombres de columna
    pos = {
        "cod_nuevo": 1,
        "cod_region": 4,
        "alias": 14,
        "cod_comuna": 15,
        "numero": 18,
        "tipo_estrategia": 9,
        "observacion": 27,
        "longitud": 28,
        "latitud": 29,
    }
    # Verificar que el archivo tiene suficientes columnas
    max_pos = max(pos.values())
    if len(col_names) <= max_pos:
        print(f"[excel] Estructura inesperada ({len(col_names)} cols), se esperaban >={max_pos+1}")
        return None, []

    rename = {col_names[v]: k for k, v in pos.items()}
    df = df.rename(columns=rename)

    # Filtrar Valparaíso (código región = 5)
    df = df[df["cod_region"].astype(str).str.strip() == "5"].copy()

    extra = ["alias", "tipo_estrategia", "observacion"]
    extra = [c for c in extra if c in df.columns]
    print(f"[excel] {len(df)} registros Valparaiso | cols extra: {extra}")
    return df, extra


def load_pdf():
    """Listado-Establecimientos-DEIS.pdf — NombreComun."""
    path = os.path.join(BASE_DIR, "Listado-Establecimientos-DEIS.pdf")
    frames = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table or len(table) < 2:
                continue
            headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(table[0])]
            rows = table[1:]
            frames.append(pd.DataFrame(rows, columns=headers))

    if not frames:
        print("[pdf] Sin tablas extraibles")
        return None, []

    df = pd.concat(frames, ignore_index=True).astype(str)

    # Identificar columnas por nombre parcial
    cod_col    = next((c for c in df.columns if "Cod" in c or "digo" in c), None)
    nombre_col = next((c for c in df.columns if "Comun" in c or "Alias" in c or "Com" in c and "Nombre" in c), None)
    lat_col    = next((c for c in df.columns if "atitud" in c or "lat" in c.lower()), None)
    lon_col    = next((c for c in df.columns if "ongitud" in c or "lon" in c.lower()), None)
    com_col    = next((c for c in df.columns if "omuna" in c and "digo" in c), None)
    num_col    = next((c for c in df.columns if "mero" in c or "Num" in c), None)

    print(f"[pdf] columnas PDF: {list(df.columns)}")

    rename = {}
    if cod_col:    rename[cod_col]    = "cod_nuevo"
    if nombre_col: rename[nombre_col] = "nombre_comun"
    if lat_col:    rename[lat_col]    = "latitud"
    if lon_col:    rename[lon_col]    = "longitud"
    if com_col:    rename[com_col]    = "cod_comuna"
    if num_col:    rename[num_col]    = "numero"

    df = df.rename(columns=rename)

    if "nombre_comun" not in df.columns:
        print("[pdf] No se encontro columna de nombre comun")
        return None, []

    extra = ["nombre_comun"]
    print(f"[pdf] {len(df)} registros | cols extra: {extra}")
    return df, extra


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    df = load_base()

    # --- Merge con CSV antiguo ---
    df_old, extra_old = load_old_csv()
    if extra_old:
        df = cascade_merge(
            df, df_old, extra_old, "csv_old",
            base_cod="EstablecimientoCodigo", src_cod="C_VIG",
            base_com="ComunaCodigo",          src_com="C_COM",
            base_num="Numero",                src_num="NUMERO",
            base_lat="Latitud",               src_lat="LATITUD",
            base_lon="Longitud",              src_lon="LONGITUD",
        )

    # --- Merge con Excel 2019 ---
    df_xl, extra_xl = load_excel()
    if df_xl is not None and extra_xl:
        df = cascade_merge(
            df, df_xl, extra_xl, "excel",
            base_cod="EstablecimientoCodigo", src_cod="cod_nuevo",
            base_com="ComunaCodigo",          src_com="cod_comuna",
            base_num="Numero",                src_num="numero",
            base_lat="Latitud",               src_lat="latitud",
            base_lon="Longitud",              src_lon="longitud",
        )

    # --- Merge con PDF ---
    df_pdf, extra_pdf = load_pdf()
    if df_pdf is not None and extra_pdf:
        pdf_has_addr  = "cod_comuna" in df_pdf.columns and "numero" in df_pdf.columns
        pdf_has_coord = "latitud" in df_pdf.columns and "longitud" in df_pdf.columns
        df = cascade_merge(
            df, df_pdf, extra_pdf, "pdf",
            base_cod="EstablecimientoCodigo", src_cod="cod_nuevo",
            base_com="ComunaCodigo",          src_com="cod_comuna" if pdf_has_addr else "cod_nuevo",
            base_num="Numero",                src_num="numero"     if pdf_has_addr else "cod_nuevo",
            base_lat="Latitud",               src_lat="latitud"    if pdf_has_coord else "cod_nuevo",
            base_lon="Longitud",              src_lon="longitud"   if pdf_has_coord else "cod_nuevo",
        )

    out = os.path.join(BASE_DIR, "establecimientos_valparaiso_vigentes.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\nArchivo guardado: {out}")
    print(f"  Registros: {len(df)}")
    print(f"  Columnas ({len(df.columns)}): {list(df.columns)}")


if __name__ == "__main__":
    main()
