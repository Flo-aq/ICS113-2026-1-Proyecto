"""
modelo_gurobi.py
================
Modelo de Programación Lineal Entera Mixta (MILP) para la localización y
operación de Centros de Triaje (PMAs) post-terremoto en la Región de Valparaíso.

Referencia: Informe 2 — Grupo 10, ICS1113-Optimización, PUC Chile.

Uso:
    python modelo_gurobi.py

El script lee los CSVs generados por construir_instancia.py desde Datos/data/
y escribe los resultados en resultados/.

Requiere:
    pip install gurobipy
"""

import csv
import os
import sys
from collections import defaultdict

import gurobipy as gp
from gurobipy import GRB

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BASE        = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE, "Datos", "data")
OUTPUT_DIR  = os.path.join(BASE, "resultados")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------

def leer_csv(path: str) -> list:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cargar_datos(data_dir: str) -> dict:
    """Lee todos los CSVs del modelo y retorna un diccionario de datos."""
    d = {}

    # ── Conjuntos ──────────────────────────────────────────────────────────
    comunas = leer_csv(os.path.join(data_dir, "nodos_comunas.csv"))
    centros = leer_csv(os.path.join(data_dir, "nodos_centros.csv"))
    hospitales = leer_csv(os.path.join(data_dir, "nodos_hospitales.csv"))
    params  = {r["parametro"]: r["valor"] for r in leer_csv(os.path.join(data_dir, "parametros.csv"))}

    I = [int(c["id"]) for c in comunas]           # zonas de demanda
    J = [int(c["id"]) for c in centros]           # centros de triaje candidatos
    T = list(range(1, 8))                          # días (1..7)
    G = ["leve", "moderado"]                      # tipos de gravedad
    K = [int(c["k"]) for c in hospitales]         # hospitales

    d["I"] = I
    d["J"] = J
    d["T"] = T
    d["G"] = G
    d["K"] = K

    # ── Parámetros escalares ───────────────────────────────────────────────
    d["T_max"]  = int(params["T_max"])
    d["L"]      = int(params["L"])
    d["Pres"]   = float(params["Pres"])
    d["ratio"]  = {"leve": float(params["ratio_leve"]),
                   "moderado": float(params["ratio_moderado"])}
    d["P_g"]    = {"leve": float(params["P_leve"]),
                   "moderado": float(params["P_moderado"])}

    # ── Capacidad de centros ───────────────────────────────────────────────
    d["cap_j"]  = {int(c["id"]): int(c["cap_j"]) for c in centros}
    d["f_j"]    = {int(c["id"]): float(c["f_j"]) for c in centros}
    d["o_j"]    = {int(c["id"]): float(c["o_j"]) for c in centros}
    d["req_j"]  = {int(c["id"]): int(c["req_j"]) for c in centros}

    # ── Equipos disponibles por día ────────────────────────────────────────
    personal = leer_csv(os.path.join(data_dir, "personal_dia.csv"))
    d["H_t"]   = {int(r["t"]): int(r["H_t"]) for r in personal}

    # ── Máximo de centros activos por día ─────────────────────────────────
    maxc = leer_csv(os.path.join(data_dir, "max_centros_dia.csv"))
    d["MaxC_t"] = {int(r["t"]): int(r["MaxC_t"]) for r in maxc}

    # ── Cobertura A_ij ─────────────────────────────────────────────────────
    cob = leer_csv(os.path.join(data_dir, "cobertura_ij.csv"))
    d["A_ij"]  = {(int(r["i"]), int(r["j"])): int(r["A_ij"]) for r in cob}

    # ── Cobertura A_ik ─────────────────────────────────────────────────────
    cob_h = leer_csv(os.path.join(data_dir, "cobertura_ik.csv"))
    d["A_ik"] = {(int(r["i"]), int(r["k"])): int(r["A_ik"]) for r in cob_h}

    # ── Demanda D_itg ──────────────────────────────────────────────────────
    dem = leer_csv(os.path.join(data_dir, "demanda.csv"))
    d["D_itg"] = {(int(r["i"]), int(r["t"]), r["g"]): int(r["D_i_t_g"]) for r in dem}

    # ── Demanda máxima D_ig_max (para restricción de asignación máxima) ────
    dmax = leer_csv(os.path.join(data_dir, "demanda_max.csv"))
    d["D_ig_max"] = {(int(r["i"]), r["g"]): int(r["D_i_g_max"]) for r in dmax}

    # ── Capacidad de hospitales (vacía — sin datos) ────────────────────────
    d["cap_k_t"] = {(int(r["k"]), t): int(r[f"Cap_{t}"]) for r in hospitales for t in T}   # {(k, t): capacidad}

    return d


# ---------------------------------------------------------------------------
# Construcción del modelo
# ---------------------------------------------------------------------------

def construir_modelo(d: dict) -> tuple:
    """
    Construye y retorna el modelo Gurobi junto con las variables de decisión.

    Variables
    ---------
    z[j,t]      : binaria — centro j activo en día t
    v[j,t]      : binaria — centro j abre en día t
    c[j,t]      : binaria — centro j cierra en día t
    p[j,t]      : entera  — equipos médicos asignados al centro j en día t
    a[i,j,t,g]  : continua — pacientes tipo g de zona i atendidos en centro j día t
    w[i,k,t,g]  : continua — pacientes tipo g de zona i atendidos en hospital k día t
    s[i,t,g]    : continua — pacientes tipo g de zona i en espera al final del día t
    """
    I, J, T, G, K = d["I"], d["J"], d["T"], d["G"], d["K"]

    m = gp.Model("PMA_Valparaiso")
    m.setParam("OutputFlag", 1)
    m.setParam("TimeLimit", 300)   # 5 min máximo (ajustar según hardware)

    vars_ = {}

    # ── Variables binarias de activación ──────────────────────────────────
    z = m.addVars(J, T, vtype=GRB.BINARY, name="z")   # activo
    v = m.addVars(J, T, vtype=GRB.BINARY, name="v")   # abre
    c = m.addVars(J, T, vtype=GRB.BINARY, name="c")   # cierra

    # ── Personal asignado (entero no negativo) ────────────────────────────
    p = m.addVars(J, T, vtype=GRB.INTEGER, lb=0, name="p")

    # ── Asignación de pacientes a centros de triaje ───────────────────────
    a = m.addVars(I, J, T, G, vtype=GRB.CONTINUOUS, lb=0, name="a")

    # ── Asignación de pacientes a hospitales (vacía si K = {}) ───────────
    w = {}
    if K:
        w = m.addVars(I, K, T, G, vtype=GRB.CONTINUOUS, lb=0, name="w")

    # ── Stock de espera al final del día ──────────────────────────────────
    # Incluye t=0 (condición inicial) como parámetro fijo = 0
    s = m.addVars(I, T, G, vtype=GRB.CONTINUOUS, lb=0, name="s")

    vars_.update({"z": z, "v": v, "c": c, "p": p, "a": a, "w": w, "s": s})

    # ── Función objetivo: minimizar Σ_i Σ_t Σ_g s[i,t,g] * P_g ──────────
    m.setObjective(
        gp.quicksum(
            s[i, t, g] * d["P_g"][g]
            for i in I for t in T for g in G
        ),
        GRB.MINIMIZE
    )

    # ════════════════════════════════════════════════════════════════════════
    # RESTRICCIONES
    # ════════════════════════════════════════════════════════════════════════

    # 1. Condición inicial de stock (s_{i,0,g} = 0 implícito; t=1 parte sin backlog)
    #    La restricción de balance para t=1 usa s_{i,0,g}=0 directamente.

    # 2. Balance de inventario de heridos
    for i in I:
        for g in G:
            # t = 1: s_{i,0,g} = 0
            m.addConstr(
                s[i, 1, g] == 0 + d["D_itg"].get((i, 1, g), 0)
                             - gp.quicksum(a[i, j, 1, g] for j in J)
                             - gp.quicksum(w.get((i, k, 1, g), 0) for k in K),
                name=f"balance_t1_i{i}_g{g}"
            )
            for t in T[1:]:   # t = 2..T
                m.addConstr(
                    s[i, t, g] == s[i, t-1, g] + d["D_itg"].get((i, t, g), 0)
                                 - gp.quicksum(a[i, j, t, g] for j in J)
                                 - gp.quicksum(w.get((i, k, t, g), 0) for k in K),
                    name=f"balance_t{t}_i{i}_g{g}"
                )

    # 3. Capacidad de atención de centros de triaje
    for j in J:
        for t in T:
            m.addConstr(
                gp.quicksum(a[i, j, t, g] for i in I for g in G) <= d["cap_j"][j] * z[j, t],
                name=f"cap_centro_j{j}_t{t}"
            )

    # 4. Capacidad por equipos equivalentes (ratio_g pacientes por equipo por día)
    for j in J:
        for t in T:
            m.addConstr(
                gp.quicksum(a[i, j, t, g] / d["ratio"][g] for i in I for g in G) <= p[j, t],
                name=f"cap_equipos_j{j}_t{t}"
            )

    # 5. Capacidad de atención de hospitales
    for k in K:
        for t in T:
            cap_kt = d["cap_k_t"].get((k, t), 0)
            m.addConstr(
                gp.quicksum(w[i, k, t, g] for i in I for g in G) <= cap_kt,
                name=f"cap_hospital_k{k}_t{t}"
            )

    # 6. Disponibilidad de equipos médicos totales
    for t in T:
        m.addConstr(
            gp.quicksum(p[j, t] for j in J) <= d["H_t"][t],
            name=f"disp_equipos_t{t}"
        )

    # 7. Activación y permanencia mínima
    #    7a. z_{j,1} = v_{j,1}
    for j in J:
        m.addConstr(z[j, 1] == v[j, 1], name=f"act_init_j{j}")

    #    7b. c_{j,1} = 0
    for j in J:
        m.addConstr(c[j, 1] == 0, name=f"cierre_init_j{j}")

    #    7c. v_{j,t} - c_{j,t} = z_{j,t} - z_{j,t-1}  ∀t≥2
    for j in J:
        for t in T[1:]:
            m.addConstr(v[j, t] - c[j, t] == z[j, t] - z[j, t-1],
                        name=f"flujo_vc_j{j}_t{t}")

    #    7d. v_{j,t} + c_{j,t} ≤ 1  (no puede abrir y cerrar el mismo día)
    for j in J:
        for t in T:
            m.addConstr(v[j, t] + c[j, t] <= 1, name=f"vc_excl_j{j}_t{t}")

    #    7e. Permanencia mínima L días: Σ_{τ=t}^{min(t+L-1,T)} z_{j,τ} ≥ L·v_{j,t}
    L = d["L"]
    T_max_idx = max(T)
    for j in J:
        for t in T:
            tau_end = min(t + L - 1, T_max_idx)
            m.addConstr(
                gp.quicksum(z[j, tau] for tau in range(t, tau_end + 1)) >= L * v[j, t],
                name=f"perm_min_j{j}_t{t}"
            )

    # 8. Seguridad sísmica y operatividad
    #    8a. p_{j,t} ≥ req_j · z_{j,t}  (dotación mínima si el centro está activo)
    for j in J:
        for t in T:
            m.addConstr(
                p[j, t] >= d["req_j"][j] * z[j, t],
                name=f"req_min_j{j}_t{t}"
            )

    #   8a bis. p_{j,t} ≤ H_t · z_{j,t}  (no asignar equipos si el centro está cerrado, y no exceder el total disponible)
    for j in J:
        for t in T:
            m.addConstr(
                p[j, t] <= d["H_t"][t] * z[j, t],
                name=f"eq_cerrado_j{j}_t{t}"
            )
    
    #    8b. a_{i,j,t,g} ≤ A_{ij} · D_ig_max  (solo asignar si hay cobertura)
    for i in I:
        for j in J:
            for t in T:
                for g in G:
                    A = d["A_ij"].get((i, j), 0)
                    D_max = d["D_ig_max"].get((i, g), 0)
                    m.addConstr(
                        a[i, j, t, g] <= A * D_max,
                        name=f"cob_a_i{i}_j{j}_t{t}_g{g}"
                    )

    #    8c. w_{i,k,t,g} ≤ A_{ik} · D_ig_max  (cobertura hospitales)
    for k in K:
        for i in I:
            for t in T:
                for g in G:
                    A = d["A_ik"].get((i, k), 0)
                    D_max = d["D_ig_max"].get((i, g), 0)
                    m.addConstr(
                        w[i, k, t, g] <= A * D_max,
                        name=f"cob_w_i{i}_k{k}_t{t}_g{g}"
                    )

    # 9. Restricción de presupuesto
    m.addConstr(
        gp.quicksum(d["f_j"][j] * v[j, t] for j in J for t in T)
        + gp.quicksum(d["o_j"][j] * z[j, t] for j in J for t in T)
        <= d["Pres"],
        name="presupuesto"
    )

    # 10. Capacidad de gestión y supervisión regional
    for t in T:
        m.addConstr(
            gp.quicksum(z[j, t] for j in J) <= d["MaxC_t"][t],
            name=f"max_centros_t{t}"
        )

    m.update()

    return m, vars_


# ---------------------------------------------------------------------------
# Escritura de resultados
# ---------------------------------------------------------------------------

def escribir_resultados(m: gp.Model, vars_: dict, d: dict, output_dir: str) -> None:
    """Escribe los resultados de la solución en CSVs y un resumen en texto."""

    if m.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT) or m.SolCount == 0:
        print(f"\n[!] No se encontró solución factible. Status: {m.Status}")
        return

    z, v, c, p, a, s = vars_["z"], vars_["v"], vars_["c"], vars_["p"], vars_["a"], vars_["s"]
    I, J, T, G = d["I"], d["J"], d["T"], d["G"]

    def w(filename, header, rows):
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(header)
            wr.writerows(rows)
        print(f"  → {path}")

    # Activación de centros z[j,t]
    w("resultado_activacion.csv",
      ["j", "t", "z_jt", "v_jt", "c_jt", "p_jt"],
      [(j, t,
        round(z[j, t].X),
        round(v[j, t].X),
        round(c[j, t].X),
        round(p[j, t].X))
       for j in J for t in T])

    # Asignación de pacientes a centros a[i,j,t,g]
    w("resultado_asignacion_centros.csv",
      ["i", "j", "t", "g", "a_ijtg"],
      [(i, j, t, g, round(a[i, j, t, g].X, 2))
       for i in I for j in J for t in T for g in G
       if a[i, j, t, g].X > 0.01])

    # Stock de espera s[i,t,g]
    w("resultado_stock_espera.csv",
      ["i", "t", "g", "s_itg"],
      [(i, t, g, round(s[i, t, g].X, 2))
       for i in I for t in T for g in G])

    # Resumen por día
    resumen_rows = []
    for t in T:
        centros_activos = [j for j in J if z[j, t].X > 0.5]
        equipos_total   = sum(round(p[j, t].X) for j in J)
        pacientes_atend = sum(a[i, j, t, g].X for i in I for j in J for g in G)
        en_espera_leve  = sum(s[i, t, "leve"].X for i in I)
        en_espera_mod   = sum(s[i, t, "moderado"].X for i in I)
        resumen_rows.append((t, len(centros_activos), equipos_total,
                             round(pacientes_atend), round(en_espera_leve),
                             round(en_espera_mod)))

    w("resultado_resumen_dia.csv",
      ["t", "centros_activos", "equipos_totales", "pacientes_atendidos",
       "espera_leve", "espera_moderado"],
      resumen_rows)

    # Resumen en texto
    gap_str = f"{m.MIPGap*100:.2f}%" if m.SolCount > 0 else "N/A"
    summary_path = os.path.join(output_dir, "resumen.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("RESULTADOS — Modelo PMA Valparaíso\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Estado del solver : {m.Status} ({'Óptimo' if m.Status == GRB.OPTIMAL else 'Límite de tiempo'})\n")
        f.write(f"Función objetivo  : {m.ObjVal:.2f}  (pacientes-día ponderados en espera)\n")
        f.write(f"MIP Gap           : {gap_str}\n")
        f.write(f"Tiempo de cómputo : {m.Runtime:.1f} s\n\n")
        f.write("─" * 60 + "\n")
        f.write(f"{'Día':>4} {'Centros':>8} {'Equipos':>8} {'Atendidos':>10} {'Espera L':>9} {'Espera M':>9}\n")
        f.write("─" * 60 + "\n")
        for row in resumen_rows:
            f.write(f"{row[0]:>4} {row[1]:>8} {row[2]:>8} {row[3]:>10} {row[4]:>9.0f} {row[5]:>9.0f}\n")
        f.write("─" * 60 + "\n\n")

        # Centros abiertos por día
        f.write("Centros activos por día:\n")
        # Necesitamos nombres
        centros_csv = leer_csv(os.path.join(DATA_DIR, "nodos_centros.csv"))
        nombre_j = {int(r["id"]): r["nombre"] for r in centros_csv}
        for t in T:
            activos = [j for j in J if z[j, t].X > 0.5]
            nombres = ", ".join(f"j{j}={nombre_j.get(j,'?')}" for j in activos) or "(ninguno)"
            f.write(f"  Día {t}: {nombres}\n")

    print(f"  → {summary_path}")
    print(f"\n{'='*60}")
    print(f"  FO = {m.ObjVal:.2f}  |  Gap = {gap_str}  |  {m.Runtime:.1f}s")
    print(f"{'='*60}\n")

    # Imprimir resumen en consola también
    print("\nResumen por día:")
    print(f"{'Día':>4} {'Centros':>8} {'Equipos':>8} {'Atendidos':>10} {'Espera L':>9} {'Espera M':>9}")
    print("-" * 60)
    for row in resumen_rows:
        print(f"{row[0]:>4} {row[1]:>8} {row[2]:>8} {row[3]:>10} {row[4]:>9.0f} {row[5]:>9.0f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("── Cargando datos desde", DATA_DIR)
    d = cargar_datos(DATA_DIR)
    print(f"   |I|={len(d['I'])} comunas, |J|={len(d['J'])} centros, |T|={len(d['T'])} días, |G|={len(d['G'])} gravedades")
    print(f"   Presupuesto: CLP {d['Pres']:,.0f}")

    print("\n── Construyendo modelo Gurobi...")
    m, vars_ = construir_modelo(d)

    nvars  = m.NumVars
    nconst = m.NumConstrs
    print(f"   Variables   : {nvars:,}")
    print(f"   Restricciones: {nconst:,}")

    print("\n── Optimizando...")
    m.optimize()

    print("\n── Escribiendo resultados en", OUTPUT_DIR)
    escribir_resultados(m, vars_, d, OUTPUT_DIR)

    return m, vars_, d


if __name__ == "__main__":
    main()
