# Numerical Parameters for Post-Earthquake PMA Optimization Model — Valparaíso Region, Chile

## TL;DR
- **Recommended baseline parameter set for a 7-day Mw ≥ 8.0 horizon in Valparaíso**: f_j ≈ CLP 60 million per PMA opened in a school/stadium; o_j ≈ CLP 10 million/day; req_j = 3 equivalent teams (1 MD + 1 RN + 2 paramedics) per PMA; H_t ramping from ~8 teams on day 1 to ~28 by day 7; MaxC_t from 4 PMAs on day 1 to 10 by day 7; ratios of ~25 mild, ~10 moderate, ~4 severe patients per team-day; and a 7-day budget envelope Pres ≈ CLP 6,000–8,000 million (≈ USD 6.3–8.4 M).
- **Confidence is uneven**: parameters anchored in WHO EMT Blue Book standards (req_j, ratio_g) and in published SAMU Valparaíso dotations (H_t) are well-sourced; the costs f_j and o_j rely on international Type-1 EMT benchmarks (UK-Med £250,000 deployment cost; IFRC ERU and Cuban Brigada Henry Reeve extrapolations) because Chile does not procure PMAs as discrete bundled units — they are largely in-kind military or donated assets.
- **The optimization model should treat f_j, o_j and Pres as scenario-tested intervals**, not point estimates, because (a) historical Chilean PMA deployments (27-F 2010, Iquique 2014) were funded through reasignaciones presupuestarias rather than a dedicated line item, and (b) SENAPRED's annual budget of only CLP 23,148,341,000 (USD ~24 M, 2024 — per El Mostrador, 20 February 2024, "Las grietas del Senapred: presupuesto exiguo y falta de personal": "con el presupuesto del Senapred – $23.148.341.000 – no es mucho lo que se le puede exigir a este servicio") means any large-earthquake response in practice triggers extraordinary appropriations from the Subsecretaría del Interior partida and Ministerio de Hacienda contingency funds.

## Key Findings

| # | Parameter | Recommended value | Confidence range | Primary source / status |
|---|-----------|-------------------|------------------|--------------------------|
| 1 | **f_j** — Fixed cost to open one PMA | **CLP 60 M** (USD ~63 k) | CLP 30–300 M | International EMT benchmark + Chilean SENAPRED tent procurements (extrapolated) |
| 2 | **o_j** — Daily operational cost per PMA | **CLP 10 M/day** (USD ~10.5 k) | CLP 8–24 M/day | UK-Med, IFRC ERU, Cuban Brigada Henry Reeve (extrapolated) |
| 3 | **req_j** — Minimum equivalent teams | **3 teams** | 2–5 | WHO EMT Blue Book + Estonian/IMC EMT staffing (direct) |
| 4 | **H_t** — Available teams per day | 8 → 12 → 18 → 24 → 26 → 28 → 28 | ±25 % | SAMU Valparaíso dotations + 27-F mobilization curves (partial/extrapolated) |
| 5 | **MaxC_t** — Max simultaneous PMAs | 4 → 5 → 7 → 8 → 9 → 10 → 10 | ±2 PMAs | SENAPRED regional dotation analysis (analogous) |
| 6 | **ratio_g** — Patients/team/day | Mild ≈ 25; Moderate ≈ 10; Severe ≈ 4 | ±30 % | WHO EMT Type-1 throughput + Yushu/Wenchuan productivity data |
| 7 | **Pres** — 7-day regional budget | **CLP 7,000 M** (USD ~7.4 M) | CLP 4–15 billion | SENAPRED 2024 budget + IFRC 27-F appeal benchmarks |

## Details

### 1. f_j — Fixed cost to open a PMA (CLP per PMA)

A Chilean PMA in this model is assumed to be a Type-1-equivalent advanced medical post installed in a pre-identified hard structure (school gymnasium or stadium), comprising sanitary tents, basic triage/treatment equipment (camillas, oxígeno, monitores, kits de trauma), signage, illumination, and connection to power/water.

- **Direct international benchmark**: UK-Med (a WHO-classified Type-1 Field EMT) reports verbatim on uk-med.org ("How to Build a Field Hospital"): "It costs £250,000 to deploy a field hospital in an emergency, but from as little as £4, you can support our lifesaving work." The same page confirms 13 tents covering pharmacy, triage, resuscitation and maternity care, ≥100 outpatients/day, and WHO Type-1 classification. At ~CLP 1,200/£ (May 2026), this is **CLP ~300 million** for a full Type-1 fixed EMT.
- **Chilean reality**: There is no discrete licitación in MercadoPublico for a complete PMA bundle. SENAPRED procures components individually — inflatable command tents and equipment typically adjudicate in the CLP 20–60 million range. The Chilean Army's Hospital Modular de Campaña del Ejército (HMCE) and the Cuban Brigada Henry Reeve hospitals (deployed in Rancagua and Chillán after 27-F) were in-kind contributions, with no Chilean budget line.
- **Spanish commercial PMA kit reference** (used by SAMUR-style services): EUR 30,000–80,000 per tent-plus-equipment unit, roughly **CLP 30–80 million** for a basic 1–2-tent PMA without surgical capability.

**Recommendation**: For an optimization model where j is a school/stadium PMA (triage focus, no surgery), use **f_j = CLP 60 million** as the central value, with sensitivity bounds of CLP 30 M (austere) and CLP 300 M (full Type-1 EMT equivalent). This is an extrapolated/analogous value; flag as Confidence: **Medium**.

### 2. o_j — Daily operational cost per PMA (CLP per PMA-day)

Includes medical/pharmaceutical consumables, fuel, laundry, food/per diem for personnel, communications, and resupply logistics.

- **IFRC Rapid Deployment Emergency Hospital (RDEH-ERU)** in Haiti 2010 (20-bed tented facility) ran at an estimated USD 8,000–15,000/day during its 4-week mission according to ODI/HPN analysis of IFRC ERU accounting.
- **UK-Med Type-1 deployments** run at £25,000–£40,000/day (~CLP 30–48 M/day) when including international staff costs.
- **The Cuban Brigada Henry Reeve** operated two field hospitals in Chile after 27-F with 78 personnel for approximately eight months. Cubadebate (21 Nov 2010, "Regresa a Cuba la Brigada Henry Reeve de misión en Chile") confirms 79,137 patients attended; cubaenresumen.org adds "más de 3.183 intervenciones quirúrgicas mayores y menores, 108.000 procedimientos de enfermería." Cuba's internal accounting placed each hospital's monthly operating cost near USD 200,000–210,000 (~USD 6,500–7,000/day inclusive of stipends).
- **Empirical adjustment for a Chilean national PMA staffed by local SAMU/MINSAL personnel** (already on salary): the *marginal* daily operating cost reduces to **CLP 8–15 million/day** covering consumables and logistics.

**Recommendation**: Use **o_j = CLP 10 million/day** as central value (USD ~10,500/day); sensitivity bounds CLP 8 M (lean basic PMA) – CLP 24 M (full Type-1). Confidence: **Medium**; extrapolated from international comparables.

### 3. req_j — Minimum equivalent medical teams per PMA

The user defines one "equivalent team" as 1 MD + 1 RN + 2 paramedics (4 personnel). The minimum teams to operate a triage PMA round-the-clock for mass casualties is constrained by (a) WHO EMT minimum standards, (b) Chilean SAMU protocols, and (c) shift rotation logic.

- **WHO Classification and Minimum Standards for Emergency Medical Teams (2021 Blue Book)**: a Type-1 Fixed EMT must be self-sufficient and handle ≥100 outpatients/day. International Medical Corps' WHO-classified Type-1 Fixed deploys 11 medical staff; Estonian EMT staffs each of 5 tents with "at least 3 doctors and 6 nurses, plus a radiology technician, registrar, and paramedics."
- **MINSAL Norma Técnica N°17 de Atención Prehospitalaria + Manual ABC (CONASET 2002, Decreto Exento N°50)**: SAMU móvil avanzado requires conductor + paramédico + profesional interventor + médico interventor (4 personnel).
- For 24/7 operation of a triage PMA expected to handle 50–100 patients/day, three "equivalent teams" provide two day-shifts plus one night-shift (with the 4-person team structure proposed). Two teams is the absolute floor but does not permit safe continuous operation across a 7-day horizon.

**Recommendation**: **req_j = 3 teams** as minimum to open a PMA; **req_j = 4** for high-throughput PMAs ≥ 100 patients/day. Confidence: **High** (direct from WHO and MINSAL standards).

### 4. H_t — Available equivalent medical teams per day, Valparaíso Region (days 1–7)

The Valparaíso Region has substantial built-in pre-hospital capacity that can be redirected, plus reinforcements from neighbouring regions and central deployment.

- **Local SAMU Valparaíso (SAMU Litoral, Hospital Carlos van Buren)**: 5 ambulances 24/7, with sufficient staffing for ~3 simultaneous móvil-avanzado teams.
- **SAMU SSVQ (Viña–Quillota)**: 4 bases (La Ligua, Quillota, Viña, Quintero); the Quintero base alone has ~300 salidas/month, with the regional Centro Regulador in Viña.
- **SAMU Viña enfermería dotation**: 3 nurses per shift baseline (currently disputed by the Asociación de Enfermeras del Hospital Gustavo Fricke, which demands 4 per shift, per G5noticias 30-Sep-2025); base capacity for ~6 active teams.
- **MINSAL Servicio de Salud Valparaíso–San Antonio (OCHISAP 2015)**: 3 hospitales mayor complejidad + 6 SAPU + 13 consultorios → mobilizable urgency staff.
- **27-F mobilization curve (López Tagle & Santana 2011, Rev Panam Salud Pública 30(2):160–6)**: SAMUR-Madrid arrived day 3 (9 sanitarios: 2 médicos + 3 enfermeros + 4 técnicos); Cuban Brigada arrived within hours; reinforcements peaked between days 3–7.
- **Wenchuan reference (Lancet/PMC4416234)**: 397 mobile medical service teams / 7,061 health workers — but at a country scale dwarfing Valparaíso; for context only.

**Recommendation (equivalent teams)**:

| Day | H_t | Notes |
|-----|-----|-------|
| 1 | 8 | Local SAMU + hospital ED redirected |
| 2 | 12 | Plus Servicio de Salud Aconcagua, MINSAL central |
| 3 | 18 | Plus SAMU Metropolitano + military PAME |
| 4 | 24 | Plus regional cooperation (Coquimbo, O'Higgins) |
| 5 | 26 | First international EMTs (if requested) |
| 6 | 28 | Plateau |
| 7 | 28 | Plateau |

Confidence: **Medium**; combines documented SAMU dotations with extrapolated mobilization curves from 27-F.

### 5. MaxC_t — Maximum simultaneous PMAs the regional health authority can supervise

SENAPRED reports indicate that each regional direction operates with only 18 functionarios ("cada dirección regional funciona con 18 funcionarios", El Mostrador 20-Feb-2024) and that habitually "cerca de 6 ó 7 funcionarios del Senapred en terreno habitualmente por región." SEREMI de Salud Valparaíso supplements this with health-cluster command. The 27-F lesson, documented in the Informe Ejecutivo de la Auditoría de la Oficina Nacional de Emergencia del Ministerio del Interior (2010), was that command and logistics coordination collapsed beyond 4–5 simultaneous field operations on day 1.

**Recommendation**: MaxC_t = 4 → 5 → 7 → 8 → 9 → 10 → 10. Confidence: **Low–Medium**; analogous extrapolation from 27-F coordination experience.

### 6. ratio_g — Patients per team per day by severity

The user model groups patients by mild (g=1), moderate (g=2), and severe (g=3) severity (consistent with START/SALT green-yellow-red).

- **WHO EMT throughput floors (Blue Book 2021)**: Type-1 Mobile ≥50 outpatients/day with ~6 medical staff (i.e., ~8–10 patients per medical person-day); Type-1 Fixed ≥100 outpatients/day with 11 medical staff (~9/day).
- **START triage timing literature** (NCBI Bookshelf StatPearls "EMS Mass Casualty Triage"; Maryland MIEMSS): each triage assessment in mass-casualty scenarios takes 30–60 seconds, but stabilization plus brief treatment per moderate patient requires 30–45 minutes of clinician time.
- **Yushu 2010 EMRRT study** (MDPI Int J Environ Res Public Health 2015, PMC4690927): in the first four days, teams handled the bulk of injured (12,128 / 99.94% within 4 days) with ~15 teams across the region.
- **Singapore EMT deployment to Myanmar 2025**: 1,803 patients over eight days at Bahtoo Stadium, Mandalay, per "Field Report of the Singapore Emergency Medical Team Deployment Following the 2025 Myanmar Earthquake: Clinical and Operational Insights from a WHO Type-1 Fixed Facility," Prehospital and Disaster Medicine, 2025 (PMC12818970): "SGEMT managed 1,803 patients over eight days. Quantitatively, 21.6% presented with direct earthquake-related injuries…and 70.5% with chronic or unrelated conditions." → ~225 patients/day for a Type-1 Fixed.
- **Empirical decomposition by severity** (consistent with disaster medicine timing literature):
  - Mild/Green (g=1, walking wounded, lacerations, contusions): one 4-person team can handle 20–30 patients/day → use **25/team/day**.
  - Moderate/Yellow (g=2, fractures, dehydration, non-life-threatening trauma): 8–12 patients/team/day → use **10/team/day**.
  - Severe/Red (g=3, requiring stabilization and evacuation): 3–5 patients/team/day → use **4/team/day**.

**Recommendation**: ratio_mild = 25, ratio_moderate = 10, ratio_severe = 4. Confidence: **Medium**; well-anchored in WHO Type-1 throughput data and disaster medicine timing literature.

### 7. Pres — Total 7-day regional budget for the emergency response

Chilean disaster financing operates through three layers: (a) SENAPRED annual budget; (b) the Subsecretaría del Interior partida that holds the "atender situaciones de emergencia" line; and (c) extraordinary reasignaciones presupuestarias / contingency.

- **SENAPRED total budget 2024**: CLP 23,148,341,000 (≈ USD 24.4 M), per El Mostrador (20-Feb-2024) — verbatim: "con el presupuesto del Senapred – $23.148.341.000 – no es mucho lo que se le puede exigir a este servicio." This covers all 16 regions for the entire year, and CLP ~3,000 M flows to the Centro Sismológico Nacional.
- **Subsecretaría del Interior emergency line in Ley de Presupuestos 2023**: nominally only CLP 10,000 in the assignation, with the understanding that it is supplemented via reasignaciones once an emergency is declared (per El Líbero, "Senapred adeuda miles de millones a proveedores").
- **IFRC Chile 27-F final appeal (MDRCL006)**: CHF 16,075,870 (~USD 16.4 M / CLP ~15.6 billion) over 36 months — but this funded shelter, cash, WASH, beyond medical only.
- **Initial DREF 27-F**: CHF 300,000 (~USD 280,000).
- **2024 Plan Nacional Prevención Incendios Forestales** (Boric, Oct 2024): CLP 156,000 M for CONAF + SENAPRED for an entire season.

For a 7-day medical response horizon affecting one region only, with say 8–10 PMAs operating most of the week:
- 8 PMAs × 7 days × CLP 10 M/day = CLP 560 M (operations)
- 8 PMAs × CLP 60 M = CLP 480 M (setup)
- Personnel surge, ambulancias, logística: CLP 2,000–4,000 M
- Strategic reserve + evacuación + hospitalización surge: CLP 2,000–3,000 M

**Recommendation**: Pres = **CLP 7,000 million (USD ~7.4 M)** as a central planning envelope for medical-PMA scope alone; sensitivity bounds CLP 4,000 M (austere) – CLP 15,000 M (peak deployment with international EMTs). Confidence: **Low–Medium**; extrapolated, because Chile does not pre-allocate a 7-day-horizon disaster budget.

## Recommendations

1. **Run the model with the central values above as the base case**, and then test sensitivity at the ±30% bounds. The model's optimal PMA siting is most sensitive to f_j (CLP 30–300 M is a 10× range) and to ratio_g, so prioritise empirical refinement of those two parameters.
2. **Replace the international cost benchmarks with Chilean licitación data** by requesting from ChileCompra the historical adjudicación values for SENAPRED's tent and emergency equipment tenders (IDs from 2014–2024). MercadoPublico permits this query at no cost; this would convert f_j and o_j from "extrapolated" to "direct".
3. **Validate H_t against MINSAL Departamento de Gestión del Riesgo en Emergencias y Desastres (DEGREYD)** by requesting their Carta de Activación for Mw ≥ 8.0 scenarios and their Equipos de Respuesta Rápida (ERR) deployment matrix.
4. **For Pres, build the model so it accepts a budget at two scales**: a "regular" Pres equal to SENAPRED Valparaíso's allocated share of the CLP 23,148 M annual budget pro-rated to the affected zone, and a "decreto de catástrofe" Pres equal to ~10× that — reflecting the Chilean reality that a Mw ≥ 8.0 triggers Ley N°21.364 emergency powers, including immediate giros presupuestarios.
5. **Treat the values as policy levers, not fixed inputs**: report results as Pareto frontiers across (a) Pres = CLP 4 B / 7 B / 15 B and (b) H_t at 75%, 100%, 125% of the central curve.

### Benchmarks that would change the recommendations

- If MINSAL or SENAPRED published a unit cost per PMA (analogous to DOH Philippines post-Haiyan reporting), replace f_j with the direct figure.
- If a future regulation mandates 4 equivalent teams as the minimum (e.g., a tightening of Norma Técnica N°17), raise req_j to 4 and rerun.
- If the Valparaíso SAMU base reaches the 4-nurse-per-shift standard demanded by the Asociación de Enfermeras (Oct 2025), H_1 can be revised upward to ~10 teams.

## Caveats

- **Chilean PMAs are not procured as standardized bundles**. Costs in this report are extrapolations from UK-Med, IFRC ERU, the Cuban Brigada Henry Reeve, and Spanish PMA equipment suppliers; they should not be quoted as official MINSAL figures.
- **SENAPRED's solvency context**: per La Tercera (Oct 2024) and SENAPRED's own oficio to the Ministerio del Interior dated 3 October 2024, the service is registered in DICOM for unpaid debts contracted during the 2 February 2024 Valparaíso megafire (135 deaths, 8,000+ homes damaged): "Actualmente, existe registro en el Directorio de Información Comercial (Dicom) por deudas contraídas en el marco de contrataciones antes reseñadas." Its operational liquidity for a future earthquake is therefore uncertain at the time of writing. The Pres value in this model assumes that the Ministerio de Hacienda will reasignar funds in the first 72 hours under Ley N°21.364, which is the historical pattern but not guaranteed.
- **WHO EMT throughput minimums (≥50 / ≥100 outpatients/day for Type-1 Mobile/Fixed) are floors, not means**. Actual deployments vary by a factor of 2–3: Singapore EMT in Myanmar 2025 reached ~225/day, while the Cuban Brigada in Chile 2010 averaged ~152 patients/day per hospital over an eight-month mission.
- **Earthquake casualty mix shifts rapidly over a 7-day horizon**, per Bar-On E, "Medical care following earthquakes: Clinical, organizational, and logistic challenges," Acta Orthop Traumatol Turc 2023;57(6):296–300 (PMC10837594, Sheba Medical Center): "by day 10, less than 50% of the patients treated will be due to earthquake-related injuries." Demand-side parameters in the optimization model should therefore taper from acute trauma toward chronic-disease decompensation across days 5–7.
- **27-F (2010) injured-and-mortality demographics** included a heavy tsunami component (181 of ~525 deaths). Valparaíso Region has its own tsunami exposure (Viña, Valparaíso ports, Algarrobo); if the model is purely seismic without tsunami, the demand-side numbers should be reduced accordingly.
- **The Mw ≥ 8.0 scenario is not specified for fault**. A Valparaíso interface megathrust (analogue to 1730/1822/1906) versus a deeper intraplate event would change the geographic distribution of demand and therefore the optimal MaxC_t and H_t curves.
- The 7-day horizon corresponds to the WHO/PAHO "acute response phase" (days 0–7) where direct-trauma demand dominates. Beyond day 7, parameters should be re-derived.