# Capacidad Hospitalaria Post-Sismo — Cap_{k,t}

Parámetro de capacidad operativa del hospital k en el día t para el modelo de
optimización de Zonas de Triaje post-terremoto, Región de Valparaíso.
Horizonte: 7 días. Escenario: sismo Mw ≥ 8.0 con potencial tsunamigénico.

---

## Cap_{k,t} — Capacidad diaria del hospital k en el día t

### Fórmula

```
Cap_{k,t} = round(Camas2023_k × CURVAS[categoria_k][t - 1])
```

`Camas2023_k` es la dotación de camas pre-sismo (dato 2023, fuente DEIS-MINSAL).
`categoria_k` se determina a partir de altitud, tipo y nivel de complejidad del establecimiento.

---

## Umbral tsunami (Restricción 8)

```
TSUNAMI_THRESHOLD = 30 m sobre el nivel del mar  ("cota 30")
```

La cota 30 es el umbral oficial de zona segura para evacuación por tsunami en Chile,
establecido por SENAPRED/SHOA y ratificado por la Guía MINVU (2018) y el PNEVR Tsunami.
Modelos de inundación para el escenario 1730 (Mw 9.1–9.3) estiman alturas máximas de
6–8 m en Viña del Mar/Concón y hasta 9 m en San Antonio, dejando margen de seguridad
amplio respecto a la cota 30 (Martínez et al. 2020; Inzunza & Martínez 2024).

---

## Categorías y curvas de recuperación

Cada hospital se clasifica en una de seis categorías. La curva representa la fracción
de `Camas2023` operativa cada día.

| Categoría | t=1 | t=2 | t=3 | t=4 | t=5 | t=6 | t=7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tsunami_flood`    | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `tsunami_vertical` | 0.00 | 0.00 | 0.20 | 0.30 | 0.40 | 0.50 | 0.60 |
| `moderno_alto`     | 0.85 | 0.88 | 0.91 | 0.94 | 0.96 | 0.98 | 1.00 |
| `antiguo_alto`     | 0.50 | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | 0.80 |
| `bajo_publico`     | 0.30 | 0.38 | 0.47 | 0.55 | 0.63 | 0.70 | 0.75 |
| `privado`          | 0.80 | 0.85 | 0.90 | 0.95 | 1.00 | 1.00 | 1.00 |

### Descripción y justificación por categoría

#### `tsunami_flood` — Altitud < 30 m, sin evacuación vertical
Hospitales en zona de inundación que no tienen altura suficiente para evacuación
vertical. Protocolo chileno exige evacuación total de pacientes y personal.
Para Mw ≥ 8.0 con inundación real, unidades críticas en plantas bajas (emergencia,
imagenología, esterilización) quedan inutilizadas por agua salina y lodo.
Capacidad nula durante todo el horizonte de 7 días.

**Fuentes:** MINSAL (2015): 22 hospitales evacuados en sismo Illapel; SENAPRED PNEVR
Tsunami; FEMA HAZUS Flood: inundación > 1 m inhabilita equipamiento de planta baja.

#### `tsunami_vertical` — Altitud < 30 m, evacuación vertical posible
Hospitales costeros de alta complejidad en edificios de varios pisos que permiten
reubicar funciones críticas en plantas altas. En la alerta de julio 2025, tanto
Van Buren como Fricke ejecutaron evacuación vertical y retornaron a operación
parcial al día siguiente.
Para Mw ≥ 8.0 con inundación de plantas bajas, se modela retorno gradual desde t=3.

Hospitales en esta categoría (hardcoded):
- **Hospital Carlos Van Buren** (Valparaíso, 19 m) — edificio de 6 pisos
- **Hospital Dr. Gustavo Fricke** (Viña del Mar, 10 m) — 8 pisos, 193 aisladores sísmicos

**Fuentes:** Alerta tsunami 30-jul-2025 (G5Noticias, Cooperativa Ciencia); 27-F:
evacuación preventiva Van Buren y Fricke (Puranoticia 2010).

#### `moderno_alto` — Alta complejidad, moderno / base-isolated
Hospitales de alta complejidad reconstruidos post-27F o con aisladores sísmicos.
Mitrani-Reiser et al. (2012): hospitales con aislación y buena norma sísmica retienen
85–100% de capacidad estructural en t=1; pérdidas se limitan a componentes no
estructurales (cielos, tabiques) y suministros básicos (agua/electricidad) por 1–3 días.

Hospitales en esta categoría (hardcoded, reconstruidos post-27F o base-isolated):
- Hospital Dr. Gustavo Fricke (193 aisladores sísmicos, inaugurado 2019)
- Hospital San Camilo de San Felipe (reconstruido post-27F)
- Hospital San Juan de Dios (Los Andes) (reconstruido post-27F)
- Hospital Biprovincial Quillota Petorca (moderno)
- Hospital de Quilpué (reconstruido)

**Fuentes:** Mitrani-Reiser et al. (2012); Christchurch Riverside Hospital: 16% pérdida
permanente en sismo 7.1 (Jacques et al. 2014); SCAR (2010): especificaciones técnicas
Fricke; Aarqhos (2018): Hospital Gustavo Fricke post-27F.

#### `antiguo_alto` — Alta complejidad, antiguo sin aislación
Hospitales de alta complejidad con infraestructura anterior a 2000, sin aisladores.
Ancla empírica directa: Hospital Claudio Vicuña (San Antonio) pasó de 164 a 67 camas
tras 27-F = 41% retenido en t=1. Promedio SS Valparaíso-San Antonio: 97.7% retenido
en t=1, degradando a 93% en t=2 por inspecciones tardías.
Se adopta 50% como valor central entre el peor caso documentado (41%) y el promedio
regional (97.7%), ponderando por antigüedad de la infraestructura.

**Fuentes:** Hospital Claudio Vicuña historia institucional (hcv.cl);
MINSAL/OPS (2010) PAHO IRIS 10665.2/10037; Kirsch et al. (2010).

#### `bajo_publico` — Baja/Mediana complejidad público
Hospitales comunitarios y rurales con infraestructura más antigua y vulnerable.
Caso extremo documentado: Hospital San Antonio de Putaendo redujo a 6 camas desde
t=1 hasta mayo 2011 (21% retenido). Promedio SS Aconcagua en t=1: 64.4% retenido.
Valor central 30% en t=1 refleja vulnerabilidad alta de establecimientos pequeños
con construcción no reforzada o de adobe.

**Fuentes:** Wikipedia - Servicio de Salud Aconcagua (daños 27-F);
MINSAL (2010); Kirsch et al. (2010).

#### `privado` — Clínica privada
Clínicas privadas con infraestructura generalmente más moderna, menor antigüedad
y mejor mantenimiento. Favier et al. (2019): reorganización operativa interna rápida
en clínicas privadas post-sismo en Chile.

**Fuentes:** Favier et al. (2019) *Earthquake Spectra*; extrapolado de comportamiento
de instalaciones privadas en 27-F (sin datos directos disponibles).

---

## Lógica de clasificación (orden de prioridad)

```
1. Altitud_m < 30 Y nombre en VERTICAL_EVAC  →  tsunami_vertical
2. Altitud_m < 30                             →  tsunami_flood
3. TipoEstablecimiento == "Clínica"           →  privado
4. nombre en HOSPITALES_MODERNOS              →  moderno_alto
5. NivelComplejidad == "Alta Complejidad"     →  antiguo_alto
6. resto                                      →  bajo_publico
```

---

## Cobertura hospitalaria — A_{i,k}

El criterio de cobertura para hospitales no es el tiempo de viaje (como en los centros
de triaje J), sino la **colindancia comunal** (supuesto del modelo, sección 1.5 del E2):

> "Un centro puede atender a una zona si se encuentra en la misma comuna o en una
> comuna colindante, aproximando restricciones de accesibilidad en emergencias."

```
A_{i,k} = 1  si  comuna(k) == comuna(i)  O  comuna(k) ∈ adj[comuna(i)]
A_{i,k} = 0  en caso contrario
```

La matriz de colindancia está en `Datos/colindancia.json`.

---

## Ejemplos numéricos

| Hospital | Camas2023 | Altitud | Categoría | Cap_1 | Cap_4 | Cap_7 |
|---|---:|---:|---|---:|---:|---:|
| Hospital Dr. Gustavo Fricke | 558 | 10 m | `tsunami_vertical` | 0 | 167 | 335 |
| Hospital Carlos Van Buren | 363 | 19 m | `tsunami_vertical` | 0 | 109 | 218 |
| Clínica Valparaíso | 63 | 9 m | `tsunami_flood` | 0 | 0 | 0 |
| Hospital San Camilo | 221 | 662 m | `moderno_alto` | 188 | 208 | 221 |
| Hospital Claudio Vicuña | 164 | 55 m | `antiguo_alto` | 82 | 107 | 131 |
| Hospital de Petorca | 18 | 504 m | `bajo_publico` | 5 | 10 | 14 |
| Clínica Reñaca | 158 | 168 m | `privado` | 126 | 150 | 158 |
| Hospital Adriana Cousiño | 31 | 17 m | `tsunami_flood` | 0 | 0 | 0 |

---

## Referencias

Favier, P., Poulos, A., Vásquez, J. A., De la Llera, J. C., & Mitrani-Reiser, J.
(2019). Seismic risk assessment of an emergency department of a Chilean hospital
using a performance-based earthquake engineering framework. *Earthquake Spectra*,
35(2), 489–514. https://doi.org/10.1193/101417EQS208M

Inzunza, G., & Martínez, C. (2024). CRET: A comprehensive risk evaluation tool for
tsunami hazard assessment in coastal territories of central Chile. *Natural Hazards
and Earth System Sciences*, 24, 2145–2162.

Jacques, C. C., McIntosh, J., Giovinazzi, S., Kirsch, T. D., Wilson, T., &
Mitrani-Reiser, J. (2014). Resilience of the Christchurch hospital system to the
2011 earthquake. *Earthquake Spectra*, 30(1), 533–554.

Kirsch, T. D., Mitrani-Reiser, J., & De la Llera, J. C. (2010). Functionality loss
in hospitals following the 2010 Maule, Chile earthquake. *PLoS Medicine*, 7(10).

Martínez, C., et al. (2020). Worst-case tsunami scenario in Cartagena Bay, central
Chile. *Natural Hazards*, 94(3), 1089–1120.

Ministerio de Salud de Chile. (2010). *El terremoto y tsunami del 27 de febrero en
Chile: Crónica y lecciones aprendidas en el sector salud*. OPS/OMS.
PAHO IRIS handle 10665.2/10037.

Ministerio de Vivienda y Urbanismo. (2018). *Guía de referencia para sistemas de
evacuación comunales por tsunami*. MINVU.

Mitrani-Reiser, J., et al. (2012). A functional loss assessment of a hospital system
in the Bío-Bío Province, Chile. *Earthquake Spectra*, 28(2), 473–502.

SENAPRED / SHOA. (2024). *Plan Nacional de Emergencia por Variable de Riesgo Tsunami
(PNEVR)*. Gobierno de Chile.
