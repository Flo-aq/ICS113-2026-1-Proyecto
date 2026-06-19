# Resultados — Modelo PMA Valparaíso

Modelo de optimización de Puestos Médicos Avanzados (PMA) post-terremoto Mw ≥ 8.0,
Región de Valparaíso. Horizonte de planificación: 7 días.

---

## Instancia

| Conjunto / Parámetro | Valor |
|----------------------|-------|
| Comunas (I) | 36 (continentales Región 5, excl. Isla de Pascua y Juan Fernández) |
| Centros candidatos (J) | 85 (70 colegios + 15 recintos deportivos) |
| Hospitales (K) | 32 |
| Gravedades (G) | leve, moderado, grave |
| Horizonte (T) | 7 días |
| tau (heridos/hab) | 0,009 (MMI VIII) |
| Prop. leve / mod / grave | 66,6% / 23,4% / 10,0% |
| Demanda total leve + mod | 14.530 pacientes |
| Demanda total grave | 1.614 pacientes |
| L (permanencia mínima) | 3 días |
| Presupuesto | 2.270.000.000 CLP |

---

## Parámetros normativos

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| `FACTOR_USO_REFUGIO` | 0,65 | OGUC Art. 4.8.2 |
| `M2_POR_PERSONA` | 3,5 m²/persona | Estándar SPHERE (2018) |
| `P_leve` | 1 | Peso FO espera leve |
| `P_moderado` | 10 | Peso FO espera moderado |
| `ratio_leve` | 30 pac/equipo/día | — |
| `ratio_moderado` | 12 pac/equipo/día | — |
| `c_dist` | 1/60 por min | Penalización distancia grave → hospital |
| `c_pma` | 50 | Penalización grave atendido en PMA |

---

## Runs ejecutados

Se corrieron 9 instancias variando `T_max` (radio de cobertura PMA) y el factor de equipos médicos.

**H_t base** (escenario 2 intermedio, escalado 1,892× para 36 comunas): `[19, 32, 55, 78, 93, 104, 112]`

| Carpeta | T_max | Factor H_t | H_t día 7 | MaxC_t día 7 |
|---------|-------|------------|-----------|--------------|
| `T30_H100` | 30 min | ×1,0 | 112 | 19 |
| `T30_H125` | 30 min | ×1,25 | 140 | 24 |
| `T30_H150` | 30 min | ×1,5 | 168 | 28 |
| `T45_H100` | 45 min | ×1,0 | 112 | 19 |
| `T45_H125` | 45 min | ×1,25 | 140 | 24 |
| `T45_H150` | 45 min | ×1,5 | 168 | 28 |
| `T60_H100` | 60 min | ×1,0 | 112 | 19 |
| `T60_H125` | 60 min | ×1,25 | 140 | 24 |
| `T60_H150` | 60 min | ×1,5 | 168 | 28 |

Pares (i,j) cubiertos: T30 = 114/3.060 (3,7%) · T45 = 288/3.060 (9,4%) · T60 = 393/3.060 (12,8%)

---

## Resultados por run


### T30_H100 — base

FO = 82.857 · Tasa leve 39,4% · Tasa mod 96,4% · Runtime 33 s

---

### T30_H125

FO = 64.408 · Tasa leve 77,7% · Tasa mod 97,6% · Runtime 23 s

---

### T30_H150 - optimizado

FO = 50.178 · Tasa leve 99,8% · Tasa mod 99,6% · Runtime 23 s

---

### T45_H100

FO = 80.444 · Tasa leve 45,3% · Tasa mod 97,4% · Runtime 7 s

---

### T45_H125

FO = 61.764 · Tasa leve 79,4% · Tasa mod 98,3% · Runtime 74 s · Esp. leve d7 = 2.215 · Esp. mod d7 = 63

---

### T45_H150

FO = 48.030 · Tasa leve 99,8% · Tasa mod 99,7% · Runtime 9 s · Esp. leve d7 = 21 · Esp. mod d7 = 12

---

### T60_H100

FO = 78.028 · Tasa leve 47,9% · Tasa mod 98,8% · Runtime 12 s · Esp. leve d7 = 5.598 · Esp. mod d7 = 47

---

### T60_H125

FO = 59.063 · Tasa leve 82,7% · Tasa mod 99,1% · Runtime 13 s · Esp. leve d7 = 1.856 · Esp. mod d7 = 35

---

### T60_H150

FO = 45.925 · Tasa leve 99,8% · Tasa mod 99,7% · Runtime 14 s · Esp. leve d7 = 21 · Esp. mod d7 = 11

---

## Resumen comparativo

### Función objetivo

|          | H_t ×1,0 | H_t ×1,25 | H_t ×1,5 |
|----------|----------|-----------|----------|
| T_max 30 | 82.857 | 64.408 | 50.178 |
| T_max 45 | 80.444 | 61.764 | 48.030 |
| T_max 60 | 78.028 | 59.063 | 45.925 |

### Tasa de atención leve+moderado (día 7)

|          | H_t ×1,0 | H_t ×1,25 | H_t ×1,5 |
|----------|----------|-----------|----------|
| T_max 30 | 54,2% | 82,8% | **99,7%** |
| T_max 45 | 58,9% | 84,3% | **99,8%** |
| T_max 60 | 61,1% | 87,0% | **99,8%** |

---

## Archivos por run

Cada carpeta `resultados/Txx_Hyyy/` contiene:

| Archivo | Contenido |
|---------|-----------|
| `resumen.txt` | Resumen por día y centros activos |
| `resultado_resumen_dia.csv` | Métricas agregadas por día |
| `resultado_activacion.csv` | Estado z, v, c, p por centro y día |
| `resultado_asignacion_centros.csv` | Pacientes a_ijtg asignados a PMAs |
| `resultado_asignacion_hospitales.csv` | Graves asignados a hospitales |
| `resultado_stock_espera.csv` | Stock de espera s_itg por zona y día |

Para regenerar los runs T45 y T60: `python run_experiments.py`
Para regenerar los runs T30: ejecutar manualmente con los H_t correspondientes en `construir_instancia.py`.
