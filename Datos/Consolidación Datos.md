# Catastro Consolidado: Modelo de Optimización de Centros de Triaje Post-Sismo
## Región de Valparaíso, Chile | Censo 2024 + Datos de Horizonte de Planificación 7 días

**Propósito:** Insumos para modelo de programación lineal entera mixta que optimiza localización y operación de centros de triaje en emergencias sísmicas (ICS1113-Optimización, Grupo 10, PUC, 2026).

---

## 📋 Tabla de Contenidos
1. [Población por Comuna (Censo 2024)](#1-población-por-comuna)
2. [Infraestructura Deportiva y Centros Potenciales](#2-infraestructura-deportiva)
3. [Riesgo Sísmico y Tsunami](#3-riesgo-sísmico-y-tsunami)
4. [Red Hospitalaria](#4-red-hospitalaria)
5. [Dinámicas de Evacuación y Cobertura](#5-dinámicas-de-evacuación)
6. [Demanda Post-Sismo](#6-demanda-post-sismo)
7. [Datos a Calcular (Matriz de Entrada)](#7-datos-a-calcular-matriz-de-entrada)
8. [Datos Pendientes de Investigación](#8-datos-pendientes-de-investigación)

---

## 1. Población por Comuna

### Datos Confiables: Censo 2024 (INE)

La Región de Valparaíso cuenta con aproximadamente **1.896.053 habitantes distribuidos en 38 comunas** según los resultados oficiales del Censo 2024 (INE, 2025)[^1], con una alta concentración en zonas metropolitanas costeras. Para el año 2026 se proyecta una población de **2.054.246 habitantes** según estimaciones del INE.

[^1]: INE (2025). "Resultados Censo 2024: Región de Valparaíso." Instituto Nacional de Estadísticas. Presentación regional de resultados del Censo de Población y Vivienda 2024.


#### Indicadores Demográficos Regionales (Censo 2024)
- **Índice de Envejecimiento:** 98.6 (98.6 adultos >65 por cada 100 menores de 14) — **más alto del país**
- **Proporción de mayores de 65 años:** 16.6% 
- **Proporción de menores de 14 años:** 16.8%
- **Crítico para evacuación:** 23.7% de la población será >60 años en 2026 (INE, 2025)[^2]
- **Vulnerabilidad diferenciada:** Comunas como El Tabo (IE≈178) y Algarrobo (IE≈166) muestran envejecimiento crítico por dinámica de segunda vivienda y retiro, impactando significativamente en velocidades de evacuación peatonal[^3]

[^2]: Estimación based on proyecciones demográficas incluidas en presentación INE Censo 2024.
[^3]: Inzunza, S. & Martínez, C. (2024). "Método CRET: Una propuesta para incorporar áreas de riesgo concatenado sismo-tsunami en la planificación territorial chilena." Revista EURE, 51(152):1–33.

---

## 2. Infraestructura Deportiva y Centros Potenciales

### 2.1 Recintos Potenciales como Zonas de Triaje

Tras filtrado por operatividad y confiabilidad de datos, se cuenta con **18 recintos verificados** operativos y ubicados en comunas estratégicas.

#### Principales Recintos Operativos

| Recinto | Comuna | Tipo | Capacidad | Coordenadas | Estado | Notas |
|---------|--------|------|-----------|-------------|--------|-------|
| **Estadio Sausalito** | Viña del Mar | Estadio | 18,002 | -33.0204, -71.5378 | Operativo | Casa de Everton; Copa 1962 |
| **Estadio Elías Figueroa Brander** | Valparaíso | Estadio | 20,575 | -33.0220, -71.6400 | Operativo | Casa Santiago Wanderers |
| **Gimnasio Polideportivo Viña del Mar** | Viña del Mar | Polideportivo | 3,371 | -33.0158, -71.5353 | Operativo | Sede Panamericanos 2023 |
| **Estadio O'Higgins** | Valparaíso | Estadio | 4,000 | -33.0350, -71.6250 | Operativo | Complejo Bernardo O'Higgins |
| **Estadio Lucio Fariña Fernández** | Quillota | Estadio | 7,680 | -32.8875, -71.2428 | Operativo | Casa San Luis Quillota |
| **Estadio Ítalo Composto Scarpatti** | Villa Alemana | Estadio | 3,500 | -33.0336, -71.3719 | Operativo | Renovado 2012 |
| **Estadio Nicolás Chahuán Nazar** | La Calera | Estadio | 9,200 | -32.7500, -71.2167 | Operativo | Casa Unión La Calera |
| **Estadio Javier Muñoz Delgado** | San Felipe | Estadio | 10,000 | -32.8470, -70.7150 | Operativo | Casa Unión San Felipe |
| **Estadio Regional Los Andes** | Los Andes | Estadio | 3,300 | -32.8333, -70.6167 | Operativo | Casa Trasandino |
| **Estadio Atlético Municipal Concón** | Concón | Estadio | 3,000 | -33.0333, -71.4167 | Operativo | Césped sintético 2010 |

### 2.2 Problemas Críticos Identificados

#### Vulnerabilidad por Cota 30 (Riesgo de Tsunami)
Comunas costeras con infraestructura bajo cota de inundación de 30 m s.n.m. (Servicio Hidrográfico y Oceanográfico de la Armada - SHOA):
- Valparaíso
- Viña del Mar
- Concón
- Quintero
- Puchuncaví
- Papudo
- Zapallar
- Algarrobo
- El Quisco
- El Tabo
- Cartagena
- San Antonio
- Santo Domingo
- Juan Fernández
- Isla de Pascua

**Consecuencia:** Estos recintos NO pueden operar como zonas de refugio post-tsunami a pesar de ser centros de albergue teóricos en planes de emergencia.

---

## 3. Riesgo Sísmico y Tsunami

### 3.1 Amenaza Histórica y Proyectada

#### Evento de Referencia Histórico
- **Terremoto Valparaíso 1730:** Mw 8.5–9.0, zona de ruptura ~575 km (La Serena a Chillán)
- **Periodo de retorno esperado:** ~200–300 años

#### Evento Contemporáneo de Referencia
- **27 de Febrero de 2010 (27F):** Mw 8.8
  - Aceleración horizontal máxima: 0.928 g
  - Intensidad Mercalli: IX
  - Víctimas fatales: 521
  - Daño en infraestructura de salud: 71% de edificios afectados
  - Pérdidas estimadas: USD 30,000 millones

### 3.2 Vulnerabilidad Estructural de Viviendas

**Tipología constructiva nacional (53% mampostería no reforzada, 34% madera, 8% hormigón armado):**
- 99.5% viviendas unifamiliares de baja altura
- 0.5% edificios en altura

**Riesgo de colapso estructural:**
- Mampostería no reforzada: **riesgo crítico**
- Adobe: **riesgo crítico** (falla por esfuerzo de corte)
- Autoconstrucciones informales en cerros de Valparaíso: **riesgo crítico**

**Edificaciones escolares e institucionales:**
- Muchas con >70 años de antigüedad
- Incumplen norma NCh433 Of.96 (diseño sismorresistente)
- Vulnerabilidad FEMA P-154: clasificadas con probabilidad alta de colapso en Mercalli ≥VII–VIII

### 3.3 Tiempo de Arribo de Tsunami

**Escenario de tsunami de campo cercano (post-sismo Mw ≥8.5):**
- **Tiempo de arribo de primera ola destructiva:** 14 minutos (Valparaíso, Viña del Mar)
- **Penetración horizontal:** Hasta 4 km en Viña del Mar (Estero Marga Marga); ~1 km en Valparaíso
- **Profundidad de inundación esperada:** Hasta 6 m en sectores bajos (ej. Casino Viña del Mar)

---

## 4. Red Hospitalaria

INVESTIGAR

---

## 5. Dinámicas de Evacuación

### 5.1 Parámetros Cinéticos de Evacuación Peatonal

| Perfil | Tipo de Terreno | Velocidad (m/s) | Velocidad (km/h) | Distancia en 14 min |
|--------|-----------------|:---------------:|:----------------:|--------------------:|
| **Adulto sano** | Pendiente <5.6° | 1.10–1.24 | 3.96–4.48 | 0.93–1.05 km |
| **Adulto sano** | Pendiente 5.6°–8.0° | 0.91 | 3.29 | 0.77 km |
| **Movilidad reducida** | Terreno plano | 0.90 | 3.24 | 0.76 km |
| **Peatón en estrés** | Densidad baja | ~1.5 a 2.0× tiempo nominal | Variable | Reducida 50%+ |

### 5.2 Brecha Crítica de Evacuación

**Escenario Población Vergara (Viña del Mar - densidad alta, terreno plano):**
- Distancia a zona segura (Cota ≥30 m): ~1.5–2.2 km
- Tiempo de evacuación completo: **15–22 minutos**
- Tiempo de arribo de tsunami: **14 minutos**
- **Resultado: "Margen de supervivencia negativo"** → Evacuación horizontal insuficiente

### 5.3 Estrategia de Evacuación Vertical

**Propuesta de refugios en altura (PUC / USM):**
- Edificios de hormigón armado sismorresistente
- Refugio a partir de 5to piso
- Resistencia a carga inercial (sismo) + empuje hidrodinámico (tsunami)
- Reduce significativamente tiempos requeridos
- **Crítico para 23.7% de población >60 años**

### 5.4 Interferencia de Infraestructura Vial

#### Estero Marga Marga (Viña del Mar)
- Canal hidrodinámico de baja resistencia
- Permite penetración de agua hasta 4 km tierra adentro
- **Colapso de puentes = interrupción de rutas de evacuación**
- Atrapa población en zona de alta energía sin escape

#### Daño Típico Post-Sismo en Vías
- Asentamiento diferencial en accesos de puentes: 7–10 cm
- Restricción de velocidad a 20 km/h (o cierre total)
- Desprendimiento de taludes: obstrucción física

#### Efecto Socio-Vial
- Uso masivo de automóviles: congestión crítica
- Velocidad promedio post-sismo: **<10 km/h** (parálisis vial)
- **Directiva actual:** Evacuación estrictamente peatonal para evitar parálisis

---

## 6. Demanda Post-Sismo

El modelo estima la demanda de pacientes (D_{i,t,g}) por zona, día y gravedad usando la metodología HAZUS-MH adaptada para construcciones vulnerables tipo D-E predominantes en cerros de Valparaíso[^5]. La distribución temporal de llegada y tasas de heridos se basan en estudios post-27F y literatura internacional.

[^5]: FEMA (2003). "HAZUS-MH 2.1 Technical Manual." FEMA 439. Multi-Hazard Loss Estimation Methodology for Earthquakes, Floods, and Hurricanes. Tasas adaptadas a viviendas de mampostería no reforzada (tipo D-E), donde heridos pueden aumentar hasta un orden de magnitud bajo intensidades elevadas (Jaiswal & Wald, 2010).

| Fase | Llegadas | Acumulado | Características |
|------|----------|-----------|-----------------|
| **Primeras 24 h** | ~50% del total | 50% | Fase de máxima demanda aguda |
| **24–72 h** | Variable (mayoría restante) | 80%–90% | Afluencia sostenida |
| **72 h – 7 días** | Decreciente | ~100% | Estabilización hacia cero |

**Modelamiento:** Distribución Poisson no homogénea

### 6.2 Tipos de Lesionados Esperados

**Para sismo Mw 8.0–8.8:**
- Trauma directo (aplastamiento, heridas)
- Fracturas múltiples
- Eventos isquémicos (estrés agudo)
- Síndrome de aplastamiento (crush syndrome)
- Quemaduras (por derrumbes, incendios)
- Trastornos psicológicos agudos

**Variación espacial:** Función de tipología estructural + distancia epicentral

### 6.3 Aumento de Demanda vs. Capacidad Normal

| Escenario | Múltiplo vs. Normal | Impacto | Tiempo Recuperación |
|-----------|-------------------:|---------|--------------------:|
| Conservador | 1.4× | Congestión moderada | 1–2 días |
| Realista | 1.8×–2.3× | Saturación extrema | 5–10 días |
| Catastrófico | 3×+ | Colapso de servicios | >14 días |

**Hallazgo crítico:** Pequeños aumentos (1.4–1.9×) de pacientes no urgentes duplican índice de congestión

### 6.4 Acceso Hospitalario

**Transporte post-sismo (caso urbano):**
| Contexto | Tenencia Auto | No-críticos en 45 min | Mejora con ambulancias |
|----------|:-------------:|:---------------------:|:----------------------:|
| Sector alto | 57% | 24% | +50% (duplica ambulancias) |
| Sector bajo | 18% | 6% | Similar limitación |
| Con coordinación vecinal | N/A | >96% | Alcanza máximo |

---

## 7. Datos a Calcular (Matriz de Entrada del Modelo)

### 7.1 Demanda Diaria por Comuna y Tipo de Paciente: D_{i,t,g}

**Necesario calcular:** Matriz de demanda de 38 comunas × 7 días × 2 tipos (leve, moderado) usando:
- Tasas de heridos según Intensidad Mercalli (0.5–200 heridos por 1.000 hab.)
- Escenario: Mw 8.5–9.0 (histórico 1730) → MMI IX–X en zona epicentral
- Población por comuna (Censo 2024)
- Distribución temporal: curva Poisson no homogénea (50% primeras 24h, 80% en 72h, ~100% en 7 días)
- Ajuste por vulnerabilidad: aumentar tasas en zonas de construcción tipo D-E (cerros Valparaíso, barrios informales)

### 7.2 Matriz Origen-Destino de Tiempos de Viaje: T^{viaje}_{i,j} y T^{viaje}_{i,k}

**Necesario calcular:** 
- Tiempos desde cada zona i (comuna) a cada recinto j (triaje) y hospital k
- Considerar daño post-sismo: velocidades reducidas a 3–5 km/h en vías urbanas (vs. 10–20 km/h normal)
- Parámetro crítico: T_{max} = 30 minutos (limitación de accesibilidad post-desastre)
- Generar matriz de cobertura binaria: A_{i,j} = 1 si tiempo ≤ 30 min, 0 e.o.c.

### 7.3 Parámetros de Productividad por Tipo de Paciente: ratio_g

**Necesario estimar:**
- Pacientes leve por equipo equivalente/día: ratio_{leve} (ej. 8–12 pacientes)
- Pacientes moderado por equipo equivalente/día: ratio_{moderado} (ej. 3–5 pacientes, requiere más tiempo)
- Base: tiempos promedio de atención en contextos de emergencia (SHORT/START triage ≈ 60 seg/paciente)

### 7.4 Capacidad de Recintos: Cap_j y Capacidad Hospitalaria: Cap_{k,t}

**Para centros de triaje j:**
- Cap_j = capacidad física (del CSV infraestructura)
- Verificar disponibilidad de servicios básicos (agua, electricidad, sanitarios) post-sismo

**Para hospitales k:**
- Cap_{k,t} = capacidad operativa el día t (considerando daño del 27F: ~9.3% pérdida inmediata)
- Modelo conservador: Cap_{k,1} = 0.95 × capacidad normal; Cap_{k,t>1} = recuperación gradual a 100% en 5–7 días

### 7.5 Costos de Activación y Operación: f_j y o_j

**Necesario estimar basado en:**
- Costos de habilitación: equipamiento médico básico, personal inicial (f_j)
- Costos diarios de operación: energía, agua, personal, logística (o_j)
- Modelo simplificado: f_j ∝ capacidad del recinto; o_j = función del tamaño y servicios disponibles

### 7.6 Disponibilidad de Personal Médico: H_t

**Necesario investigar:**
- Pool total de equipos médicos equivalentes disponibles en la región el día t
- Distribución: post-sismo se asume personal parcialmente desplazado (~20% pérdida día 1, recuperación gradual)
- H_1 = estimado conservador; H_t = recuperación gradual

---

## 8. Datos Pendientes de Investigación

### 8.1 Infraestructura Deportiva
- [ ] **Exactitud de coordenadas GPS** para todos los recintos (VALIDAR)
- [ ] **Capacidades actuales 2025–2026** de gimnasios menores (VALIDAR)
- [ ] **Certificación de Cota 30 SHOA** para todos los recintos costeros (VALIDAR)
- [ ] **Disponibilidad de servicios básicos** (agua, electricidad, sanitarios) en cada recinto post-sismo
- [ ] **Presupuestos municipales 2025–2026** para operación de recintos

### 8.2 Población y Demanda
- [ ] **Actualización de población flotante/turística** en zonas costeras (Viña del Mar, Isla de Pascua)
- [ ] **Desagregación espacial de vulnerabilidad** (% de construcción tipo D-E por comuna) para ajuste de tasas HAZUS-MH
- [ ] **Curvas de demanda temporal específicas para Valparaíso** (si existen estudios post-27F desagregados por comuna)

### 8.3 Red Hospitalaria
- [ ] **Hospitales y centros de salud de la región**
- [ ] **Capacidad exacta de UTI/camas críticas** por hospital 
- [ ] **Daño esperado post-sismo** en hospitales (adaptar del 27F con función de distancia epicentral)
- [ ] **Capacidad de hospitales privados** para reconversión post-desastre (clínicas mayores región)
- [ ] **Protocolos actualizados 2025 de triage** (referencias disponibles hasta 2021)

### 8.4 Evacuación, Movilidad y Cobertura
- [ ] **Matriz O-D de tiempos de viaje 38×18 recintos** (VALIDAR GPS de recintos primero)
- [ ] **Tiempo real de evacuación** desde cada sector a centros de triaje (estudios de agent-based modeling)
- [ ] **Velocidad post-sismo en Ruta 5, Ruta 68** y vías urbanas principales
- [ ] **Análisis de daño en puentes críticos** (Estero Marga Marga, accesos costeros)

### 8.5 Demanda Específica de Triaje
- [ ] **Tasa de lesionados esperada específica para Valparaíso** con distribución MMI (adaptar HAZUS-MH)
- [ ] **Proporción real leve:moderado:grave** observada en hospitales 27F desagregada por intensidad
- [ ] **Curvas de demanda temporal** por tipo de paciente (si graves llegan primero que leves, afecta recursos día 1)
- [ ] **Coeficientes de recuperación** de capacidad hospitalaria post-sismo (velocidad de reparación y habilitación)

### 8.6 Parámetros Operacionales del Modelo
- [ ] **Tiempo máximo de permanencia mínima** L para un centro abierto (política de decisión)
- [ ] **Máximo de centros activos simultáneamente** MaxC_t (capacidad de supervisión regional)
- [ ] **Presupuesto total disponible** Pres (CLP, 2026)
- [ ] **Pesos de pacientes** P_g para función objetivo (relación costo-beneficio: grave vs. leve)
- [ ] **Requisito mínimo de personal** req_j por recinto (equipo base para funcionamiento)

---

## 📚 Referencias y Citas

### Referencias Bibliográficas Principales

Castro, S., Poulos, A., Herrera, J., & De La Llera, J. (2019). "Modeling the Impact of Earthquake-Induced Debris on Tsunami Evacuation Times of Coastal Cities." *Earthquake Spectra*, 35, 137–158. https://doi.org/10.1193/101917eqs218m

Flores, C., Lee, H., & Mas, E. (2024). "Understanding Tsunami Evacuation via a Social Force Model While Considering Stress Levels Using Agent-Based Modelling." *Sustainability*, 16(10). https://doi.org/10.3390/su16104307

FEMA (2003). *HAZUS-MH 2.1 Technical Manual*. FEMA 439. Multi-Hazard Loss Estimation Methodology for Earthquakes, Floods, and Hurricanes.

Hart, A., Rodríguez, Á., Carvajal, J., & Ciottone, G. (2021). "Earthquake response in Chile: A case study in health emergency and disaster risk management." *American Journal of Disaster Medicine*, 14(4), 313–318. https://doi.org/10.5055/ajdm.2021.0413

Instituto Nacional de Estadísticas (2025). *Resultados Censo 2024: Región de Valparaíso*. Presentación regional de resultados del Censo de Población y Vivienda 2024.

Inzunza, S., & Martínez, C. (2024). "Método CRET: Una propuesta para incorporar áreas de riesgo concatenado sismo-tsunami en la planificación territorial chilena." *Revista EURE*, 51(152), 1–33.

Jaiswal, K., & Wald, D. (2010). "An empirical model for global earthquake fatality estimation." U.S. Geological Survey. PAGER system background document.

Ministerio de Salud de Chile (2010). *El terremoto y tsunami del 27 de febrero en chile: Crónica y lecciones aprendidas en el sector salud*. Technical report.

### Fuentes de Datos

**Infraestructura Deportiva:**
- Wikipedia: Artículos sobre estadios de fútbol de Chile y recintos deportivos de Valparaíso
- Bases municipales (MINEDUC Vitrina Escolar para colegios; municipalidades para gimnasios)

**Población y Demografía:**
- INE Censo 2024 (datos definitivos por comuna)
- INE Proyecciones (datos para 2026)

**Riesgo Sísmico y Tsunami:**
- SHOA (Servicio Hidrográfico y Oceanográfico de la Armada)
- Centro Sismológico Nacional
- Estudios académicos (PUC, USM)


## Sección de Colegios y scripts generadores de datos

## `Colegios.csv`

Archivo de **matrícula y ubicación de establecimientos educacionales** en Chile (datos MINEDUC). Contiene aproximadamente 16.700 filas de colegios de todo el país.

| Aspecto | Detalle |
|---------|---------|
| Formato | CSV con separador `;`, codificación `latin-1` |
| Cobertura | Todos los establecimientos del país por año (`AGNO`) |
| Uso en el proyecto | Solo Región de Valparaíso (`COD_REG_RBD = 5`) |

https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/

### Columnas relevantes para el generador

| Columna | Descripción |
|---------|-------------|
| `RBD` | Rol Base de Datos (identificador único del establecimiento) |
| `NOM_RBD` | Nombre del colegio |
| `COD_REG_RBD` | Código de región (5 = Valparaíso) |
| `NOM_COM_RBD` | Nombre de la comuna |
| `ESTADO_ESTAB` | Estado del establecimiento (`1` = activo) |
| `RURAL_RBD` | Tipo de localización (`0` = urbano) |
| `LATITUD`, `LONGITUD` | Coordenadas geográficas (coma decimal) |
| `MAT_TOTAL` | Matrícula total del establecimiento |

El script generar_datos.py **no usa todo el archivo**: filtra colegios urbanos activos de la Región de Valparaíso, en las cinco comunas del estudio, con matrícula mínima de 300 alumnos.

## Scripts generadores

La lógica compartida está en `generar_datos_core.py`. Hay **tres puntos de entrada**:

| Script | Uso | Salida por defecto |
|--------|-----|-------------------|
| `generar_datos.py` | Instancia reducida del Informe 2 (5 comunas fijas, 2 colegios c/u) | `Datos/data/` |
| `generar_datos_configurable.py` | Muestra aleatoria de comunas de la región 5 | `Datos/data/configurable/` |
| `generar_datos_completo.py` | Todas las comunas con colegios en MINEDUC (37 con `mat_min=300`) | `Datos/data/completo/` |

### Comunas y hospitales

- **Población:** Censo 2024 desde `poblacion_comunas_censo2024_consolidado.csv`; si una comuna no está en ese archivo, se estima a partir de la matrícula escolar.
- **Coordenadas de comuna:** centroide ponderado por matrícula de colegios urbanos activos.
- **Hospitales** (3, fijos en todos los modos): Carlos Van Buren, Eduardo Pereira (Valparaíso) y Gustavo Fricke (Viña del Mar).

### Flujo común (`generar_datos_core.py`)

1. Cargar colegios de `Colegios.csv` (región 5, activos, urbanos, `mat_min`).
2. Seleccionar centros de triaje (top por matrícula o todos, según el modo).
3. Derivar `cap_j`, `f_j`, `o_j`, `req_j` según matrícula del colegio.
4. Calcular demanda HAZUS (τ = 5‰, 74% leve / 26% moderado, 7 días).
5. Matrices de tiempo Haversine y cobertura binaria (`T_max` = 30 min).
6. Escribir CSV y resumen de cobertura.

### 1. `generar_datos.py` — instancia Informe 2

**Comunas fijas (5):** Viña del Mar, Valparaíso, Quilpué, Villa Alemana, Concón.  
**Colegios:** 2 por comuna (mayor matrícula).

```bash
python Datos/generar_datos.py
```

### 2. `generar_datos_configurable.py` — muestra aleatoria

Elige **N comunas al azar** entre las ~37 con colegios elegibles en la región 5, y **K colegios** por comuna (top matrícula).

```bash
# 8 comunas aleatorias, 3 colegios c/u, reproducible con semilla
python Datos/generar_datos_configurable.py --comunas 8 --escuelas 3 --seed 42

# Comunas fijas (sin sorteo)
python Datos/generar_datos_configurable.py --lista "VIÑA DEL MAR,VALPARAISO,QUILPUE" --escuelas 2

# Ver comunas disponibles
python Datos/generar_datos_configurable.py --listar-comunas
```

| Argumento | Default | Descripción |
|-----------|---------|-------------|
| `--comunas` | 5 | Cantidad de comunas aleatorias |
| `--escuelas` | 2 | Top K colegios por comuna |
| `--mat-min` | 300 | Matrícula mínima |
| `--seed` | — | Semilla para repetir la muestra |
| `--lista` | — | Comunas fijas separadas por coma |
| `--output` | `data/configurable` | Carpeta de salida |

### 3. `generar_datos_completo.py` — región a fondo

Incluye **todas las comunas** de Valparaíso con al menos un colegio que cumple `mat_min`. Sin `--escuelas`, usa **todos** los colegios elegibles por comuna (~400+ centros); con `--escuelas N` limita al top N (recomendado si el solver es lento).

```bash
# Todas las comunas, todos los colegios elegibles
python Datos/generar_datos_completo.py

# 37 comunas, top 3 colegios c/u (~98 centros)
python Datos/generar_datos_completo.py --escuelas 3

# Incluir comunas pequeñas (matrícula desde 100)
python Datos/generar_datos_completo.py --mat-min 100
```

### Parámetros globales (en `generar_datos_core.py`)

| Parámetro | Valor | Significado |
|-----------|-------|-------------|
| `DIAS` | 7 | Horizonte temporal |
| `T_MAX` | 30 min | Tiempo máximo de viaje permitido |
| `TAU_TOTAL` | 0.005 | Heridos por mil habitantes |
| `PROP` | 74% / 26% | Proporción leve / moderado |
| `MAT_MIN` | 300 (configurable) | Matrícula mínima del colegio |
| `FACTOR_CAMAS` | 0.907 × 0.85 | Camas operativas post-desastre |

`MaxC_t` y `H_t` se escalan automáticamente según el número de centros y comunas de cada instancia.

### Archivos generados

| Archivo | Contenido |
|---------|-----------|
| `nodos_comunas.csv` | Comunas: id, nombre, lat, lon, población |
| `nodos_centros.csv` | Centros de triaje (colegios): id, RBD, capacidad, costos, equipos |
| `nodos_hospitales.csv` | Hospitales: ubicación, camas base y capacidad efectiva |
| `cap_hospital_dia.csv` | Capacidad hospitalaria por día |
| `demanda.csv` | Demanda diaria por comuna, día y gravedad |
| `demanda_max.csv` | Demanda máxima diaria por comuna y gravedad |
| `tiempos_ij.csv` / `tiempos_ik.csv` | Tiempos comuna → centro / hospital |
| `cobertura_ij.csv` / `cobertura_ik.csv` | Cobertura binaria |
| `personal_dia.csv` | Personal disponible por día |
| `max_centros_dia.csv` | Máximo de centros abiertos por día |
| `parametros.csv` | Parámetros globales + metadatos de la instancia |

