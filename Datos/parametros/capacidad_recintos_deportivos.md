# Capacidad de Recintos Deportivos como PMAs — cap_j

Justificación normativa del parámetro `cap_j` para estadios y polideportivos
usados como Puestos Médicos Avanzados (PMA) en el modelo de optimización
post-terremoto Región de Valparaíso.

---

## Por qué no se usa el aforo

El aforo certificado de un recinto deportivo corresponde a la capacidad de las
**graderías** (Art. 4.8.2 OGUC: zona de espectadores), no del espacio de
intervención médica. En un PMA, las graderías no son superficie usable para
triaje: carecen de nivel uniforme, acceso de camillas y conexión a redes de
emergencia. OGUC Art. 4.8.2 distingue explícitamente "zona de cancha" y
"zona de espectadores" como zonas de ocupación distintas.

---

## Fórmula

```
cap_j = floor(A_cancha_m2 × FACTOR_USO_REFUGIO / M2_POR_PERSONA)
```

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| `FACTOR_USO_REFUGIO` | 0,65 | OGUC Art. 4.8.2 — mismo valor que colegios |
| `M2_POR_PERSONA` | 3,5 m²/persona | Estándar SPHERE (2018), mínimo para albergue de emergencia — mismo que colegios |

El parámetro `M2_POR_PERSONA` se eligió igual al de colegios (SPHERE 3,5 m²)
para mantener consistencia normativa entre tipos de centro. OGUC Art. 4.2.4
establece 4,0 m²/persona para gimnasios en uso normal (no emergencia); se
prefiere el estándar humanitario SPHERE por tratarse de situación de desastre.

---

## Área de cancha (A_cancha_m2)

### Reglas de composición

1. Se suman todos los espacios de cancha **físicamente distintos** dentro del recinto.
2. Una cancha que sirve a más de un deporte cuenta **una sola vez**.
3. Para estadios con **pista de atletismo**: se suma la superficie de la pista
   (anillo corredor) al área del campo interior. Las graderías no se suman.
4. Para estadios con **solo cancha de fútbol** (sin pista): se usa el área del campo.

### Cálculo de pista de atletismo (World Athletics / IAAF)

Dimensiones estándar: radio interior r = 36,5 m; largo rectas L = 84,39 m;
ancho de carril = 1,22 m.

```
A_pista(n_carriles) = 2 × L × (n × 1,22) + π × [(r + n×1,22)² − r²]
```

| Carriles | A_pista |
|----------|---------|
| 6 | 3.082 m² |
| 7 | 3.629 m² |
| 8 | 4.185 m² |

Para recintos donde la fuente especifica "6–8 carriles" se usa 7 (punto medio).
Para recintos donde solo se indica "400 m estándar" sin número de carriles se
usa 8 (estándar IAAF nivel 2, más común en estadios municipales chilenos de
esta categoría).

---

## Dimensiones de cancha por recinto

Los valores marcados con (~) son inferidos del estándar FIFA para la disciplina;
los sin (~) son exactos según la fuente citada.

| ID | Nombre | Cancha / Espacio | Dim. exactas | Área m² | Tipo dato | Fuente principal |
|----|--------|-----------------|--------------|---------|-----------|-----------------|
| 1 | Estadio Sausalito, Viña del Mar | Cancha Fútbol 11 | 105×68 m | 7.140 | Exacto | ArchDaily CL; recintosdeportivos.wordpress.com; Wikipedia (fr/it) |
| 1 | Estadio Sausalito | Pista Atletismo | 400 m, 6–8 carriles | 3.629* | Calculado (7 carriles) | olympics.com; CSD España ATLpt 2021 |
| 2 | Gin. Polideportivo Viña del Mar | Cancha Multiuso (principal) | 40×20 m | 800 | Exacto | munivina.cl; quieroentrenar.cl |
| 2 | Gin. Polideportivo Viña del Mar | Cancha Básquetbol | 15×28 m | 420 | Exacto (reglamentario FIBA) | goreloslagos.cl/FRIL 2015 |
| 2 | Gin. Polideportivo Viña del Mar | Cancha Vóleibol | 18×9 m | 162 | Exacto (reglamentario FIVB) | goreloslagos.cl/FRIL 2015; chilecubica.com |
| 2 | Gin. Polideportivo Viña del Mar | Cancha Fútbol Sala | 15×28 m | 420 | Exacto (cancha física distinta a básquetbol) | goreloslagos.cl/FRIL 2015 |
| 3 | Estadio Elías Figueroa, Valparaíso | Cancha Fútbol 11 | 105×68 m | 7.140 | Exacto | Wikipedia (bs/nl/fr) |
| 4 | Complejo O'Higgins, Valparaíso | Cancha Fútbol 11 | 100×54 m | 5.400 | Exacto | Wikipedia; aroundus.com |
| 4 | Complejo O'Higgins | Pista Atletismo | 400 m estándar | 4.185* | Calculado (8 carriles) | olympics.com; civideportes.com.co |
| 5 | Estadio Lucio Fariña, Quillota | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia (sin dimensión oficial). Aforo 7.680 esp. |
| 7 | Estadio Ítalo Composto, Villa Alemana | Cancha Fútbol 11 | ~100×54 m | ~5.400 | Inferido | wikimapia.org; Instagram. Aforo ~3.500 |
| 11 | Estadio Atlético Concón | Cancha Fútbol 11 | 105×68 m | 7.140 | Exacto | Wikipedia (es) |
| 11 | Estadio Atlético Concón | Pista Atletismo | 400 m tartán | 4.185* | Calculado (8 carriles) | olympics.com; flyonsport.com |
| 12 | Estadio Raúl Vargas, Quintero | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. Aforo 2.500 esp. |
| 15 | Gimnasio Municipal Quilpué | Cancha Básquetbol | 15×28 m | 420 | Exacto (FIBA, inferido por tipo) | goreloslagos.cl/FRIL 2015. Inauguración 2019 con básquetbol. Área total construida: 1.084 m² (incluye graderías, vestuarios y circulaciones — no usable) |
| 18 | Estadio Arturo Echazarreta, Casablanca | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. Aforo exacto 1.672 esp. |
| 19 | Estadio Fernando Ross, Cartagena | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. Reconstrucción 2009 |
| 20 | Estadio Eugenio Castro, El Quisco | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. ~25–28 m s.n.m. |
| 24 | Estadio Arturo Longton, Quilpué | Cancha Fútbol 11 | 105×68 m | 7.140 | Confirmado por equipo | Villa Olímpica, ~120–130 m s.n.m. |
| 25 | Estadio Hanga Roa, Isla de Pascua | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. Pasto sintético 1988 |
| 26 | Estadio Juan Fernández | Cancha Fútbol 11 | — | 4.000 | Confirmado por equipo | Estadio pequeño (aforo 350 esp.), Robinson Crusoe, inaugurado 2012 |
| 27 | Estadio Ángel Navarrete, Limache | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. Complejo con piscina |
| 28 | Estadio Gustavo Ocaranza, Limache | Cancha Fútbol 11 | ~105×68 m | ~7.140 | Inferido (estándar FIFA) | Wikipedia. Sede Deportes Limache 1988 |

\* Área calculada con fórmula IAAF a partir de dimensiones estándar; no es medida directamente.

### Supuesto para estadios sin dimensiones exactas

Los estadios sin dimensión oficial verificada (IDs 5, 12, 18, 19, 20, 25, 27, 28) tienen
asignado el estándar FIFA recomendado (105×68 m = 7.140 m²). El mínimo FIFA es
100×64 m (6.400 m²); los estadios de esta categoría en Chile suelen cumplir el estándar
recomendado. ID 24 confirmado a 105×68 m por el equipo. ID 26 confirmado a 4.000 m²
(estadio de isla pequeña, aforo 350 espectadores).

---

## Parámetro configurable

El valor de fallback para recintos sin `Area_Cancha_m2` en el CSV es controlable
desde `construir_instancia.py`:

```python
AREA_CANCHA_DEFECTO_M2 = 7_140  # FIFA estándar 105×68 m
```

Se pasa a `filtrar_recintos(area_cancha_defecto=...)` al construir la instancia.

---

## Referencias

Ministerio de Vivienda y Urbanismo [MINVU]. (1992). *Ordenanza General de Urbanismo
y Construcciones* (Decreto Supremo N° 47, de 5 de junio de 1992).
https://www.bcn.cl/leychile/navegar?idNorma=8201
- Art. 4.8.2: distingue "zona de cancha" y "zona de espectadores" → justifica excluir aforo. (MINVU, 1992, Art. 4.8.2)
- Art. 4.2.4: 4,0 m²/persona para gimnasios en uso normal → referencia de carga; se prefiere SPHERE 3,5 m² para situación de emergencia. (MINVU, 1992, Art. 4.2.4)

InterAction. (2018). *The Sphere Handbook: Humanitarian charter and minimum standards
in humanitarian response* (Revised ed.).
https://www.spherestandards.org/wp-content/uploads/Sphere-Handbook-2018-EN.pdf
- 3,5 m²/persona mínimo para albergue de emergencia → justifica `M2_POR_PERSONA`. (InterAction, 2018)

FIFA. (2023). *FIFA Quality Programme for Football Turf: Technical guidelines for
football turf* (2023 ed.).
https://inside.fifa.com/innovation/standards/football-turf/fifa-quality-programme-for-football-turf
- Campo recomendado 105×68 m, mínimo 100×64 m → justifica dimensiones inferidas. (FIFA, 2023)

World Athletics. (2019). *Track and field facilities manual* (2019 ed.).
https://www.beathletics.com/en/iaaf-world-athletic-manual
- Radio interior 36,5 m, rectas 84,39 m, carril 1,22 m → base del cálculo de A_pista. (World Athletics, 2019)

FIBA. (2022). *FIBA official basketball rules 2022*.
https://www.fiba.basketball/en/news/fiba-official-basketball-rules-2022-set-to-come-into-force-october-1
- Cancha 28×15 m → IDs 2 y 15. (FIBA, 2022)

FIVB. (2023). *FIVB official volleyball rules 2023-2024*.
https://www.fivb.com/volleyball/the-game/official-volleyball-rules/
- Cancha 18×9 m → ID 2. (FIVB, 2023)
