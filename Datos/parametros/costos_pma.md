# Costos de Apertura y Operación de PMAs — f_j y o_j

Parámetros de costo del modelo de optimización de centros de triaje post-terremoto
en la Región de Valparaíso (Mw ≥ 8.0, horizonte 7 días).

---

## Definición

| Parámetro | Significado |
|-----------|-------------|
| `f_j` | Costo fijo de habilitación del recinto j como Puesto Médico Avanzado (PMA): equipamiento de triaje, señalética, redes eléctricas de emergencia, gestión de residuos clínicos |
| `o_j` | Costo operativo diario del PMA j: insumos médicos consumibles, combustible, raciones de personal, gestión de RPBI |

---

## Fórmula de cálculo (escala con capacidad)

Los costos escalan linealmente con `cap_j` (capacidad de personas del recinto).
Los valores de referencia se derivan de la investigación para recintos típicos:

```
REFERENCIA_COLEGIO_CAP  = 500   personas
REFERENCIA_ESTADIO_CAP  = 3000  personas

F_POR_PERSONA_COLEGIO   = 22_500_000 / 500   = 45_000  CLP / persona
F_POR_PERSONA_ESTADIO   = 58_000_000 / 3000  = 19_333  CLP / persona

O_POR_PERSONA_COLEGIO   =  2_800_000 / 500   =  5_600  CLP / persona / día
O_POR_PERSONA_ESTADIO   =  6_200_000 / 3000  =  2_067  CLP / persona / día

f_j = round(F_POR_PERSONA_tipo × cap_j)
o_j = round(O_POR_PERSONA_tipo × cap_j)
```

**Economías de escala**: los estadios tienen menor costo por persona de capacidad
porque su infraestructura abierta ya existe (graderías, explanadas). Los colegios
requieren más trabajo de habilitación interior (subdivisión de salas, redes eléctricas
de aulas, manejo de residuos en espacios cerrados).

### Ejemplos numéricos

| Tipo | cap_j | f_j (CLP) | o_j (CLP/día) |
|------|------:|----------:|---------------:|
| Colegio | 500 | 22,500,000 | 2,800,000 |
| Colegio | 800 | 36,000,000 | 4,480,000 |
| Colegio | 1,200 | 54,000,000 | 6,720,000 |
| Estadio | 2,000 | 38,667,000 | 4,133,000 |
| Estadio | 3,000 | 58,000,000 | 6,200,000 |
| Estadio | 5,000 | 96,667,000 | 10,333,000 |

---

## Fuentes y justificación

### Colegio — f_j de referencia: CLP 22,500,000

- **Extrapolación licitaciones GORE Chile (COVID-19, 2020)**: el Gobierno Regional
  financió hospitales modulares de campaña anexos a colegios a un costo de
  CLP ~487,000,000 por estructura de 396 m² y 40 camas de cuidados básicos.
  Un PMA de triaje en un colegio (sin camas, solo estabilización) se estima
  en ~5% de ese costo: ~CLP 24,000,000. Se ajusta a la baja por tratarse de
  habilitación funcional de espacios existentes (no construcción modular).
- **Kits de equipamiento de triaje (Proyecto Esfera / OPS)**: un kit de triaje
  START para 200 pacientes ronda USD 8,000–12,000 (~CLP 8–12M). Para 500 pacientes
  con señalética y red de agua segura: CLP ~15M en insumos.
- **Valor central adoptado**: CLP 22,500,000. Fuente: *research_gemini.md*.

### Estadio — f_j de referencia: CLP 58,000,000

- **Carpas de campaña del Ejército de Chile y módulos OPS**: una carpa
  autoinflable con generador diésel de 25–50 kVA y sistema de climatización
  se cotiza entre EUR 15,000–40,000 (~CLP 16–44M). Para sectorizar un estadio
  en 3 zonas de triaje (rojo/amarillo/verde) se requieren 2–3 carpas: CLP ~48–80M.
- **Iluminación perimetral y accesos para ambulancias**: CLP ~5–10M adicionales.
- **Valor central adoptado**: CLP 58,000,000. Fuente: *research_gemini.md*.

### Colegio — o_j de referencia: CLP 2,800,000/día

Desglose para flujo estimado de 200 pacientes/día:

| Componente | CLP/día |
|------------|--------:|
| Fármacos e insumos básicos (kits trauma, analgésicos, sutura) | 1,100,000 |
| Personal clínico: salario base SAMU + horas extra catástrofe | 1,200,000 |
| Logística, combustible, agua potable, RPBI | 500,000 |
| **Total** | **2,800,000** |

Referencia de sueldo: médico SAMU Valparaíso ~CLP 2,052,000/mes en turno ordinario
(Escala Servicio Civil 2024). En catástrofe, turnos de 12–24h duplican el costo diario
por profesional. Fuente: *research_gemini.md*.

### Estadio — o_j de referencia: CLP 6,200,000/día

Desglose para flujo estimado de 500 pacientes/día:

| Componente | CLP/día |
|------------|--------:|
| Insumos de soporte vital avanzado (SVA, fluidoterapia, oxígeno) | 3,200,000 |
| Personal: rotación continua + TENS | 1,800,000 |
| Soporte operativo carpas (combustible generadores, mantenimiento) | 1,200,000 |
| **Total** | **6,200,000** |

Fuente: *research_gemini.md*.

### Cota superior de referencia (Claude)

*research_claude.md* reporta f_j ≈ CLP 60M (cualquier tipo) basado en UK-Med Type-1
Field Hospital (£250,000 ~CLP 300M) escalado a PMA básico de triaje (~20% del costo
de un hospital de campaña completo). Esta cifra es la **cota superior** del modelo.
El valor adoptado de Gemini (22.5M/58M) es más conservador y más ajustado a la
realidad chilena donde los PMAs reutilizan infraestructura pública existente.

---

## Nivel de confianza y recomendaciones

| Parámetro | Confianza | Nota |
|-----------|-----------|------|
| `f_colegio` | Media | Extrapolación. Validar con licitaciones ChileCompra (SENAPRED 2014–2024) |
| `f_estadio` | Media | Extrapolación de precios comerciales carpas militares/OPS |
| `o_colegio` | Media–Alta | Anclado en remuneraciones SAMU Chile (dato directo) |
| `o_estadio` | Media | Extrapolación por escala desde colegio |

> Para mejorar la confianza: consultar en MercadoPublico los códigos de adjudicación
> de SENAPRED entre 2010–2024 bajo categorías "carpa emergencia", "kit triaje",
> "puesto médico avanzado".

---

## Bibliografía

[research_gemini] — fuente principal para f_j y o_j diferenciados por tipo de recinto.
Incluye: extrapolación de licitaciones GORE COVID-19 (hospitales modulares ~CLP 487M/40 camas),
precios de carpas Ejército de Chile y módulos OPS (EUR 15,000–40,000 por carpa), remuneraciones
SAMU Valparaíso (médico ~CLP 2,052,000/mes base 2024), e insumos médicos de triaje (kits MINSAL).

[research_claude] — fuente para la cota superior de f_j (~CLP 60M por PMA) basada en UK-Med
Type-1 Field Hospital (£250,000 de despliegue) y costos IFRC ERU Haití 2010 (USD 8,000–15,000/día).
También reporta datos de la Brigada Henry Reeve en Chile post-27F (~USD 200,000–210,000/hospital/mes).
