# The Perfect World Cup Fantasy Team

Motor de análisis y optimización para armar la mejor plantilla posible en **FIFA World Cup Fantasy 2026** (play.fifa.com), maximizando puntos a lo largo del torneo.

## La idea

1. **Entender las reglas a la perfección** — estructura del torneo, sistema de puntos, transfers, boosters, gestión in-play.
2. **Identificar y priorizar los factores que influyen en los puntos** — qué hace que un jugador sea "rentable".
3. **Fórmula de profitability por jugador** — score que combina proyección de puntos esperados, precio, ownership (scouting bonus), probabilidad de avance del equipo, riesgo de lesión/rotación.
4. **Modelo dinámico, no estático** — se actualiza con la información más reciente (lesiones, ratings, resultados) vía APIs antes de cada deadline.
5. **Output: la plantilla óptima del momento** — optimización combinatoria sujeta a presupuesto, posiciones, límite por país y transfers disponibles.

## Documentación

| Doc | Qué contiene |
|---|---|
| [docs/00-onboarding.md](docs/00-onboarding.md) | El juego explicado desde cero (para quien nunca jugó fantasy) y su conexión con este proyecto |
| [docs/01-reglas.md](docs/01-reglas.md) | Reglas **oficiales** completas (fuente: FIFA, verificado 2026-06-11) + discrepancias vs. la guía de FPL Mate |
| [docs/02-factores-de-puntos.md](docs/02-factores-de-puntos.md) | Los 10 factores priorizados que influyen en los puntos + borrador de la fórmula de profitability |
| [docs/03-fuentes-de-datos.md](docs/03-fuentes-de-datos.md) | APIs y fuentes: API-Football, news aggregator, endpoints del propio juego (ownership, precios) |
| [docs/04-plan-de-ejecucion.md](docs/04-plan-de-ejecucion.md) | Plan por fases anclado a los deadlines reales del torneo |

## Estado

- [x] **Fase 0** — Reglas oficiales documentadas, factores priorizados, onboarding, mapa de datos
- [ ] **Fase 1** — Base de datos: API-Football validada, endpoints fantasy descubiertos, equipo actual registrado (→ 14 jun)
- [ ] **Fase 2** — MVP de decisión para las transfers del MD2 (→ deadline MD2, ~18 jun)
- [ ] **Fase 3** — Pipeline repetible por ronda (→ deadline MD3)
- [ ] **Fase 4** — Optimizador completo para el gran reset del Round of 32
- [ ] **Fase 5** — Loop de knockout + asistente in-play
- [ ] **Fase 6** — Post-mortem y backtest

## El torneo de un vistazo (reglas oficiales)

| Ronda | Fase | Transfers libres antes | Máx. jugadores/país |
|---|---|---|---|
| MD1 | Grupos R1 (desde 11 jun 2026) | Ilimitadas | 3 |
| MD2 | Grupos R2 | 2 | 3 |
| MD3 | Grupos R3 | 2 (+1 rollover) | 3 |
| R32 | Dieciseisavos | **Ilimitadas** | **3** |
| R16 | Octavos | 4 | 4 |
| QF | Cuartos | 4 | 5 |
| SF | Semifinales | 5 | 6 |
| F | Final | 6 | 8 |

Presupuesto: $100M, sube a **$105M** al abrir el R32. Precios fijos todo el torneo. Transfer extra: **−3 pts**. Scouting bonus: **+2** si el jugador hace >4 pts y está en <5% de equipos.

## Contexto de juego (Mani)

- Equipo MD1 ya inscrito (en juego desde el 11 jun). Próxima decisión: **transfers de MD2**.
- Compitiendo en mini-league privada con amigos.
