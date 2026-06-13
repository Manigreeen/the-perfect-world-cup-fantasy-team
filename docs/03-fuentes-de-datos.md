# Fuentes de datos y APIs

Mapa de qué dato necesita el modelo (según [02-factores-de-puntos.md](02-factores-de-puntos.md))
y de dónde sale. Estado: **por validar** — antes de construir nada hay que confirmar cobertura
real del Mundial 2026 en cada fuente (ver Fase 1 del [plan](04-plan-de-ejecucion.md)).

## Fuentes identificadas

### 1. API-Football (api-football.com) — fuente principal de stats

API de API-Sports. Endpoints relevantes para nosotros:

| Endpoint | Dato que aporta | Factor que alimenta |
|---|---|---|
| `fixtures` | Calendario, horarios, resultados | P2, P6 (horario dentro de la ronda) |
| `fixtures/lineups` | Alineaciones confirmadas (~20-40 min antes) | P1 (minutos) |
| `players` / `players/statistics` | Goles, asistencias, tiros, tackles, key passes, minutos, tarjetas por jugador | P3, P7, P8 |
| `injuries` | Lesionados y sancionados por equipo/fixture | P1 |
| `predictions` | Predicción del partido (forma, h2h, fuerza) | P2, P4 |
| `odds` | Cuotas de casas (ganador, goles) | P2, P4 (clean sheet implícito vía goles esperados) |
| `events` | Eventos en vivo (goles, tarjetas, cambios) | Gestión in-play |
| `standings` | Posiciones de grupo | P2 |

- **Pendiente validar:** id de liga del World Cup 2026, profundidad de stats por jugador en
  selecciones (las stats de club suelen ser más ricas que las de torneos internacionales),
  límites del plan (free tier ~100 requests/día — probablemente haga falta plan pago durante
  el torneo), y si `injuries` cubre selecciones.

### 2. Football News Aggregator Live (RapidAPI)

`rapidapi.com/arkasarkar2000/api/football-news-aggregator-live` — noticias agregadas de medios.

- **Uso:** señal cualitativa para P1 — rumores de rotación, lesiones de último minuto, ruedas de
  prensa ("X no se entrenó hoy"), antes de que aparezcan en datos estructurados.
- **Pendiente validar:** qué medios agrega, latencia, si se puede filtrar por selección/jugador,
  y cuánto ruido trae. Es complemento, no fuente primaria.

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
- Bonus inesperado: `rounds.json` también sirve de respaldo de fixtures/resultados, reduciendo
  la dependencia de API-Football a stats por jugador, injuries y odds.

### 4. Candidatas de respaldo (si falta algo)

- **FBref / FotMob / SofaScore** — stats avanzadas (xG, xA, key passes) si API-Football queda corto
  en selecciones; sería scraping, evaluar términos de uso.
- **Cuotas de avance del torneo** (outright odds) — para P2 si `odds` de API-Football no cubre
  mercados de avance de ronda; alternativa: simulación propia del bracket con Elo.

## Matriz factor → fuente

| Factor | Fuente primaria | Respaldo |
|---|---|---|
| P1 Minutos | API-Football (lineups, injuries) | News aggregator |
| P2 Avance del equipo | API-Football (odds, predictions, standings) | Simulación Elo propia |
| P3 Goal involvement | API-Football (players stats) | FBref/FotMob |
| P4 Clean sheet | API-Football (odds de goles, stats defensivas) | — |
| P5 Ownership <5% | **play.fifa.com (único)** | — |
| P6 Horario fixtures | API-Football (fixtures) | Calendario oficial FIFA |
| P7 Volumen estadístico | API-Football (players stats) | FBref/FotMob |
| P8 Disciplina | API-Football (players stats) | — |
| P9 Precios | **play.fifa.com (único, captura una vez)** | — |

## Claves / secretos

API keys en `.env` (gitignored), nunca en el repo. Plantilla en `.env.example` cuando exista código.
