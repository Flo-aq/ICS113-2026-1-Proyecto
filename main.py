import csv
import os
import sys
from collections import defaultdict

import gurobipy as gp
from gurobipy import GRB

BASE        = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE, "Datos", "data")
OUTPUT_DIR  = os.path.join(BASE, "resultados")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def leer_csv(path: str) -> list:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cargar_datos(data_dir: str) -> dict:
    """Lee todos los CSVs del modelo y retorna un diccionario de datos."""
    d = {}

    # Conjuntos
    comunas    = leer_csv(os.path.join(data_dir, "nodos_comunas.csv"))
    centros    = leer_csv(os.path.join(data_dir, "nodos_centros.csv"))
    hospitales = leer_csv(os.path.join(data_dir, "nodos_hospitales.csv"))
    params     = {r["parametro"]: r["valor"] for r in leer_csv(os.path.join(data_dir, "parametros.csv"))}

    I = [int(c["id"]) for c in comunas]           # zonas de demanda
    J = [int(c["id"]) for c in centros]           # centros de triaje candidatos
    T = list(range(1, 8))                         # dias (1..7)
    G = ["leve", "moderado", "grave"]             # tipos de gravedad
    K = [int(c["k"]) for c in hospitales]         # hospitales

    d["I"] = I
    d["J"] = J
    d["T"] = T
    d["G"] = G
    d["K"] = K

    # Parametros escalares
    d["T_max"]  = int(params["T_max"])
    d["L"]      = int(params["L"])
    d["Pres"]   = float(params["Pres"])
    d["ratio"]  = {"leve": float(params["ratio_leve"]),
                   "moderado": float(params["ratio_moderado"])}
    d["P_g"]    = {"leve": float(params["P_leve"]),
                   "moderado": float(params["P_moderado"])}
    d["c_dist"] = float(params["c_dist"])   # penalizacion distancia graves a hospital (por min)
    d["c_pma"]  = float(params["c_pma"])    # penalizacion por atender grave en PMA

    # Capacidades
    d["cap_j"]  = {int(c["id"]): int(c["cap_j"]) for c in centros}
    d["f_j"]    = {int(c["id"]): float(c["f_j"]) for c in centros}
    d["o_j"]    = {int(c["id"]): float(c["o_j"]) for c in centros}
    d["req_j"]  = {int(c["id"]): int(c["req_j"]) for c in centros}

    # Equipos disponibles por dia
    personal = leer_csv(os.path.join(data_dir, "personal_dia.csv"))
    d["H_t"]   = {int(r["t"]): int(r["H_t"]) for r in personal}

    # Maximo de centros activos por dia
    maxc = leer_csv(os.path.join(data_dir, "max_centros_dia.csv"))
    d["MaxC_t"] = {int(r["t"]): int(r["MaxC_t"]) for r in maxc}

    # Cobertura A_ij derivada de T_ij_viaje y T_max (hace explicito el parametro de tiempo)
    tiempos_ij = leer_csv(os.path.join(data_dir, "tiempos_ij.csv"))
    d["T_ij_viaje"] = {(int(r["i"]), int(r["j"])): int(r["minutos"]) for r in tiempos_ij}
    d["A_ij"] = {(i, j): 1 if t <= d["T_max"] else 0
                 for (i, j), t in d["T_ij_viaje"].items()}

    # Tiempos hospitales (T_ik_viaje usado en FO para penalizacion de distancia graves)
    tiempos_ik = leer_csv(os.path.join(data_dir, "tiempos_ik.csv"))
    d["T_ik_viaje"] = {(int(r["i"]), int(r["k"])): int(r["minutos"]) for r in tiempos_ik}

    # Demanda D_itg
    dem = leer_csv(os.path.join(data_dir, "demanda.csv"))
    d["D_itg"] = {(int(r["i"]), int(r["t"]), r["g"]): int(r["D_i_t_g"]) for r in dem}

    # Demanda maxima D_ig_max (para restriccion de asignacion maxima)
    dmax = leer_csv(os.path.join(data_dir, "demanda_max.csv"))
    d["D_ig_max"] = {(int(r["i"]), r["g"]): int(r["D_i_g_max"]) for r in dmax}

    # Capacidad de hospitales {(k, t): capacidad}
    d["cap_k_t"] = {(int(r["k"]), t): int(r[f"Cap_{t}"]) for r in hospitales for t in T}

    return d


def construir_modelo(d: dict, escenario_base=False) -> tuple:
    """
    Construye y retorna el modelo Gurobi junto con las variables de decision.

    Variables
    ---------
    z[j,t]        : binaria   -- centro j activo en dia t
    v[j,t]        : binaria   -- centro j abre en dia t
    c[j,t]        : binaria   -- centro j cierra en dia t
    p[j,t]        : entera    -- equipos medicos asignados al centro j en dia t
    a[i,j,t,g]    : continua  -- pacientes tipo g de zona i atendidos en centro j dia t
    w[i,k,t,grave]: continua  -- pacientes graves de zona i atendidos en hospital k dia t
    s[i,t,g]      : continua  -- pacientes tipo g de zona i en espera al final del dia t
                                 (s[i,t,grave] = 0 siempre; graves siempre cubiertos)
    """
    I, J, T, G, K = d["I"], d["J"], d["T"], d["G"], d["K"]

    m = gp.Model("PMA_Valparaiso")
    m.setParam("OutputFlag", 1)
    m.setParam("TimeLimit", 1800)  # 30 minutos (requisito de entrega)

    vars_ = {}

    # Variables binarias de activacion
    z = m.addVars(J, T, vtype=GRB.BINARY, name="z")   # activo
    if escenario_base:
        for j in J:
            for t in T:
                z[j, t].ub = 0
    v = m.addVars(J, T, vtype=GRB.BINARY, name="v")   # abre
    c = m.addVars(J, T, vtype=GRB.BINARY, name="c")   # cierra

    # Personal asignado (entero no negativo)
    p = m.addVars(J, T, vtype=GRB.INTEGER, lb=0, name="p")

    # Asignacion de pacientes a centros de triaje (todas las gravedades, incluye grave como overflow)
    a = m.addVars(I, J, T, G, vtype=GRB.CONTINUOUS, lb=0, name="a")

    # Asignacion de graves a hospitales (solo categoria "grave")
    w = {}
    if K:
        w = m.addVars(I, K, T, ["grave"], vtype=GRB.CONTINUOUS, lb=0, name="w")

    # Stock de espera al final del dia (s[i,t,"grave"] = 0 forzado por restriccion 11)
    s = m.addVars(I, T, G, vtype=GRB.CONTINUOUS, lb=0, name="s")

    vars_.update({"z": z, "v": v, "c": c, "p": p, "a": a, "w": w, "s": s})

    # Funcion objetivo:
    # - Minimizar espera ponderada de leves y moderados
    # - Penalizar distancia de viaje de graves a hospitales (c_dist * T_ik_viaje)
    # - Penalizar atencion de graves en PMAs (c_pma por paciente)
    m.setObjective(
        gp.quicksum(
            s[i, t, g] * d["P_g"][g]
            for i in I for t in T for g in ["leve", "moderado"]
        )
        + gp.quicksum(
            d["c_dist"] * d["T_ik_viaje"].get((i, k), 9999) * w[i, k, t, "grave"]
            for i in I for k in K for t in T
        )
        + gp.quicksum(
            d["c_pma"] * a[i, j, t, "grave"]
            for i in I for j in J for t in T
        ),
        GRB.MINIMIZE
    )


    # RESTRICCIONES


    # 1. Balance de inventario de heridos (leve y moderado — sin termino w)
    for i in I:
        for g in ["leve", "moderado"]:
            m.addConstr(
                s[i, 1, g] == d["D_itg"].get((i, 1, g), 0)
                             - gp.quicksum(a[i, j, 1, g] for j in J),
                name=f"balance_t1_i{i}_g{g}"
            )
            for t in T[1:]:
                m.addConstr(
                    s[i, t, g] == s[i, t-1, g] + d["D_itg"].get((i, t, g), 0)
                                 - gp.quicksum(a[i, j, t, g] for j in J),
                    name=f"balance_t{t}_i{i}_g{g}"
                )

    # 2. Balance de graves (con termino w; s[i,t,"grave"] forzado a 0 en restriccion 11)
    for i in I:
        for t in T:
            m.addConstr(
                s[i, t, "grave"] == d["D_itg"].get((i, t, "grave"), 0)
                                  - gp.quicksum(a[i, j, t, "grave"] for j in J)
                                  - gp.quicksum(w.get((i, k, t, "grave"), 0) for k in K),
                name=f"balance_grave_t{t}_i{i}"
            )

    # 3. Capacidad de atencion de centros de triaje
    for j in J:
        for t in T:
            m.addConstr(
                gp.quicksum(a[i, j, t, g] for i in I for g in G) <= d["cap_j"][j] * z[j, t],
                name=f"cap_centro_j{j}_t{t}"
            )

    # 4. Capacidad por equipos equivalentes (ratio_g pacientes por equipo por dia)
    for j in J:
        for t in T:
            m.addConstr(
                gp.quicksum(a[i, j, t, g] / d["ratio"][g] for i in I for g in ["leve", "moderado"]) <= p[j, t],
                name=f"cap_equipos_j{j}_t{t}"
            )

    # 5. Capacidad de atencion de hospitales (solo graves)
    for k in K:
        for t in T:
            cap_kt = d["cap_k_t"].get((k, t), 0)
            m.addConstr(
                gp.quicksum(w.get((i, k, t, "grave"), 0) for i in I) <= cap_kt,
                name=f"cap_hospital_k{k}_t{t}"
            )

    # 6. Disponibilidad de equipos medicos totales
    for t in T:
        m.addConstr(
            gp.quicksum(p[j, t] for j in J) <= d["H_t"][t],
            name=f"disp_equipos_t{t}"
        )

    # 7. Activacion y permanencia minima
    #    7a. z_{j,1} = v_{j,1}
    for j in J:
        m.addConstr(z[j, 1] == v[j, 1], name=f"act_init_j{j}")

    #    7b. c_{j,1} = 0
    for j in J:
        m.addConstr(c[j, 1] == 0, name=f"cierre_init_j{j}")

    #    7c. v_{j,t} - c_{j,t} = z_{j,t} - z_{j,t-1}  para t >= 2
    for j in J:
        for t in T[1:]:
            m.addConstr(v[j, t] - c[j, t] == z[j, t] - z[j, t-1],
                        name=f"flujo_vc_j{j}_t{t}")

    #    7d. v_{j,t} + c_{j,t} <= 1
    for j in J:
        for t in T:
            m.addConstr(v[j, t] + c[j, t] <= 1, name=f"vc_excl_j{j}_t{t}")

    #    7e. Permanencia minima L dias
    L = d["L"]
    T_max_idx = max(T)
    for j in J:
        for t in T:
            tau_end = min(t + L - 1, T_max_idx)
            m.addConstr(
                gp.quicksum(z[j, tau] for tau in range(t, tau_end + 1)) >= L * v[j, t],
                name=f"perm_min_j{j}_t{t}"
            )

    # 8. Cotas de equipos asignados: req_j[j]*z[j,t] <= p[j,t] <= H_t[t]*z[j,t]
    for j in J:
        for t in T:
            m.addConstr(p[j, t] >= d["req_j"][j] * z[j, t], name=f"p_lb_j{j}_t{t}")
            m.addConstr(p[j, t] <= d["H_t"][t]   * z[j, t], name=f"p_ub_j{j}_t{t}")

    # 9. Seguridad sismica: cobertura geografica de PMAs (a_{i,j,t,g} <= A_ij * D_ig_max)
    for i in I:
        for j in J:
            for t in T:
                for g in G:
                    A     = d["A_ij"].get((i, j), 0)
                    D_max = d["D_ig_max"].get((i, g), 0)
                    m.addConstr(
                        a[i, j, t, g] <= A * D_max,
                        name=f"cob_a_i{i}_j{j}_t{t}_g{g}"
                    )

    # 10. Restriccion de presupuesto
    m.addConstr(
        gp.quicksum(d["f_j"][j] * v[j, t] for j in J for t in T)
        + gp.quicksum(d["o_j"][j] * z[j, t] for j in J for t in T)
        <= d["Pres"],
        name="presupuesto"
    )

    # 11. Capacidad de gestion y supervision regional
    for t in T:
        m.addConstr(
            gp.quicksum(z[j, t] for j in J) <= d["MaxC_t"][t],
            name=f"max_centros_t{t}"
        )

    # 12. Graves siempre cubiertos: s[i,t,"grave"] = 0
    #     (combinado con restriccion 2 fuerza: D[i,t,grave] = sum_j a + sum_k w)
    for i in I:
        for t in T:
            m.addConstr(s[i, t, "grave"] == 0, name=f"grave_cubierto_i{i}_t{t}")

    m.update()

    return m, vars_


def escribir_resultados(m: gp.Model, vars_: dict, d: dict, output_dir: str) -> None:
    """Escribe los resultados de la solucion en CSVs y un resumen en texto."""

    if m.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT) or m.SolCount == 0:
        print(f"\n[!] No se encontro solucion factible. Status: {m.Status}")
        return

    z, v, c, p, a, s, w = (vars_["z"], vars_["v"], vars_["c"], vars_["p"],
                             vars_["a"], vars_["s"], vars_["w"])
    I, J, T, G, K = d["I"], d["J"], d["T"], d["G"], d["K"]

    def wr(filename, header, rows):
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8", newline="") as f:
            wt = csv.writer(f)
            wt.writerow(header)
            wt.writerows(rows)
        print(f"  -> {path}")

    # Activacion de centros z[j,t]
    wr("resultado_activacion.csv",
       ["j", "t", "z_jt", "v_jt", "c_jt", "p_jt"],
       [(j, t, round(z[j,t].X), round(v[j,t].X), round(c[j,t].X), round(p[j,t].X))
        for j in J for t in T])

    # Asignacion de pacientes a centros a[i,j,t,g]
    wr("resultado_asignacion_centros.csv",
       ["i", "j", "t", "g", "a_ijtg"],
       [(i, j, t, g, round(a[i,j,t,g].X, 2))
        for i in I for j in J for t in T for g in G
        if a[i,j,t,g].X > 0.01])

    # Asignacion de graves a hospitales w[i,k,t,"grave"]
    if w:
        wr("resultado_asignacion_hospitales.csv",
           ["i", "k", "t", "w_iktgrave"],
           [(i, k, t, round(w[i,k,t,"grave"].X, 2))
            for i in I for k in K for t in T
            if w[i,k,t,"grave"].X > 0.01])

    # Stock de espera s[i,t,g]
    wr("resultado_stock_espera.csv",
       ["i", "t", "g", "s_itg"],
       [(i, t, g, round(s[i,t,g].X, 2))
        for i in I for t in T for g in G])

    # Resumen por dia
    resumen_rows = []
    for t in T:
        centros_activos  = [j for j in J if z[j,t].X > 0.5]
        equipos_total    = sum(round(p[j,t].X) for j in J)
        pacientes_atend  = sum(a[i,j,t,g].X for i in I for j in J for g in G)
        en_espera_leve   = sum(s[i,t,"leve"].X for i in I)
        en_espera_mod    = sum(s[i,t,"moderado"].X for i in I)
        graves_hospital  = sum(w[i,k,t,"grave"].X for i in I for k in K) if w else 0
        graves_pma       = sum(a[i,j,t,"grave"].X for i in I for j in J)
        resumen_rows.append((t, len(centros_activos), equipos_total,
                             round(pacientes_atend), round(en_espera_leve),
                             round(en_espera_mod), round(graves_hospital),
                             round(graves_pma)))

    wr("resultado_resumen_dia.csv",
       ["t", "centros_activos", "equipos_totales", "pacientes_atendidos",
        "espera_leve", "espera_moderado", "graves_hospital", "graves_pma"],
       resumen_rows)

    # Resumen en texto
    gap_str = f"{m.MIPGap*100:.2f}%" if m.SolCount > 0 else "N/A"
    summary_path = os.path.join(output_dir, "resumen.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("RESULTADOS - Modelo PMA Valparaiso\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Estado del solver : {m.Status} ({'Optimo' if m.Status == GRB.OPTIMAL else 'Limite de tiempo'})\n")
        f.write(f"Funcion objetivo  : {m.ObjVal:.2f}\n")
        f.write(f"MIP Gap           : {gap_str}\n")
        f.write(f"Tiempo de computo : {m.Runtime:.1f} s\n\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'Dia':>4} {'Centros':>8} {'Equipos':>8} {'Atend.':>8} "
                f"{'Esp.L':>7} {'Esp.M':>7} {'GravHosp':>9} {'GravPMA':>8}\n")
        f.write("-" * 70 + "\n")
        for row in resumen_rows:
            f.write(f"{row[0]:>4} {row[1]:>8} {row[2]:>8} {row[3]:>8} "
                    f"{row[4]:>7.0f} {row[5]:>7.0f} {row[6]:>9.0f} {row[7]:>8.0f}\n")
        f.write("-" * 70 + "\n\n")

        centros_csv = leer_csv(os.path.join(DATA_DIR, "nodos_centros.csv"))
        nombre_j = {int(r["id"]): r["nombre"] for r in centros_csv}
        f.write("Centros activos por dia:\n")
        for t in T:
            activos = [j for j in J if z[j,t].X > 0.5]
            nombres = ", ".join(f"j{j}={nombre_j.get(j,'?')}" for j in activos) or "(ninguno)"
            f.write(f"  Dia {t}: {nombres}\n")

    print(f"  -> {summary_path}")
    print(f"\n{'='*70}")
    print(f"  FO = {m.ObjVal:.2f}  |  Gap = {gap_str}  |  {m.Runtime:.1f}s")
    print(f"{'='*70}\n")

    print("\nResumen por dia:")
    print(f"{'Dia':>4} {'Centros':>8} {'Equipos':>8} {'Atend.':>8} "
          f"{'Esp.L':>7} {'Esp.M':>7} {'GravH':>7} {'GravP':>7}")
    print("-" * 70)
    for row in resumen_rows:
        print(f"{row[0]:>4} {row[1]:>8} {row[2]:>8} {row[3]:>8} "
              f"{row[4]:>7.0f} {row[5]:>7.0f} {row[6]:>7.0f} {row[7]:>7.0f}")


def main():
    print("-- Cargando datos desde", DATA_DIR)
    d = cargar_datos(DATA_DIR)
    print(f"   |I|={len(d['I'])} comunas, |J|={len(d['J'])} centros, "
          f"|T|={len(d['T'])} dias, |G|={len(d['G'])} gravedades, |K|={len(d['K'])} hospitales")
    print(f"   Presupuesto: CLP {d['Pres']:,.0f}")

    print("\n-- Construyendo modelo Gurobi...")
    m, vars_ = construir_modelo(d, escenario_base=False)

    nvars  = m.NumVars
    nconst = m.NumConstrs
    print(f"   Variables    : {nvars:,}")
    print(f"   Restricciones: {nconst:,}")

    print("\n-- Optimizando...")
    m.optimize()

    print("\n-- Escribiendo resultados en", OUTPUT_DIR)
    escribir_resultados(m, vars_, d, OUTPUT_DIR)

    return m, vars_, d


if __name__ == "__main__":
    main()
