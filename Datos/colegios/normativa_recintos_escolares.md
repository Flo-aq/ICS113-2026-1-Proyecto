# Normativa de Recintos Escolares — Región de Valparaíso

Referencia para el cálculo de capacidad de colegios como refugios de emergencia
en `filtrar_colegios.py`. Las áreas estimadas se derivan exclusivamente de la
matrícula declarada en el dataset MINEDUC, ya que el CSV no contiene superficie real.

---

## Normas nacionales aplicables

| Instrumento | Ámbito | Exigencia relevante |
|-------------|--------|---------------------|
| **DS N°548/1988 (Mineduc)** | Planta física escolar | Detalla recintos obligatorios (aulas, laboratorios, comedor, servicios). Comedor: 0,9 m²/alumno (3 turnos, mín. 54 m²). No fija área de aula directamente. |
| **DS N°40/2021 (Mineduc)** | Modifica DS 548 | Actualiza requisitos de educación parvularia. No redefine superficies principales. |
| **OGUC — DS N°47/1992 (Minvu)** | Locales escolares | Patios: ancho mínimo 5,50 m; ~2,5 m²/alumno. Multicancha 18×30 m si matrícula ≥ 135. Altura libre ≥ 2,20 m en aulas. |
| **DS N°289/1989 (Minsalud)** | Condiciones sanitarias | Servicios higiénicos según tabla OGUC. No fija superficies de locales. |
| **Guías Técnicas Mineduc (2017)** | Diseño de proyectos SEP/JEC | Recomendación: aulas 2,0–3,2 m²/alumno; patios 2,5 m²/alumno. Sin valor legal obligatorio. |

---

## Parámetros usados en `filtrar_colegios.py`

| Constante | Valor | Fuente normativa |
|-----------|-------|-----------------|
| `AREA_AULA_M2_POR_ALUMNO` | 2,5 m²/alumno | Punto medio del rango Mineduc (2,0–3,2 m²) |
| `AREA_PATIO_M2_POR_ALUMNO` | 2,5 m²/alumno | OGUC Art. 4.5.x (recomendación ~2,5 m²/alumno) |
| `AREA_MULTICANCHA_M2` | 540 m² | OGUC: 18×30 m para establecimientos con matrícula ≥ 135 |
| `FACTOR_USO_REFUGIO` | 0,65 | Fracción del área total efectivamente usable como refugio (descuenta pasillos, baños, área administrativa) |
| `M2_POR_PERSONA` | 3,5 m²/persona | Estándar SPHERE mínimo para albergues de emergencia |

---

## Fórmula de estimación

```
area_total   = MAT × 2,5  +  MAT × 2,5  +  (540 si MAT ≥ 135 else 0)
             = MAT × 5,0  +  540
area_util    = area_total × 0,65
cap_base     = floor(area_util / 3,5)
cap_final    = floor(cap_base × (1 + holgura/100))
```

`holgura` es un porcentaje firmado:
- Valor **negativo** → estimación conservadora (reduce capacidad).
- Valor **positivo** → estimación optimista (amplía capacidad).
- Valor **0** → capacidad base sin ajuste.

### Ejemplos numéricos

| Matrícula | área total (m²) | área útil (m²) | cap. base | holgura −20% | holgura +20% |
|----------:|----------------:|---------------:|----------:|-------------:|-------------:|
| 500       | 3 040           | 1 976          | 564       | 451          | 677          |
| 1 000     | 5 540           | 3 601          | 1 028     | 822          | 1 234        |
| 1 500     | 8 040           | 5 226          | 1 493     | 1 194        | 1 792        |
| 2 000     | 10 540          | 6 851          | 1 957     | 1 566        | 2 348        |

---

## Brechas normativas relevantes

- **No existe norma legal de área para gimnasios cerrados.** La OGUC solo exige
  la multicancha exterior (18×30 m); cualquier gimnasio cubierto queda a criterio
  del proyecto.
- **El DS 548 no fija superficie de aula**, solo capacidad máxima (40 alumnos/sala).
  Las guías ministeriales recomiendan 2,0–3,2 m²/alumno pero no tienen fuerza legal.
- **Edificios anteriores a 1997** pueden tener reducción de hasta 50 % en patios
  si ampliaron por JEC con informe SEREMI favorable (OGUC).
- **Las coordenadas del CSV** son el centroide del establecimiento declarado a
  MINEDUC; para establecimientos con terrenos dispersos o múltiples inmuebles
  la ubicación puede ser aproximada.

---

## Fuentes

- Ley Chile — DS 548/1988: <https://www.bcn.cl/leychile>
- Ley Chile — OGUC DS 47/1992: <https://www.bcn.cl/leychile>
- Ley Chile — DS 289/1989: <https://www.bcn.cl/leychile>
- MINEDUC — Directorio de Establecimientos Educacionales: <https://datosabiertos.mineduc.cl>
- SPHERE Handbook — Minimum Standards in Humanitarian Response (2018)
