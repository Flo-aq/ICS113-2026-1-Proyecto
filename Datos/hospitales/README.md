# Datos: Red Hospitalaria — Región de Valparaíso

Dataset consolidado de establecimientos de salud con camas de hospitalización para la Región de Valparaíso, utilizado como conjunto **K** (hospitales de la red asistencial) en el modelo de optimización de Zonas de Triaje post-sismo.

---

## Fuentes de datos

### Establecimientos de salud

| Archivo | Descripción | Fecha |
|---|---|---|
| `establecimientos_20260526.csv` | Registro MINSAL de todos los establecimientos de salud de Chile. **Fuente principal.** | Mayo 2026 |
| `Establecimientos_de_Salud_de_Chile.csv` | Registro anterior MINSAL, ya filtrado a Valparaíso. Aporta columnas históricas (`F_REAPER`, `F_CAMBIO`, `TIPO_CAMB`, `COORD_X`, `COORD_Y`). | Sin fecha |
| `Base_Establecimientos_ChileDEIS_MINSAL(23-01-2019).xlsx` | Base DEIS-MINSAL. Aporta columnas `Alias`, `Tipo Estrategia` y `Observación`. | Enero 2019 |
| `Listado-Establecimientos-DEIS.pdf` | Listado oficial DEIS. Aporta `NombreComun` (nombre popular del establecimiento). | Sin fecha |

### Dotación de camas

| Archivo | Descripción | URL |
|---|---|---|
| `Dotación de camas 2010-2023 Establecimientos Pertenecientes al SNSS.xlsx` | Dotación histórica de camas para hospitales públicos de la red SNSS, por área funcional. | [repositoriodeis.minsal.cl](https://repositoriodeis.minsal.cl) |
| `Dotación de camas 2019-2023 Establecimientos No pertenecientes al SNSS.xlsx` | Dotación de camas para establecimientos privados y no-SNSS (clínicas, mutuales, FF.AA.). | [repositoriodeis.minsal.cl](https://repositoriodeis.minsal.cl/ContenidoSitioWeb2020/Estadisticas/DOTACION_CAMAS/Dotaci%C3%B3n%20de%20camas%202019-2020-2021%20Establecimientos%20No%20pertenecientes%20al%20SNSS.xlsx) |

Fuente adicional consultada para verificación de datos del Servicio de Salud Valparaíso-San Antonio: [ssvalposa.redsalud.gob.cl](https://ssvalposa.redsalud.gob.cl/atencion-secundaria-y-terciaria/).

---

## Metodología de construcción

### 1. Consolidación de archivos de establecimientos

Los cuatro archivos de establecimientos se integraron en un único dataset mediante un **join en cascada** con tres estrategias (en orden de prioridad):

1. **Código de establecimiento** (`EstablecimientoCodigo` / `C_VIG` / `Cod`)
2. **Dirección**: `ComunaCodigo` + `Numero` (normalizado: sin tildes, en minúsculas)
3. **Coordenadas geográficas**: `Latitud` + `Longitud` redondeadas a 3 decimales (~111 m de precisión)

La normalización de texto para el join por dirección elimina tildes y diferencias de mayúsculas/minúsculas para evitar falsos negativos por inconsistencias de formato entre fuentes.

Resultados del join por fuente secundaria:

| Fuente | Por código | Por dirección | Por coordenadas | Sin match |
|---|---|---|---|---|
| `Establecimientos_de_Salud_de_Chile.csv` | 65 | 2 | 0 | 354 |
| `Base_Establecimientos_ChileDEIS_MINSAL.xlsx` | 315 | 24 | 14 | 68 |
| `Listado-Establecimientos-DEIS.pdf` | 132 | 0 | 0 | 289 |

### 2. Dotación de camas

La columna `Camas2023` se construyó cruzando los dos xlsx de dotación contra el dataset consolidado, también usando join normalizado por nombre. Dos establecimientos requirieron corrección manual por diferencia de nombre entre fuentes:

- **Hospital Claudio Vicuña**: registrado con espacio extra en el xlsx SNSS → 164 camas
- **Hospital Biprovincial Quillota Petorca**: registrado como *Hospital San Martín (Quillota)* en el xlsx SNSS → 290 camas

---

## Filtros aplicados

### Filtro 1 — Región y estado vigente
- `RegionCodigo == '05'` (Región de Valparaíso)
- `EstadoFuncionamiento` contiene `'Vigente'` (en operación habitual)

Resultado: **421 establecimientos** de un total de 5.649 a nivel nacional.

### Filtro 2 — Tipo de establecimiento relevante para el modelo

Se mantuvieron solo los tipos con capacidad de atención general (eliminando centros de servicio único o ambulatorios):

| Tipo incluido | N | Tipo excluido | N |
|---|---|---|---|
| Centro de Salud Familiar (CESFAM) | 80 | Centro de Salud Privado | 59 |
| Posta de Salud Rural (PSR) | 54 | CECOSF | 29 |
| SAPU | 31 | Laboratorio Clínico | 34 |
| Hospital | 26 | Clínica Dental | 17 |
| SUR | 21 | Vacunatorio | 5 |
| Clínica | 12 | Otros | — |
| SAR | 6 | | |

Resultado: **230 establecimientos**.

### Filtro 3 — Solo establecimientos con camas (conjunto K del modelo)

El modelo distingue dos conjuntos:
- **J** = Centros de triaje temporales (colegios, gimnasios, estadios) — *no son establecimientos de salud*
- **K** = Hospitales de la red asistencial, que reciben pacientes **graves** con capacidad medida en **camas** (`Cap_{k,t}`)

Por tanto, se conservaron únicamente los tipos con camas de hospitalización real:

| Tipo | N |
|---|---|
| Hospital | 26 |
| Clínica | 12 |

Resultado: **38 establecimientos**.

### Filtro 4 — Exclusión de establecimientos atípicos

Se eliminaron 6 establecimientos por las siguientes razones:

| Establecimiento | Razón |
|---|---|
| Complejo Penitenciario (Valparaíso) | Enfermería de recinto penitenciario, no hospital general |
| Hospital Psiquiátrico Dr. Philippe Pinel (Putaendo) | Hospital psiquiátrico; mencionado explícitamente en el informe MINSAL 2010 como completamente inhabilitado tras el 27-F |
| Hospital Hanga Roa (Isla de Pascua) | Pertenece administrativamente a la región pero se ubica a ~3.700 km del continente |
| Sanatorio Marítimo San Juan de Dios (Viña del Mar) | Sin datos de dotación de camas disponibles |
| Clínica de la Agrupación Médica Americana (Valparaíso) | Sin datos de dotación de camas disponibles |
| Clínica Intermedical (San Antonio) | Sin datos de dotación de camas disponibles |

Resultado: **32 establecimientos**.

---

## Dataset final

**Archivo**: `establecimientos_valparaiso_vigentes.csv`  
**Registros**: 32 establecimientos  
**Columnas**: 43

### Columnas clave para el modelo

| Columna | Descripción |
|---|---|
| `EstablecimientoCodigo` | Código MINSAL vigente |
| `EstablecimientoGlosa` | Nombre oficial |
| `ComunaCodigo` / `ComunaGlosa` | Código y nombre de la comuna |
| `Latitud` / `Longitud` | Coordenadas geográficas (WGS84) |
| `TipoEstablecimientoGlosa` | Hospital o Clínica |
| `NivelComplejidadEstabGlosa` | Alta / Mediana / Baja complejidad |
| `DependenciaAdministrativa` | Público / Privado / FF.AA. |
| `Camas2023` | Dotación total de camas (año 2023) — parámetro `Cap_{k,t}` base |

### Distribución por comuna

| Comuna | Hospitales | Clínicas | Total | Camas |
|---|---|---|---|---|
| Viña del Mar | 3 | 4 | 7 | 1.432 |
| Valparaíso | 3 | 1 | 4 | 684 |
| Quillota | 1 | 0 | 1 | 290 |
| Quilpué | 1 | 1 | 2 | 222 |
| San Felipe | 1 | 0 | 1 | 221 |
| San Antonio | 1 | 2 | 3 | 205 |
| Los Andes | 1 | 1 | 2 | 195 |
| Limache | 2 | 0 | 2 | 121 |
| Villa Alemana | 1 | 0 | 1 | 81 |
| Calera | 1 | 1 | 2 | 80 |
| La Ligua | 1 | 0 | 1 | 59 |
| Llaillay | 1 | 0 | 1 | 37 |
| Quintero | 1 | 0 | 1 | 31 |
| Putaendo | 1 | 0 | 1 | 28 |
| Cabildo | 1 | 0 | 1 | 21 |
| Petorca | 1 | 0 | 1 | 18 |
| Casablanca | 1 | 0 | 1 | 6 |
| **Total** | **22** | **10** | **32** | **3.731** |

> **Nota**: La dotación de camas corresponde al año 2023 (dato pre-sismo). El parámetro `Cap_{k,t}` del modelo debe ajustarse según la reducción de capacidad post-sismo estimada para cada período `t`.
