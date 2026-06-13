# Fuentes de datos y APIs

Mapa de qué dato necesita el modelo (según [02-factores-de-puntos.md](02-factores-de-puntos.md))
y de dónde sale. Estado: **validado 2026-06-13.** Conclusión: **el pool de FIFA es la única
fuente accesible para el Mundial 2026 con el plan actual** — API-Football queda detrás de un
plan pago (ver §1). El MVP de grupos corre 100% con datos de FIFA.

## Fuentes identificadas

### 1. API-Football (v3.football.api-sports.io) — stats granulares, **detrás de plan pago**

API de API-Sports. Base URL `https://v3.football.api-sports.io`, auth header `x-apisports-key`.
Cliente en `src/wcf/sources/api_football.py`.

**Validación 2026-06-13 (key Free, 100 req/día):**

- ✅ El Mundial es **liga id=1**, season **2026** existe, con cobertura declarada:
  `fixtures`, `lineups`, `players stats`, `odds`, `predictions` = **True**.
- ❌ **`injuries` = False para el Mundial.** No hay endpoint de lesiones para este torneo, ni
  siquiera pagando.
- 🔒 **El plan Free NO da acceso a la season 2026** (solo histórico 2022-2024). Confirmado por el
  error del API: *"Free plans do not have access to this season, try from 2022 to 2024."* Toda
  llamada a fixtures/players/odds del Mundial 2026 requiere **plan pago**.

| Endpoint | Dato que aporta | Factor | Disponible |
|---|---|---|---|
| `fixtures` | Calendario, horarios, resultados | P2, P6 | 🔒 pago (FIFA `rounds.json` lo cubre gratis) |
| `fixtures/lineups` | Alineaciones confirmadas (~20-40 min antes) | P1 | 🔒 pago (FIFA `matchStatus` aproxima) |
| `players/statistics` | Tiros, tackles, key passes, minutos por jugador | P3, P7, P8 | 🔒 pago — **lo que FIFA NO da** |
| `injuries` | Lesionados/sancionados | P1 | ❌ no cubierto |
| `odds` | Cuotas (ganador, goles) | P2, P4 | 🔒 pago |
| `predictions` | Forma, h2h, fuerza | P2, P4 | 🔒 pago |

- **Decisión de costo (abierta, no urgente):** el MVP corre sin esto. API-Football solo aporta si
  pagamos, y su valor diferencial son **stats granulares** (mejor proyección P3/P7) y **odds**
  (mejor dificultad de matchup P2/P4) — NO lesiones. Recomendación: evaluar el upgrade recién
  para el **reset del R32** (máximo apalancamiento), no antes.

#### 1b. Histórico del free tier (2022-2024) como prior de baja confianza ✅

Aunque el 2026 en vivo está bloqueado, **el free tier SÍ da histórico 2022-2024 con stats
granulares** (validado: tiros, key passes, tackles, tarjetas por jugador). Lo usamos para tapar
el único hueco (P7) con *priors*. Módulo `src/wcf/historical.py`, comando `wcf history`.

- **Fuente v1:** Mundial 2022 (`league=1, season=2022`) — contexto de selección, lo más comparable.
- **Acotado y evolutivo** (decisión de Mani): solo se bajan las selecciones **vivas** relevantes
  para la ronda; al eliminarse equipos, salen del set. Se baja **por equipo** (no de a 1.500
  jugadores): `teams?league=1&season=2022` da el mapa nación→id en 1 request, luego
  `players?team=<id>&season=2022` por selección.
- **Inmutable y cacheado:** el histórico no cambia → cada selección se baja una vez a
  `data/historical/2022/team-<id>.json` y no se vuelve a pedir. Fetch **resumible** y **throttled**
  (free tier ~10 req/min, 100 req/día).
- **Peso BAJO y decayente** (decisión de Mani): el prior entra con shrinkage bayesiano
  (`strategy.HIST_PRIOR_STRENGTH` ≈ 1 partido de evidencia) y el rendimiento 2026 lo diluye ronda
  a ronda (1 partido → 50%, 3 → 25%). Un jugador pudo cambiar de nivel desde 2022: el histórico
  **nunca domina** la plantilla óptima.
- **Cobertura parcial aceptada:** selecciones que no jugaron el WC2022 (p. ej. Noruega, Colombia)
  usan prior por defecto de posición. Dado el peso bajo, es tolerable; se podría enriquecer con
  Euro/Copa 2024 (también en el free tier) más adelante.

### 2. Noticias vía RSS — gratis, sin API key ✅ (reemplaza al agregador de pago de RapidAPI)

RapidAPI ofrece agregadores de noticias, pero son de pago. **Alternativa gratis y sencilla,
validada 2026-06-13: RSS de medios confiables.** Módulo `src/wcf/sources/news.py`, comando
`wcf news`.

| Fuente | Feed RSS | Estado |
|---|---|---|
| BBC Sport | `feeds.bbci.co.uk/sport/football/rss.xml` | ✅ ~87 ítems |
| The Guardian | `theguardian.com/football/rss` | ✅ ~62 ítems |
| Sky Sports | `skysports.com/rss/12040` | ✅ ~20 ítems |

- **Uso (P1):** señal cualitativa *forward-looking* de lesiones/rotación — el único canal de
  lesiones que tenemos, dado `injuries=False` en API-Football (§1).
- **Filtrado a entidades:** `wcf news` cruza los titulares con los apellidos de mi squad (señal
  alta) y sus naciones (contexto, más ruidoso), y los separa. Robusto: 3 fuentes; si una cae, las
  demás siguen. Snapshot a `data/snapshots/`.
- **Limitación conocida:** el match por nación genera falsos positivos (p. ej. "Spain" matchea F1
  o dardos). Por eso la sección de jugadores va aparte; la de naciones se marca "ruido posible".
  Para el MVP la lectura final es manual/asistida — el comando reduce el universo, no decide.
- **Descartado:** Reddit r/soccer JSON (403, ya exige auth). Ampliable con más feeds en `FEEDS`.

### 3. El propio juego (play.fifa.com) — datos fantasy que NINGUNA otra fuente tiene

**✅ Endpoints descubiertos (2026-06-12): JSON estáticos públicos, SIN auth.** Cliente en
`src/wcf/sources/fifa_fantasy.py`; snapshot con `wcf pool` y `wcf rounds`.

| Endpoint (`play.fifa.com/json/fantasy/`) | Trae | Alimenta |
|---|---|---|
| `players.json` | Pool completo (~1.487): **precio**, **posición del juego**, **percentSelected** total Y por ronda, puntos oficiales, form, status, squadId | P5, P9, P3, backtest |
| `squads.json` | Las 48 selecciones: grupo, abbr, `isEliminated` | P2 |
| `rounds.json` | Las 8 rondas con **fechas exactas (lockout = startDate)** y fixtures con estadio, horario, marcador, status | P6, deadlines |

- Otros nombres probados (`fixtures`, `settings`, `constants`, `teams`, ...) → 403. Solo esos
  tres están abiertos, y cubren todo lo que necesitábamos de esta fuente.
- `percentSelected` cambia entre deadlines → correr `wcf pool` antes de CADA lockout (y queda
  el histórico en `data/snapshots/<fecha>/`).
- **Señal de disponibilidad (P1), el workaround del hueco de lesiones** (validado 2026-06-13):
  - `status`: `playing` (1.247) vs `transferred` (240) → "transferred" = fuera del pool del
    torneo (no convocado / lesionado de salida). Filtro duro de candidatos.
  - `matchStatus`: `start` / `sub` / `not_in_squad` → señal de alineación de la ronda en curso
    (se puebla cerca del partido). Aproxima los lineups que API-Football cobra.
- Bonus: `rounds.json` también da fixtures/resultados gratis. Con esto, **FIFA cubre P1
  (parcial), P2 (matchups), P5, P6 y P9 sin API-Football**; lo único que FIFA no da son stats
  granulares (tiros/tackles/key passes) y odds.

### 4. Candidatas de respaldo (si falta algo)

- **FBref / FotMob / SofaScore** — stats avanzadas (xG, xA, key passes) si API-Football queda corto
  en selecciones; sería scraping, evaluar términos de uso.
- **Cuotas de avance del torneo** (outright odds) — para P2 si `odds` de API-Football no cubre
  mercados de avance de ronda; alternativa: simulación propia del bracket con Elo.

## Matriz factor → fuente (post-validación)

Reordenada a la realidad: FIFA es primaria; API-Football es **mejora opcional con plan pago**.

| Factor | Fuente primaria (accesible hoy) | Mejora (API-Football pago) |
|---|---|---|
| P1 Minutos/disponibilidad | FIFA `status` + `matchStatus` | lineups (confirmación ~30 min antes) |
| P2 Avance del equipo | FIFA matchups + **simulación Elo propia** | odds, predictions |
| P3 Goal involvement | FIFA `roundPoints` + `form` (señal cruda) | players stats (tiros, xG-proxy) |
| P4 Clean sheet | FIFA `roundPoints` por posición | odds de goles, stats defensivas |
| P5 Ownership <5% | **FIFA (único)** | — |
| P6 Horario fixtures | **FIFA `rounds.json`** | — |
| P7 Volumen estadístico | — *(FIFA no lo da)* | players stats (clave del upgrade) |
| P8 Disciplina | FIFA `roundPoints` (refleja el −1/−2) | players stats (tarjetas p90) |
| P9 Precios | **FIFA (único, captura una vez)** | — |

Lectura: P7 (volumen de tiros/tackles/chances) es el único factor que **hoy no podemos medir** —
se aproxima vía `form`/`roundPoints` hasta que (si) se pague API-Football. Lo demás está cubierto.

## Claves / secretos

API keys en `.env` (gitignored), nunca en el repo. Plantilla en `.env.example` cuando exista código.
