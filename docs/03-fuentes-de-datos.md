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

### 2. Football News Aggregator Live (RapidAPI)

`rapidapi.com/arkasarkar2000/api/football-news-aggregator-live` — noticias agregadas de medios.

- **Uso:** señal cualitativa para P1 — rumores de rotación, lesiones de último minuto, ruedas de
  prensa ("X no se entrenó hoy"), antes de que aparezcan en datos estructurados.
- **Rol elevado:** como API-Football no cubre `injuries` del Mundial (§1), esta sería la única
  fuente *forward-looking* de lesiones; aun así, para el MVP la revisión puede ser manual/asistida.
- **Pendiente validar:** qué medios agrega, latencia, filtro por selección/jugador, cuánto ruido.

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
