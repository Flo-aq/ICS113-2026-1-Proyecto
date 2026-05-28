# Parámetros de Demanda — TAU_TOTAL, PROP, PHI, D_i,t,g

Parámetros que determinan cuántos heridos se generan, su distribución por gravedad
y cómo se distribuyen en el tiempo durante los 7 días post-terremoto.

---

## Fórmula general de demanda

```
D_i,t,g = pop_i × TAU_TOTAL × PROP_g × PHI_t

D^max_i,g = max(D_i,t,g  para todo t)
```

Donde:
- `pop_i`: población de la comuna i (Censo 2024, `poblacion_comunas_censo2024_consolidado.csv`)
- `TAU_TOTAL`: tasa total de heridos por habitante
- `PROP_g`: proporción del tipo g sobre el total de heridos
- `PHI_t`: fracción de la demanda total que llega el día t

La suma garantiza: `Σ_t PHI_t = 1` y `Σ_g PROP_g = 1`.

---

## TAU_TOTAL — Tasa de heridos por habitante

**Valor**: `0.005` (5 heridos por cada 1,000 habitantes)

### Justificación

La tasa se basa en la **Escala de Intensidad de Mercalli Modificada (MMI)**, nivel VIII,
que corresponde a un sismo de gran magnitud (Mw ≈ 7.5–8.5) con daño estructural severo
en construcciones vulnerables.

| MMI | Descripción | Tasa de heridos (por 1,000 hab.) |
|-----|-------------|--------------------------------:|
| VI | Daño leve | 0.05 – 0.2 |
| VII | Daño moderado | 0.5 – 1.0 |
| **VIII** | **Daño severo** | **2.0 – 10.0** |
| IX | Destrucción parcial | 10 – 50 |
| X–XII | Destrucción masiva | > 50 |

El valor de **5 / 1,000 = 0.005** corresponde al punto medio del rango MMI VIII.

### Referencia histórica — 27-F (2010, Mw 8.8)

El terremoto del 27 de febrero de 2010 afectó a 6 regiones con una población combinada
de ~12 millones de habitantes. Se reportaron aproximadamente 12,000 heridos atendidos
(MINSAL, informe oficial 2010) y ~525 fallecidos. Heridos / 1,000 hab. ≈ 1.0 a nivel
nacional, pero la concentración en las regiones del Bío-Bío y Maule (epicentro) implicó
tasas locales de 5–8 / 1,000. Como el modelo de Valparaíso asume un epicentro cercano
(interfaz de Nazca-Sudamérica frente a la región), se adopta la tasa local de **5 / 1,000**.

### Fuentes

- **OPS/PAHO (2010)**, *Terremoto en Chile: lecciones y desafíos*
- **Tabla de Mercalli Modificada** (USGS / SHOA)
- Datos del MINSAL post-27F (heridos totales por región)
- Supuesto del modelo (consistente con generar_datos.py original)

---

## PROP — Proporción por tipo de gravedad

**Valores**: `PROP_leve = 0.74`, `PROP_moderado = 0.26`

### Justificación

La distribución entre heridos leves y moderados se basa en la evidencia epidemiológica
de desastres sísmicos. El modelo del E2 considera solo dos tipos (leve y moderado),
excluyendo los heridos graves (críticos, que van directamente a hospitales).

| Tipo | Categoría START | Fracción típica | Valor adoptado |
|------|----------------|----------------:|---------------:|
| Leve (verde) | Ambulatorio, baja complejidad | 60–80% | **74%** |
| Moderado (amarillo) | Estabilización necesaria | 15–30% | **26%** |
| Grave (rojo) | SVA + cirugía urgente | 5–15% | *(excluido del modelo)* |
| Fallecido (negro) | Sin intervención | 1–5% | *(excluido)* |

Los heridos graves y fallecidos se desvían directamente a los hospitales de la red
asistencial, por lo que se excluyen del conjunto G del modelo (PMAs solo manejan
leves y moderados). Las proporciones 74%/26% corresponden a la distribución
residual de la masa de heridos manejable en PMAs periféricos.

### Evidencia

- **27-F Chile (2010)**: de los ~12,000 heridos reportados, ~9,000 fueron atendidos
  ambulatoriamente (75%) y ~3,000 requirieron hospitalización (25%).
- **Yushu 2010, China** (PMC4690927): distribución START ≈ 70% verde / 20% amarillo /
  10% rojo (de los supervivientes que llegaron a instalaciones médicas).
- **Gemini (research_gemini.md)**: confirma rango 70–80% leve / 20–26% moderado.

---

## PHI — Distribución temporal de llegadas (7 días)

**Valores**: `PHI = [0.25, 0.20, 0.15, 0.12, 0.10, 0.10, 0.08]`

### Justificación

La demanda de atención no es uniforme: el mayor flujo llega en los primeros días,
cuando los heridos buscan atención inmediata. La curva decae exponencialmente,
reflejando que los casos agudos se atienden rápido y los tardíos corresponden
principalmente a complicaciones o heridos que tardaron en ser rescatados.

| Día t | PHI_t | % acumulado | Interpretación |
|-------|------:|------------:|----------------|
| 1 | 0.25 | 25% | Pico de llegadas: heridos inmediatos post-colapso |
| 2 | 0.20 | 45% | Segunda oleada: rescatados de escombros |
| 3 | 0.15 | 60% | Heridos tardíos y complicaciones tempranas |
| 4 | 0.12 | 72% | Heridos de zonas rurales o aisladas |
| 5 | 0.10 | 82% | Complicaciones de heridas no tratadas |
| 6 | 0.10 | 92% | Casos crónicos descompensados + trauma diferido |
| 7 | 0.08 | 100% | Cola de demanda residual |

La suma total es exactamente 1.00.

### Caveat importante (research_claude.md)

> *"By day 10, less than 50% of patients treated will be due to earthquake-related
> injuries"* (Bar-On E, Acta Orthop Traumatol Turc, 2023, PMC10837594).

Esto significa que a partir del día 5–6, la demanda en los PMAs comienza a estar
dominada por enfermedades crónicas descompensadas (hipertensión, diabetes, etc.)
y no solo por trauma agudo. El PHI del modelo captura esto con la cola plana de
días 5–7 (10%, 10%, 8%).

### Fuentes

- **OPS/PAHO** patrones de demanda post-terremoto (27-F, Haití 2010, Ecuador 2016)
- **Bar-On E (2023)**, *Acta Orthopaedica et Traumatologica Turcica*, PMC10837594
- Curva empírica derivada de la experiencia 27-F y ajustada a horizonte de 7 días
- Supuesto del modelo (consistente con generar_datos.py original)

---

## Presupuesto Pres

**Valor**: `1,200,000,000 CLP` (~USD 1.26 M)

Específicamente para la red de PMAs (colegios + estadios) durante 7 días,
**excluyendo** hospitales, evacuación y logística general.

### Feasibility check (Gemini)

```
Escenario: 6 colegios + 3 estadios activos (9 PMAs, días 3–7)

Costos fijos (apertura):
  6 × 22,500,000 =  135,000,000 CLP
  3 × 58,000,000 =  174,000,000 CLP
  Total fijos    =  309,000,000 CLP

Costos operativos (5 días × 9 PMAs):
  (6 × 2,800,000 + 3 × 6,200,000) × 5 = 177,000,000 CLP

Total estimado = 486,000,000 CLP  ←  40.5% de Pres
Holgura        = 714,000,000 CLP  ←  59.5% para imprevistos
```

La holgura del ~60% permite al optimizador operar sin quedar bloqueado por la
restricción presupuestaria en escenarios de tamaño razonable.

### Fuentes

- **SENAPRED presupuesto 2024**: CLP 23,148,341,000 total nacional (El Mostrador, 20-feb-2024).
  Para Valparaíso (1/16 regiones): ~CLP 1,450M anuales → ~CLP 28M/semana ordinaria.
  En catástrofe, el Fondo de Emergencia de la Subsecretaría del Interior puede
  multiplicar este monto por 10–50x.
- **IFRC 27-F final appeal (MDRCL006)**: CHF 16M (~CLP 15,600M) para 36 meses
  de respuesta total, no solo médica.
- Adopción de valor Gemini para el scope específico del modelo. Confianza: Media.

---

## Otros parámetros escalares del modelo

| Parámetro | Valor | Fuente / Justificación |
|-----------|------:|------------------------|
| `T_max` | 30 min | Tiempo máximo aceptable de viaje al PMA. Estándar PAHO para trauma agudo; coherente con velocidad post-desastre de 25 km/h y FACTOR_VIAL 1.35. |
| `L` | 3 días | Mínimo de días que un PMA debe permanecer activo una vez abierto. Evita aperturas y cierres de 1–2 días que no amortizan el costo fijo f_j. |
| `P_leve` | 1 | Peso de prioridad para pacientes leves en la función objetivo. |
| `P_moderado` | 10 | Peso de prioridad para pacientes moderados (10× más que leves). Refleja mayor riesgo de deterioro. |
| `VEL_KMH` | 25 | Velocidad media en emergencia post-terremoto (km/h). Conservadora por obstrucción de vías. |
| `FACTOR_VIAL` | 1.35 | Corrección Haversine → distancia real. Factor empírico para trama urbana irregular. |
| `FACTOR_CAMAS` | 0.907 × 0.85 | Camas hospitalarias operativas post-sismo: 90.7% × 85% = 77.1%. 90.7% de datos 27-F (MINSAL 2010); 85% margen de seguridad adicional. |

---

## Bibliografía

Bar-On, E., Unger, R., Kessel, B., & Kluger, Y. (2023). Medical care following earthquakes: Clinical, organizational, and logistic challenges. *Acta Orthopaedica et Traumatologica Turcica*, 57(6), 296–300. PMC10837594. https://doi.org/10.5152/j.aott.2023.23127
> «By day 10, <50% of patients treated will be due to earthquake-related injuries.» Justifica la cola plana de PHI en días 5–7.

Dirección de Presupuestos (DIPRES), Ministerio de Hacienda. (2024). *Ley de Presupuestos del Sector Público 2024*. Gobierno de Chile. https://www.dipres.gob.cl/
> Línea de la Subsecretaría del Interior para emergencias. Base para escala de Pres.

El Mostrador. (2024, 20 de febrero). Las grietas del Senapred: presupuesto exiguo y falta de personal. https://www.elmostrador.cl/noticias/pais/2024/02/20/las-grietas-del-senapred-presupuesto-exiguo-y-falta-de-personal/
> Presupuesto SENAPRED 2024: CLP 23,148,341,000 total nacional. Base para calibración de Pres.

Instituto Nacional de Estadísticas de Chile (INE). (2024). *Censo de Población y Vivienda 2024 — Resultados por comuna, Región de Valparaíso*. https://www.ine.gob.cl/estadisticas/sociales/censos-de-poblacion-y-vivienda/censo-de-poblacion-y-vivienda
> Fuente de `pop_i` para el cálculo de D_i,t,g. Datos en `poblacion_comunas_censo2024_consolidado.csv`.

International Federation of the Red Cross and Red Crescent Societies (IFRC). (2010). *Chile: Earthquake Emergency Appeal N° MDRCL006*. https://go-api.ifrc.org/publicfile/download?path=/docs/appeals/10/&name=MDRCL006eu12.pdf
> CHF 16,075,870 (~CLP 15,600M) para 36 meses de respuesta total. Contexto para escala de Pres.

Ministerio de Salud de Chile (MINSAL). (2010). *Informe de situación: atención de heridos tras terremoto del 27 de febrero de 2010*. Gobierno de Chile.
> ~12,000 heridos atendidos: ~9,000 ambulatorios (75%), ~3,000 hospitalizados (25%). Base para PROP.

Ochi, S., Kato, S., Kobayashi, K., & Wakai, S. (2015). Emergency medical response in the 2010 Yushu earthquake. *International Journal of Environmental Research and Public Health*, 12(12), 15831–15845. https://doi.org/10.3390/ijerph121215016
> Distribución START post-Yushu: ~70% verde / 20% amarillo / 10% rojo. Base adicional para PROP.

Organización Panamericana de la Salud (OPS/PAHO). (2011). *Terremoto en Chile: lecciones aprendidas para la respuesta en salud*. https://www.paho.org/es
> Tasas de heridos post-27F por región (~5–8/1,000 hab. en epicentro). Patrones de demanda para PHI. Base para TAU_TOTAL.

Secretaría Nacional de Protección Civil (SENAPRED). (2024). *Presupuesto 2024: Asignación de recursos por región*. https://www.senapred.gob.cl/
> CLP 23,148,341,000 total nacional (16 regiones). Contexto para Pres.

United States Geological Survey (USGS). (2023). *Modified Mercalli Intensity Scale*. https://www.usgs.gov/programs/earthquake-hazards/modified-mercalli-intensity-scale
> Tabla MMI VIII: 2–10 heridos/1,000 hab. Valor 5/1,000 adoptado como punto medio. Base para TAU_TOTAL.
