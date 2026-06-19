"""
run_experiments.py
==================
Corre las 9 combinaciones T_max∈{30,45,60} × {H100,H125,H150} y guarda
los resultados en:

  resultados Gurobi V{x.y.z}/
    T{t}_{h}/
      instancia/   <- CSVs generados por construir_instancia.py
      resultados/  <- CSVs + resumen.txt generados por main.py

Uso: python run_experiments.py [label]
  label  texto opcional que se agrega al nombre de la carpeta (ej. Flo-aq)
"""
import importlib.util, os, shutil, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import gurobipy

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "Datos"))
sys.path.insert(0, BASE)

# Carpeta raíz según versión de Gurobi y label opcional
_v      = gurobipy.gurobi.version()
_label  = sys.argv[1] if len(sys.argv) > 1 else ""
_suffix = f" {_label}" if _label else ""
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

T_CONFIGS = [30, 45, 60]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def copy_dir_files(src_dir, dst_dir):
    """Copia solo los archivos (no subdirectorios) de src_dir a dst_dir."""
    os.makedirs(dst_dir, exist_ok=True)
    for fn in os.listdir(src_dir):
        src = os.path.join(src_dir, fn)
        if os.path.isfile(src):
            shutil.copy(src, dst_dir)


for t_max in T_CONFIGS:
    for h_label, h_cfg in H_CONFIGS.items():
        run_name = f"T{t_max}_{h_label}"
        exp_dir  = os.path.join(OUTPUT_ROOT, run_name)
        inst_dir = os.path.join(exp_dir, "instancia")
        res_dir  = os.path.join(exp_dir, "resultados")

        print(f"\n{'='*60}")
        print(f"  RUN: {run_name}  (T_max={t_max}, {h_label})")
        print(f"{'='*60}")

        # 1. Patch escenario y construir instancia
        ci = load_module(CI_PATH, f"ci_{run_name}")
        ci._ESCENARIOS[2]["H_t"]    = h_cfg["H_t"]
        ci._ESCENARIOS[2]["MaxC_t"] = h_cfg["MaxC_t"]
        ci.main(comunas_ids=COMUNAS, n_colegios=2, holgura=0.0, escenario=2, t_max=t_max)

        # 2. Guardar instancia
        copy_dir_files(DATA_DIR, inst_dir)
        print(f"  -> Instancia guardada en {inst_dir}")

        # 3. Correr modelo
        m_mod = load_module(MAIN_PATH, f"main_{run_name}")
        m_mod.main()

        # 4. Guardar resultados
        copy_dir_files(RES_DIR, res_dir)
        print(f"  -> Resultados guardados en {res_dir}")

print("\nTodos los experimentos completados.")
