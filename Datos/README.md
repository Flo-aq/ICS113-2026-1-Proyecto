# Generador de datos

Scripts Python que arman instancias del modelo

**Entradas:** `Colegios.csv` (MINEDUC) y `poblacion_comunas_censo2024_consolidado.csv`.

## Scripts y salidas

| Script | Qué hace | Salida |
|--------|----------|--------|
| `generar_datos.py` | 5 comunas Informe 2, 2 colegios c/u | `data/` |
| `generar_datos_configurable.py` | N comunas al azar (o `--lista`) y K colegios c/u | `data/configurable/` |
| `generar_datos_completo.py` | ~37 comunas región 5, todos o top N colegios | `data/completo/` |

Cada script escribe en **su carpeta**; no se pisan entre sí.

## Ejecución

Desde la raíz del repo o desde `Datos/`:

```bash
python Datos/generar_datos.py
python Datos/generar_datos_configurable.py --comunas 8 --escuelas 3 --seed 42
python Datos/generar_datos_completo.py --escuelas 3

o tambien dependiendo

python3 Datos/generar_datos.py
python3 Datos/generar_datos_configurable.py --comunas 8 --escuelas 3 --seed 42
python3 Datos/generar_datos_completo.py --escuelas 3
```

### Configurable

| Flag | Default | |
|------|---------|--|
| `--comunas` | 5 | Cuántas comunas sortear |
| `--escuelas` | 2 | Top K colegios por matrícula |
| `--seed` | — | Repetir la misma muestra |
| `--lista` | — | Comunas fijas: `"VIÑA DEL MAR,VALPARAISO"` |
| `--mat-min` | 300 | Matrícula mínima |
| `--listar-comunas` | | Ver comunas disponibles |

### Completo

| Flag | Default | |
|------|---------|--|
| `--escuelas` | todos | Top N por comuna; sin flag ≈430 centros |
| `--mat-min` | 300 | |

## CSV generados

En cada carpeta de salida: `nodos_comunas.csv`, `nodos_centros.csv`, `nodos_hospitales.csv`, `demanda.csv`, `demanda_max.csv`, `tiempos_ij.csv`, `tiempos_ik.csv`, `cobertura_ij.csv`, `cobertura_ik.csv`, `cap_hospital_dia.csv`, `personal_dia.csv`, `max_centros_dia.csv`, `parametros.csv`.

## Notas

- **Hospitales:** siempre 3 (Valparaíso / Viña); el modo completo no amplía la red MINSAL.
- **Completo sin `--escuelas`:** instancia muy grande; para pruebas use `--escuelas 2` o `3`.
-  `Colegios.csv`: [datosabiertos.mineduc.cl](https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/).
