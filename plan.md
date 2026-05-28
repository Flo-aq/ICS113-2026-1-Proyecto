Ready for review
Select text to add comments on the plan
Plan: Reorganización y generación de datos del modelo (E3)
Context
Crear una estructura de carpetas ordenada donde cada tipo de recinto tiene su propio script de procesamiento, y un script general en Datos/ los combina para generar los CSVs finales en Datos/data/ (nombrados exactamente como en el modelo del E2).

Estructura de carpetas objetivo
Datos/
├── Colegios.csv
├── infraestructura_deportiva_consolidada.csv
├── poblacion_comunas_censo2024_consolidado.csv
│
├── construir_instancia.py          ← script general (nuevo)
│
├── colegios/                       ← ya existe
│   ├── filtrar_colegios.py         ← ACTUALIZAR (leer población de CSV, no hardcodear)
│   ├── columnas_colegios.json
│   ├── comunas_region5.json
│   ├── normativa_recintos_escolares.md
│   └── colegios_filtrados.csv      ← output de colegios/
│
├── recintos/                       ← NUEVA CARPETA
│   ├── filtrar_recintos.py         ← nuevo script solo para estadios/polideportivos
│   └── recintos_filtrados.csv      ← output de recintos/
│
├── hospitales/                     ← crear carpeta vacía (trabajo futuro)
│
└── data/                           ← CSVs finales para Gurobi (nombres del modelo)
    ├── nodos_comunas.csv
    ├── nodos_centros.csv           ← colegios + recintos combinados
    ├── demanda.csv                 ← D_i,t,g
    ├── demanda_max.csv             ← D^max_i,g
    ├── tiempos_ij.csv              ← T^viaje_i,j
    ├── cobertura_ij.csv            ← A_i,j
    ├── personal_dia.csv            ← H_t
    ├── max_centros_dia.csv         ← MaxC_t
    └── parametros.csv              ← escalares del modelo
Decisiones
Tema	Decisión
Hospitales	Ignorar por ahora. La carpeta hospitales/ se crea vacía.
Cap_j (colegios)	Fórmula OGUC/SPHERE de filtrar_colegios.py
Cap_j (recintos)	Columna Capacidad_Personas del CSV directamente
Comunas	No hardcodear. Leer de poblacion_comunas_censo2024_consolidado.csv. comunas_filtro=None = todas
Centroide i	Centroide ponderado por matrícula de colegios (igual que ahora, documentado)
Redundancia	OK que colegios_filtrados.csv y data/nodos_centros.csv se solapen
Archivos a crear/modificar
1. Datos/colegios/filtrar_colegios.py — ACTUALIZAR
Cambios respecto a la versión actual:

Leer población de CSV en vez de COMUNAS_META hardcodeada
Parámetro comunas_filtro: lista de nombres o None (todas las de Región 5 presentes en el CSV de población)
Mantener todas las funciones existentes (normalize, parse_coord, etc.)
El output colegios_filtrados.csv ya tiene las columnas correctas
2. Datos/recintos/filtrar_recintos.py — NUEVO
Lee infraestructura_deportiva_consolidada.csv
Filtra: Estado == "Operativo"
Filtra por comunas indicadas (mismo parámetro comunas_filtro)
Calcula cap_j = Capacidad_Personas (ya viene en el CSV)
Columnas output: id, nombre, comuna, tipo_recinto, lat, lon, cap_j
Escribe recintos/recintos_filtrados.csv
3. Datos/construir_instancia.py — NUEVO
Script maestro. Funciones importables por Gurobi + main().

def cargar_comunas(comunas_filtro=None) -> list[dict]
    # Lee poblacion_comunas_censo2024_consolidado.csv
    # Calcula centroide via Colegios.csv (enrollment-weighted)

def cargar_centros(comunas, n_colegios=2, min_mat=300, holgura=0.0) -> list[dict]
    # Llama internamente a la lógica de colegios/ y recintos/
    # Devuelve lista unificada con campo "tipo": "colegio" | "estadio"

def calcular_tiempos(comunas, centros) -> dict  # {(i_id, j_id): minutos}

def calcular_cobertura(tiempos, t_max=30) -> dict  # {(i_id, j_id): 0|1}

def calcular_demanda(comunas, tau=0.005, prop=None, phi=None) -> dict  # {(i_id,t,g): val}

def generar_parametros_escalares(**kwargs) -> dict
    # Retorna dict con T_max, L, Pres, P_g, ratio_g, H_t, MaxC_t
    # Parámetros sin fuente marcados con "TODO: investigar fuente"

def escribir_csvs(output_dir, comunas, centros, tiempos, cobertura, demanda, params)
    # Escribe todos los archivos en data/ con nombres exactos del modelo

def main(comunas_filtro=None, n_colegios=2, holgura=0.0)
Prompt de investigación para parámetros faltantes
Contexto del proyecto
Estamos construyendo un modelo de optimización de localización de centros de triaje de emergencia post-terremoto para la Región de Valparaíso, Chile. El escenario es un sismo de magnitud ≥ 8.0 (equivalente al 27-F de 2010). El modelo planifica la apertura, dotación y operación de centros de triaje en colegios y estadios municipales durante los primeros 7 días tras el evento. Los pacientes son de dos tipos: leves (74%) y moderados (26%), y se busca minimizar la lista de espera ponderada por severidad. Los centros son atendidos por "equipos equivalentes de salud" que incluyen médicos, enfermeras y paramédicos agrupados funcionalmente.

Verificación
python Datos/construir_instancia.py
# Imprime: N comunas, M centros (X colegios + Y estadios), cobertura por comuna
# Genera todos los CSVs en Datos/data/