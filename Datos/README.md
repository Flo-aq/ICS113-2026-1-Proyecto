# Datos — Generación de Instancias del Modelo

Pipeline de datos para el modelo de optimización de centros de triaje post-terremoto
(Región de Valparaíso, Mw ≥ 8.0, horizonte 7 días).

---

## Uso rápido

```bash
python Datos/construir_instancia.py
```

Genera todos los CSVs del modelo en `Datos/data/` usando la configuración por defecto
(5 comunas del modelo, top-2 colegios, escenario intermedio).

---

## Estructura

```
Datos/
├── construir_instancia.py          Script maestro — punto de entrada principal
├── comunas.json                    Mapa ID → nombre de todas las comunas de Región 5
├── poblacion_comunas_censo2024_consolidado.csv   Población por comuna (INE 2024)
│
├── colegios/
│   ├── Colegios.csv                Directorio MINEDUC (matrícula + coordenadas)
│   ├── filtrar_colegios.py         Filtra colegios y calcula cap_j, f_j, o_j, req_j
│   ├── colegios_filtrados.csv      Output intermedio (generado automáticamente)
│   ├── columnas_colegios.json      Mapa columna → índice de Colegios.csv
│   └── normativa_recintos_escolares.md   Fuente normativa de la fórmula de cap_j
│
├── recintos/
│   ├── infraestructura_deportiva_consolidada.csv   Estadios y polideportivos
│   ├── filtrar_recintos.py         Filtra recintos operativos y calcula f_j, o_j, req_j
│   └── recintos_filtrados.csv      Output intermedio (generado automáticamente)
│
├── hospitales/                     Pendiente de implementación
│
├── parametros/
│   ├── costos_pma.md               Metodología y fuentes de f_j y o_j
│   ├── personal_y_capacidad.md     Metodología y fuentes de req_j, H_t, MaxC_t, ratio_g
│   └── demanda.md                  Metodología y fuentes de TAU, PROP, PHI, Pres
│
└── data/                           CSVs finales para el código Gurobi
    ├── nodos_comunas.csv
    ├── nodos_centros.csv
    ├── demanda.csv
    ├── demanda_max.csv
    ├── tiempos_ij.csv
    ├── cobertura_ij.csv
    ├── personal_dia.csv
    ├── max_centros_dia.csv
    └── parametros.csv
```

---

## Parámetros configurables

Todos los parámetros se editan en el bloque `__main__` de `construir_instancia.py`:

```python
main(
    comunas_ids=[8, 27, 35, 36, 37],  # IDs de comunas.json
    n_colegios=2,                      # Top-N colegios por matrícula por comuna
    holgura=0.0,                       # % sobre cap_j de colegios (+20 → más, -20 → menos)
    escenario=2,                       # 1=conservador, 2=intermedio, 3=optimista
)
```

### `comunas_ids`
Lista de IDs enteros del archivo `comunas.json`. Cada ID corresponde a una comuna de
la Región de Valparaíso. `None` incluye todas las comunas.

**5 comunas del modelo E2:**
| ID | Comuna |
|----|--------|
| 8 | Concón |
| 27 | Quilpué |
| 35 | Valparaíso |
| 36 | Villa Alemana |
| 37 | Viña del Mar |

Ver `comunas.json` para el listado completo de las 38 comunas de Región 5.

### `n_colegios`
Top-N colegios con mayor matrícula por comuna (mínimo matrícula: 300 alumnos).
Aumentar este valor genera más centros candidatos J en el modelo.

### `holgura`
Porcentaje aplicado sobre la capacidad estimada `cap_j` de los colegios:
- `holgura = 0.0` → capacidad base (OGUC/SPHERE)
- `holgura = -20` → estimación conservadora (−20%)
- `holgura = +20` → estimación optimista (+20%)

No afecta a los recintos deportivos (su capacidad es el aforo oficial del CSV).

### `escenario`
Controla las curvas de recursos humanos disponibles. Ver `parametros/personal_y_capacidad.md`.

| Escenario | `H_t` (día 1 → 7) | `MaxC_t` (día 1 → 7) | `ratio_leve` | `ratio_moderado` |
|-----------|-------------------|----------------------|:------------:|:----------------:|
| 1 — conservador | 8 → 28 | 4 → 10 | 25 | 10 |
| 2 — intermedio *(default)* | 10 → 59 | 2 → 10 | 30 | 12 |
| 3 — optimista | 12 → 90 | 2 → 16 | 96 | 36 |

---

## Parámetros del modelo en `data/parametros.csv`

| Parámetro | Valor default | Descripción |
|-----------|:------------:|-------------|
| `T_max` | 30 min | Tiempo máximo de viaje al PMA |
| `L` | 3 días | Mínimo de días de operación continua |
| `Pres` | 1,200,000,000 CLP | Presupuesto total red de PMAs |
| `P_leve` | 1 | Peso prioridad leves en función objetivo |
| `P_moderado` | 10 | Peso prioridad moderados en función objetivo |
| `tau_total` | 0.005 | Heridos por habitante (MMI VIII) |
| `prop_leve` | 0.74 | Fracción heridos leves |
| `prop_moderado` | 0.26 | Fracción heridos moderados |
| `factor_vial` | 1.35 | Corrección Haversine → distancia real |
| `vel_kmh` | 25 | Velocidad emergencia post-terremoto |

Para cambiar estos valores, editar los parámetros de `generar_parametros_escalares()`
en `construir_instancia.py`.

---

## Uso como módulo desde código Gurobi

```python
import sys
sys.path.insert(0, "Datos")
from construir_instancia import (
    cargar_comunas, cargar_centros,
    calcular_tiempos, calcular_cobertura,
    calcular_demanda, generar_parametros_escalares,
)

comunas = cargar_comunas(["VINA DEL MAR", "VALPARAISO", "QUILPUE"])
centros = cargar_centros(comunas, n_colegios=3)
tiempos = calcular_tiempos(comunas, centros)
cobertura = calcular_cobertura(tiempos, t_max=30)
demanda = calcular_demanda(comunas)
params = generar_parametros_escalares(centros, escenario=2)
```

---

## Ejecutar scripts individuales

Cada script puede correrse de forma independiente para regenerar solo su output:

```bash
# Regenerar colegios_filtrados.csv (editar __main__ para cambiar parámetros)
python Datos/colegios/filtrar_colegios.py

# Regenerar recintos_filtrados.csv
python Datos/recintos/filtrar_recintos.py
```

---

## Fuentes de datos

| Archivo | Fuente |
|---------|--------|
| `colegios/Colegios.csv` | MINEDUC — Directorio de Establecimientos (datos.mineduc.cl) |
| `recintos/infraestructura_deportiva_consolidada.csv` | Wikipedia / Google Maps / municipios (consolidado manualmente) |
| `poblacion_comunas_censo2024_consolidado.csv` | INE — Censo de Población y Vivienda 2024 |
| `comunas.json` | Generado automáticamente desde `Colegios.csv` |
| `parametros/` | Ver bibliografía en cada archivo `.md` |
