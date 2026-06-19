"""
run_experiment.py
=================
Corre UN solo experimento y guarda instancia + resultados en una carpeta plana:

  resultados Gurobi V{x.y.z}/T{T_MAX}_{H_LABEL}/

Edita T_MAX, H_LABEL y LABEL abajo y ejecuta:
  python run_experiment.py
"""
import importlib.util, os, shutil, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import gurobipy

# ── Parámetros del experimento ────────────────────────────────────────────────
T_MAX   = 45       # 30, 45 o 60
H_LABEL = "H100"   # "H100", "H125" o "H150"
LABEL   = "Flo-aq" # texto libre que se agrega al nombre de la carpeta (puede ser "")
# ─────────────────────────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "Datos"))
sys.path.insert(0, BASE)

_v      = gurobipy.gurobi.version()
_suffix = f" {LABEL}" if LABEL else ""
OUTPUT_ROOT = os.path.join(BASE, f"resultados Gurobi V{_v[0]}.{_v[1]}.{_v[2]}{_suffix}")

CI_PATH   = os.path.join(BASE, "Datos", "construir_instancia.py")
MAIN_PATH = os.path.join(BASE, "main.py")
DATA_DIR  = os.path.join(BASE, "Datos", "data")
RES_DIR   = os.path.join(BASE, "resultados")

COMUNAS = [1,2,3,4,5,6,7,8,9,10,11,14,15,16,17,18,19,20,
           21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38]

H_CONFIGS = {
    "H100": dict(H_t=[19, 32, 55, 78, 93, 104, 112],  MaxC_t=[4,  8, 11, 15, 19, 19, 19]),
    "H125": dict(H_t=[24, 40, 69, 97, 116, 130, 140], MaxC_t=[5, 10, 14, 19, 24, 24, 24]),
    "H150": dict(H_t=[28, 48, 82, 117, 139, 156, 168],MaxC_t=[6, 12, 16, 22, 28, 28, 28]),
}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if H_LABEL not in H_CONFIGS:
    raise ValueError(f"H_LABEL debe ser uno de {list(H_CONFIGS.keys())}")

h_cfg    = H_CONFIGS[H_LABEL]
run_name = f"T{T_MAX}_{H_LABEL}"
out_dir  = os.path.join(OUTPUT_ROOT, run_name)

print(f"\n{'='*60}")
print(f"  RUN: {run_name}  (T_max={T_MAX}, {H_LABEL})")
print(f"{'='*60}")

# 1. Patch escenario y construir instancia
ci = load_module(CI_PATH, "ci_single")
ci._ESCENARIOS[2]["H_t"]    = h_cfg["H_t"]
ci._ESCENARIOS[2]["MaxC_t"] = h_cfg["MaxC_t"]
ci.main(comunas_ids=COMUNAS, n_colegios=2, holgura=0.0, escenario=2, t_max=T_MAX)

# 2. Correr modelo
m_mod = load_module(MAIN_PATH, "main_single")
m_mod.main()

# 3. Copiar instancia y resultados a la misma carpeta (plana)
os.makedirs(out_dir, exist_ok=True)

for fn in os.listdir(DATA_DIR):
    src = os.path.join(DATA_DIR, fn)
    if os.path.isfile(src):
        shutil.copy(src, out_dir)

for fn in os.listdir(RES_DIR):
    src = os.path.join(RES_DIR, fn)
    if os.path.isfile(src):
        shutil.copy(src, out_dir)

print(f"\n  -> Guardado en {out_dir}")
print("Experimento completado.")
