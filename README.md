# The Perfect World Cup Fantasy Team

Motor de análisis y optimización para armar la mejor plantilla posible en **FIFA World Cup
Fantasy 2026** (play.fifa.com), maximizando puntos a lo largo del torneo.

## La idea

1. **Entender las reglas a la perfección** — estructura del torneo, sistema de puntos, transfers, boosters, gestión in-play.
2. **Identificar y priorizar los factores que influyen en los puntos** — qué hace que un jugador sea "rentable".
3. **Fórmula de profitability por jugador** — score que combina proyección de puntos esperados, precio, ownership (scouting bonus), probabilidad de avance del equipo, riesgo de lesión/rotación.
4. **Modelo dinámico, no estático** — se actualiza con la información más reciente (lesiones, ratings, resultados) antes de cada deadline.
5. **Output: la plantilla óptima del momento** — optimización combinatoria sujeta a presupuesto, posiciones, límite por país y transfers disponibles.

**Estado de las tareas:** ver [ROADMAP.md](ROADMAP.md) (tracker vivo, qué está hecho y qué falta).

## Arquitectura

Es un **pipeline de decisión por CLI**, no una app web: una sola persona (Mani), 5 semanas de
vida útil, y cada ronda exige el mismo ciclo — refrescar datos → modelar → decidir → documentar.

```
play.fifa.com (JSON públicos, sin auth)──┐      data/snapshots/<fecha>/*.json
  precios · ownership · posiciones ·     ├──→   (todo dato que alimenta una        ──→  modelo        ──→  outputs/
  puntos oficiales · rondas/lockouts     │       recomendación queda versionado)        proyección +       <ronda>-reporte.md
                                         │                                              profitability +    (transfers, XI,
API-Football (key en .env)───────────────┘                                              optimizador         capitán, porqués)
  stats por jugador · injuries · odds
```

### El paquete `wcf`

`wcf` (World Cup Fantasy) es el código Python del proyecto, en `src/wcf/`, instalable con pip.
Instalarlo registra el comando de terminal `wcf` (definido en `pyproject.toml`), que es la
puerta de entrada a todo el pipeline.

```
src/wcf/
├── config.py        # paths, .env y constantes del torneo (presupuestos, límites, lockouts reales)
├── scoring.py       # tabla oficial de puntos (docs/01-reglas.md §8) como datos
├── strategy.py      # dial de riesgo (WCF_RISK), horizonte y peso del prior histórico (docs/05)
├── store.py         # snapshots versionables: save/load en data/snapshots/<fecha>/
├── pool.py          # capa de datos: une pool + selecciones + fixtures de la próxima ronda
├── myteam.py        # parsea data/my-team.md y lo valida contra el pool oficial
├── historical.py    # priors WC2022 (free tier) para P7, acotados a selecciones vivas y peso bajo
├── projection.py    # proyección v0 de pts esperados + ranking de profitability (FIFA + matchup + prior)
├── cli.py           # comandos `wcf <comando>` (argparse)
└── sources/
    ├── fifa_fantasy.py   # endpoints públicos del juego: players/squads/rounds.json
    ├── api_football.py   # cliente API-Football (throttled): histórico 2022-24; el 2026 es de pago
    └── news.py           # noticias vía RSS (BBC/Guardian/Sky), gratis, filtradas por entidad
```

Capas y regla de dependencia: `sources/` (HTTP crudo) → `store` (persistencia) → modelo
(proyección/ranking, llega en Fase 2) → `cli` (orquesta). Los módulos de modelo nunca llaman
HTTP directo: leen snapshots, para que toda recomendación sea reproducible después (backtest).

### Decisiones de stack

| Decisión | Porqué |
|---|---|
| Python 3.12+, deps mínimas (`requests`, `python-dotenv`) | Lo que el problema pide hoy; `pandas` entra en Fase 2 y `pulp` (ILP) en Fase 4 |
| JSON versionado en git como "base de datos" | Datos diminutos (~1.500 jugadores); reproducibilidad gratis; sin servidor que mantener |
| CLI + reportes markdown, sin UI | El deliverable es una decisión documentada antes de cada lockout, no una interfaz |
| play.fifa.com como fuente primaria | Endpoints públicos sin auth con los datos que nadie más tiene (ownership, precios, posiciones del juego, puntos oficiales) — descubierto 2026-06-12 |
| API-Football solo para lo que FIFA no da | Stats granulares (tiros, tackles, chances), injuries, odds |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env        # pegar API_FOOTBALL_KEY (gratis en dashboard.api-football.com)
```

### Comandos

| Comando | Hace | Necesita key |
|---|---|---|
| `wcf pool` | Snapshot del pool fantasy: 1.487 jugadores con precio, posición y ownership | No |
| `wcf rounds` | Las 8 rondas con lockouts reales y fixtures, desde el juego | No |
| `wcf myteam` | Valida `data/my-team.md` contra el pool (precios, posiciones, límites, presupuesto) | No |
| `wcf matchups` | Fixtures de la próxima ronda para tu squad: rival, horario, ownership, flag scouting <5% | No |
| `wcf status` | Plan y cuota usada de API-Football | Sí |
| `wcf history` | Baja priors históricos (WC2022) de selecciones vivas — acotado, cacheado, resumible | Sí (histórico) |
| `wcf news` | Titulares RSS gratis (BBC/Guardian/Sky) filtrados a tu squad (P1: lesiones/rotación) | No |
| `wcf rank` | Ranking de profitability (proyección v0) para la próxima ronda: `--by value\|proj`, `--pos`, `--risk` | No |
| `wcf fixtures` / `injuries` / `players` | Datos en vivo de API-Football **(plan pago — 2026 bloqueado en Free)** | Sí (pago) |

Ritual mínimo por ronda: `wcf pool` antes de cada lockout (el ownership cambia intradía) — todo
queda en `data/snapshots/<fecha>/` para auditar después qué sabía el modelo al recomendar.

## Documentación

| Doc | Qué contiene |
|---|---|
| [ROADMAP.md](ROADMAP.md) | **Tracker vivo**: tareas por fase, qué está hecho, brainstorm pendiente del loop de optimización |
| [docs/00-onboarding.md](docs/00-onboarding.md) | El juego explicado desde cero y su conexión con este proyecto |
| [docs/01-reglas.md](docs/01-reglas.md) | Reglas **oficiales** completas (fuente: FIFA, verificado 2026-06-11) |
| [docs/02-factores-de-puntos.md](docs/02-factores-de-puntos.md) | Los 10 factores priorizados + borrador de la fórmula de profitability |
| [docs/03-fuentes-de-datos.md](docs/03-fuentes-de-datos.md) | Fuentes y endpoints (incluye los descubiertos de play.fifa.com) |
| [docs/04-plan-de-ejecucion.md](docs/04-plan-de-ejecucion.md) | El porqué de cada fase, anclado a los deadlines reales, y los principios de trabajo |

## El torneo de un vistazo (reglas oficiales)

| Ronda | Lockout (UTC+1) | Transfers libres antes | Máx. jugadores/país |
|---|---|---|---|
| MD1 | 11 jun 20:00 (en juego) | Ilimitadas | 3 |
| MD2 | **18 jun 17:00** | 2 | 3 |
| MD3 | 24 jun 20:00 | 2 (+1 rollover) | 3 |
| R32 | 28 jun 20:00 | **Ilimitadas** | **3** |
| R16 | 4 jul 18:00 | 4 | 4 |
| QF | 9 jul 21:00 | 4 | 5 |
| SF | 14 jul 20:00 | 5 | 6 |
| F | 18 jul 22:00 | 6 | 8 |

Presupuesto: $100M, sube a **$105M** al abrir el R32. Precios fijos todo el torneo. Transfer
extra: **−3 pts**. Scouting bonus: **+2** si el jugador hace >4 pts y está en <5% de equipos.

## Contexto de juego (Mani)

- Equipo MD1 ya inscrito (en juego desde el 11 jun). Próxima decisión: **transfers de MD2**.
- Compitiendo en mini-league privada con amigos.
- Estado del equipo: [data/my-team.md](data/my-team.md) (validar con `wcf myteam`).
