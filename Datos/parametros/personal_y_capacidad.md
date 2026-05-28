# Personal y Capacidad Operativa — req_j, H_t, MaxC_t, ratio_g

Parámetros de recursos humanos y límites operativos del modelo de optimización
de PMAs post-terremoto. La unidad base es el **Equipo Equivalente de Salud (EES)**:
1 médico + 1 enfermera/o + 2 TENS (técnicos en enfermería de nivel superior).

---

## req_j — Equipos mínimos para abrir un PMA

### Fórmula (escala con cap_j)

```
REQ_POR_PERSONA_COLEGIO = 3 / 500  = 0.006  EES / persona
REQ_POR_PERSONA_ESTADIO = 6 / 3000 = 0.002  EES / persona
REQ_MIN_COLEGIO = 2   (nunca abrir con menos de 2 EES)
REQ_MIN_ESTADIO = 3

req_j = max(req_min_tipo, ceil(REQ_POR_PERSONA_tipo × cap_j))
```

### Valores de referencia y justificación

| Tipo | cap_ref | req_ref | Justificación |
|------|--------:|--------:|---------------|
| Colegio | 500 | 3 EES | Cubre turno entrada (clasificación + admisión), zona estabilización y área verde (1 equipo cada una). Espacios compactos permiten supervisión cruzada. |
| Estadio | 3,000 | 6 EES | Superficie dispersa + carpas de campaña: requiere al menos 2 equipos por turno en zonas rojo/amarillo, más 1 equipo verde y 1 equipo de refuerzo rotativo. |

### Ejemplos numéricos

| Tipo | cap_j | req_j |
|------|------:|------:|
| Colegio | 400 | 3 |
| Colegio | 800 | 5 |
| Colegio | 1,500 | 9 |
| Estadio | 2,000 | 5 |
| Estadio | 4,000 | 8 |

### Fuentes

- **WHO Emergency Medical Teams: Minimum Technical Standards and Recommendations
  for Rehabilitation (Blue Book, 2021)**: EMT Type-1 Fixed mínimo 11 personal médico
  por establecimiento → equivalente a ~3 EES para un turno diurno de 8h.
- **MINSAL Norma Técnica N°17 de Atención Prehospitalaria**: SAMU móvil avanzado
  exige conductor + paramédico + profesional interventor + médico interventor (4 personas
  = 1 EES). Para operación 24/7: mínimo 3 turnos = 3 EES en colegios.
- **Estonian EMT (WHO-classified Type-1 Fixed)**: dotación mínima de 3 médicos +
  6 enfermeras para 5 carpas de triaje → ~3 EES como mínimo operativo.
- Fuente directa: *research_claude.md* y *research_gemini.md*.

---

## H_t — Equipos disponibles por día (curva de movilización)

La disponibilidad de EES crece a lo largo de los 7 días a medida que se suman
refuerzos de distintas fuentes.

### Escenarios disponibles

| Día | escenario=1 (conservador) | escenario=2 (intermedio, default) | escenario=3 (optimista) |
|-----|:-------------------------:|:--------------------------------:|:-----------------------:|
| 1 | 8 | 10 | 12 |
| 2 | 12 | 17 | 22 |
| 3 | 18 | 29 | 40 |
| 4 | 24 | 41 | 58 |
| 5 | 26 | 49 | 72 |
| 6 | 28 | 55 | 82 |
| 7 | 28 | 59 | 90 |

*(escenario=2 = promedio redondeado entre escenario=1 y escenario=3)*

### Desglose de fuentes por ola de movilización (escenario=3, Gemini)

| Día | H_t | Contingente |
|-----|----:|-------------|
| 1 | 12 | SAMU local activo + brigadas voluntarias Valparaíso/Viña |
| 2 | 22 | + Personal CESFAM y SAPU de comunas costeras |
| 3 | 40 | + SAMU Metropolitano + regiones colindantes (MINSAL) |
| 4 | 58 | + Sanidad FF.AA. + Cruz Roja Chilena (COGRID) |
| 5 | 72 | + EMT-1 internacionales OPS/OMS acreditados |
| 6 | 82 | + Relevos clínicos nacionales de zonas extremas |
| 7 | 90 | Capacidad máxima regional bajo decreto de catástrofe |

### Justificación del escenario=1 (Claude, conservador)

Considera únicamente movilización de EMT internacionales y personal de salud local
no afectado por el sismo. Días 1–2 reducidos por: (a) personal que debe atender a
sus propias familias antes de reportarse, (b) colapso de vías de acceso, (c) daños
en base SAMU Valparaíso (caso histórico: inutilización post-27F por colapso parcial).

### Fuentes

- **SAMU Litoral (Valparaíso)**: 5 ambulancias 24/7 → ~3 EES disponibles en día 1.
- **SAMU SSVQ (Viña–Quillota)**: 4 bases regionales → ~5–6 EES.
- **López Tagle & Santana (2011)**, *Rev Panam Salud Pública* 30(2):160–6: curvas de
  movilización post-27F; SAMUR-Madrid llegó al día 3 (9 sanitarios = ~2 EES); pico
  de refuerzos días 3–7.
- **EMT Américas / OPS**: protocolo de despliegue de EMT Type-1 en 48–72h post-declaración.
- **Asociación de Enfermeras Hospital Gustavo Fricke (G5noticias, 30-sep-2025)**:
  solicitan 4 enfermeras/turno en SAMU Viña (actualmente 3) → H_1 puede subir a ~10 si
  demanda es satisfecha antes del evento.
- Fuente directa: *research_claude.md* y *research_gemini.md*.

---

## MaxC_t — Número máximo de PMAs activos simultáneos

### Escenarios disponibles

| Día | escenario=1 (conservador) | escenario=2 (intermedio, default) | escenario=3 (optimista) |
|-----|:-------------------------:|:--------------------------------:|:-----------------------:|
| 1 | 4 | 2 | 2 |
| 2 | 5 | 4 | 4 |
| 3 | 7 | 6 | 6 |
| 4 | 8 | 8 | 10 |
| 5 | 9 | 10 | 14 |
| 6 | 10 | 10 | 16 |
| 7 | 10 | 10 | 16 |

*(El escenario=2 toma Gemini para días 1–2, más conservador por colapso de comunicaciones;
y Claude para días 5–7, ya que 16 PMAs excede la capacidad realista de supervisión de
la SEREMI de Salud Valparaíso.)*

### Justificación

El límite de PMAs activos refleja la capacidad de **comando y control** de la autoridad
sanitaria, no el número de recintos disponibles.

- **Días 1–2**: colapso de energía eléctrica, antenas móviles y central de despacho SAMU
  (radiofrecuencia VHF básica como único canal). "Span of control" máximo: 2–4 nodos.
- **Días 3–5**: despliegue satelital de SENAPRED, corredor bioceánico habilitado por MOP,
  COE-Salud regional activo → capacidad sube a 6–10 PMAs.
- **Días 6–7**: logística regularizada (CENABAST Valparaíso), conectividad total
  rural → plateau de 10–16 PMAs según escenario.

### Fuentes

- **SENAPRED (El Mostrador, 20-feb-2024)**: "cada dirección regional funciona con 18
  funcionarios" y "cerca de 6 ó 7 funcionarios del Senapred en terreno habitualmente".
  → MaxC_1 = 2–4 es consistente con esta dotación.
- **Informe Ejecutivo Auditoría ONEMI (2010, post-27F)**: "el comando y la coordinación
  logística colapsaron más allá de 4–5 operaciones de campo simultáneas el día 1."
- Fuente directa: *research_claude.md* y *research_gemini.md*.

---

## ratio_g — Pacientes atendidos por EES por día

### Escenarios disponibles

| Escenario | ratio_leve | ratio_moderado | Base |
|-----------|:----------:|:--------------:|------|
| 1 (conservador) | 25 | 10 | WHO EMT Type-1 throughput (Claude) |
| 2 (intermedio, default) | 30 | 12 | Compromiso conservador |
| 3 (optimista) | 96 | 36 | Fórmula Gemini (24h continuas) |

### Fórmula Gemini (escenario=3)

```
ratio_leve    = 8 pac/h × 24 h / 2 (factor_fatiga) = 96 pac/EES/día
ratio_moderado = 3 pac/h × 24 h / 2 (factor_fatiga) = 36 pac/EES/día
```

*Asume operación continua de 24h con factor de pérdida de eficiencia del 50%
por fatiga + tiempos administrativos. Velocidad base: 8 pac/h (leve = 10–15 min
atención efectiva) y 3 pac/h (moderado = 25–30 min de SVA).*

### Fórmula WHO (escenario=1)

WHO EMT Type-1 Fixed: ≥100 pacientes ambulatorios/día con 11 personal médico.
Equivalente a ~9 pacientes/persona-día → con EES de 4 personas: ~36/día.
Pero este es el mínimo WHO, con mezcla de todos los niveles de gravedad.
Para solo leves (el mayor volumen): ~25/EES/día. Para moderados: ~10/EES/día.

### Evidencia empírica

- **Singapore EMT en Myanmar 2025** (Prehospital and Disaster Medicine, PMC12818970):
  1,803 pacientes en 8 días con un EMT Type-1 Fixed → **~225 pacientes/día**
  por todo el establecimiento. Con ~11 personal médico: ~20 pacientes/persona-día.
- **Brigada Henry Reeve en Chile, 27-F 2010** (Cubadebate, 21-nov-2010):
  79,137 pacientes en ~8 meses → **~152 pacientes/día** por hospital, con ~78 personal
  = ~2 pacientes/persona-día (pero incluye cirugías, largo plazo).
- **Yushu 2010, China** (MDPI IJERPH 2015, PMC4690927): 12,128 heridos en 4 días
  con ~15 equipos → **~202 pacientes/equipo en 4 días = ~50/equipo/día**.

### Fuentes

- *WHO Emergency Medical Teams Blue Book (2021)*
- *research_claude.md* (WHO EMT throughput, START triage literature)
- *research_gemini.md* (MINSAL rendimientos urgencia, SVA timing)
- StatPearls "EMS Mass Casualty Triage" (NCBI Bookshelf)
- Maryland MIEMSS START triage protocol

---

## Bibliografía

Cubadebate. (2010, 21 de noviembre). Regresa a Cuba la Brigada Henry Reeve de misión en Chile. http://www.cubadebate.cu/especiales/2010/11/21/regresa-a-cuba-brigada-henry-reeve-que-presto-servicios-en-chile/
> 79,137 pacientes en 8 meses con ~78 personal (~152 pac/hospital/día). Contexto empírico para ratio_g.

Departamento de Gestión del Riesgo en Emergencias y Desastres, MINSAL. (2024). *Protocolo de respuesta a emergencias de salud: Funciones y capacidad operativa*. Gobierno de Chile.
> Dotaciones SAMU Valparaíso (~3 EES día 1) y capacidad de bases costeras. Base para H_t.

Dirección Nacional de SAMU, MINSAL. (2003). *Norma Técnica N°17: Atención Prehospitalaria*. Gobierno de Chile.
> Dotación mínima SAMU móvil avanzado: 4 personas (1 médico + 1 enfermera + 2 TENS = 1 EES). Define la unidad base del modelo.

El Mostrador. (2024, 20 de febrero). Las grietas del Senapred: presupuesto exiguo y falta de personal. https://www.elmostrador.cl/noticias/pais/2024/02/20/las-grietas-del-senapred-presupuesto-exiguo-y-falta-de-personal/
> «Cada dirección regional funciona con 18 funcionarios» y «cerca de 6 ó 7 en terreno habitualmente». Base para MaxC_t.

G5Noticias.cl. (2025, 30 de septiembre). En alerta: funcionarios del SAMU de Viña del Mar exigen dotación segura en enfermería. https://g5noticias.cl/2025/09/30/en-alerta-funcionarios-del-samu-de-vina-del-mar-exigen-dotacion-segura-en-enfermeria-para-garantizar-la-vida-y-seguridad-de-la-poblacion/
> Dotación actual SAMU Viña del Mar: 3 enfermeras/turno (demandan 4). Relevante para cota inferior de H_1.

López-Tagle, R., & Santana, J. (2011). Respuesta del sistema de salud a los desastres: Lecciones del terremoto de Chile de 2010. *Revista Panamericana de Salud Pública*, 30(2), 160–166. https://doi.org/10.1590/S1020-49892011000800008
> Curvas de movilización post-27F: SAMUR-Madrid llegó al día 3 (9 sanitarios ≈ 2 EES); pico refuerzos días 3–7. Base principal para forma de H_t.

Ministerio de Salud, Chile. (2015). *Servicio de Salud Valparaíso – San Antonio: Perfil institucional*. https://www.ochisap.cl/wp-content/uploads/2022/05/6-SS-Valpara%EF%BF%BDso-SA.pdf
> Red regional: 3 hospitales alta complejidad + 6 SAPU + 13 consultorios. Base para estimación de H_t días 2–3.

Ochi, S., Kato, S., Kobayashi, K., & Wakai, S. (2015). Emergency medical response in the 2010 Yushu earthquake. *International Journal of Environmental Research and Public Health*, 12(12), 15831–15845. https://doi.org/10.3390/ijerph121215016
> 12,128 heridos en 4 días con ~15 equipos (~50 pac/equipo/día). Base empírica para ratio_g.

Oficina Nacional de Emergencia. (2010). *Informe ejecutivo de la auditoría de la Oficina Nacional de Emergencia del Ministerio del Interior*. Gobierno de Chile.
> Coordinación logística colapsó más allá de 4–5 operaciones simultáneas el día 1. Base para MaxC_1.

Organización Panamericana de la Salud (OPS). (2021). *Equipos Médicos de Emergencia (EME): Clasificación y estándares de desempeño*. OMS/OPS. https://www.paho.org/en/health-emergencies/emergency-medical-teams
> Protocolo de despliegue EMT Type-1 en 48–72h post-declaración. Base para H_t días 5–7 (escenario=3).

Singapore Emergency Medical Team. (2025). Field report of the Singapore Emergency Medical Team deployment following the 2025 Myanmar earthquake. *Prehospital and Disaster Medicine*. PMC12818970.
> 1,803 pacientes en 8 días (~225/día) con EMT Type-1 Fixed. Base empírica para ratio_g (escenario=3).

World Health Organization (WHO). (2021). *Emergency Medical Teams: Minimum standards and recommendations for excellence. WHO Blue Book*. https://www.who.int/publications/i/item/9789240012363
> EMT Type-1 Fixed: ≥100 pac/día con mínimo 11 personal médico; Estonian EMT: 3 médicos + 6 enfermeras mínimo. Base para req_j y ratio_g (escenario=1).
