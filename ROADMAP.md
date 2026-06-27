# ROADMAP — tracker vivo del proyecto

> **Única fuente de verdad del estado de las tareas.** Se actualiza al completar cada una.
> El *porqué* de cada fase y los principios de trabajo viven en
> [docs/04-plan-de-ejecucion.md](docs/04-plan-de-ejecucion.md).

**Ahora:** Fase 1 ✅ y Fase 2 ✅ cerradas — el pipeline corre end-to-end (`wcf report`). **Realidad
del torneo al 26 jun (`wcf rounds`):** rondas 1 y 2 completas, **ronda 3 en juego**, **ronda 4 es el
próximo lockout: 28 jun 2026, 20:00 (UTC+1)**. Las rondas 2 y 3 pasaron **sin correr el pipeline en
el repo** (decisiones tomadas a mano en el juego), así que el "refresco pre-MD2" del plan original
quedó superado por los hechos. **Pendiente clave:** la ronda 4 es el **R32, el gran reset** (transfers
ilimitadas, budget $105M). Ya está listo el **optimizador ILP** (`wcf optimize`, Fase 4 adelantada);
correrlo cuando R3 cierre y el bracket esté fijado, antes del lockout del 28 jun. Luego, Fase 3
(pipeline de un comando + backtest v0 vs puntos reales).
**Próximo deadline: lockout ronda 4 — 28 jun 2026, 20:00 (UTC+1).** Fuente viva: `wcf rounds`.

---

## Fase 1 — Base de datos del torneo (→ 14 jun)

- [x] Esqueleto del repo: paquete `wcf`, CLI, venv, `.env.example` *(2026-06-12)*
- [x] Endpoints fantasy de FIFA descubiertos — públicos, sin auth — y cliente operativo *(2026-06-12)*
- [x] Snapshot inicial: pool (1.487 jugadores con precio/posición/ownership) + rondas con
      lockouts reales → `data/snapshots/2026-06-12/` *(2026-06-12)*
- [x] Verificado que `players.json` es **data viva**: puntos oficiales cargados por partido,
      ownership cambia intradía *(2026-06-12)*
- [x] `wcf myteam`: validador de la plantilla contra el pool oficial *(2026-06-12)*
- [x] Squad MD1 completo y validado: 15/15, $99.3M, 4-3-3 *(2026-06-13, commit f121d22)*
- [x] **Mani:** key de API-Football en `.env` *(2026-06-13)*
- [x] Validar cobertura API-Football WC2026 *(2026-06-13)*: liga id=1 + season 2026 OK, pero
      **el plan Free NO accede a 2026** (solo 2022-2024) e **`injuries` no se cubre** ni pagando.
      → El Mundial requiere plan pago; FIFA queda como única fuente accesible. Detalle en
      [docs/03](docs/03-fuentes-de-datos.md). **Decisión de upgrade diferida al R32.**
- [x] Noticias *forward-looking* (P1, único canal de lesiones dado `injuries=False`): en vez del
      RapidAPI de pago, **RSS gratis** (BBC/Guardian/Sky) → `sources/news.py` + `wcf news`,
      filtrado a entidades del squad *(2026-06-13)*

## Fase 2 — MVP de decisión para MD2 (→ 18 jun 17:00 UTC+1)

- [x] **Diseño del loop de optimización dinámica** → [docs/05](docs/05-loop-de-optimizacion.md)
      *(2026-06-13)*
- [x] Decisiones de estrategia (Mani): horizonte **lookahead por bloque** + apetito de riesgo
      **moderate, dial ajustable** (`WCF_RISK`) → `src/wcf/strategy.py` *(2026-06-13)*
- [x] Capa de datos `pool.py` + `wcf matchups`: fixtures de la próxima ronda para mi squad
      (rival, horario, flag scouting <5%) *(2026-06-13)*
- [x] Priors históricos (WC2022) para tapar P7: módulo `historical.py` + `wcf history`, acotado
      a selecciones vivas, cacheado/resumible/throttled, **peso bajo decayente**
      (`strategy.blend_rate`). Cobertura: **26 selecciones cacheadas, 10/15 de mi squad con prior**
      (los 5 sin prior no jugaron el WC2022). *(2026-06-13)*
- [x] Proyección v0 de puntos esperados (`projection.py`): top-down FIFA (avgPoints/form + prior
      por precio con shrinkage) × disponibilidad (P1) × matchup, + término de volumen del prior
      histórico (P7, peso bajo). Constantes v0 calibrables tras MD1 *(2026-06-13)*
- [x] Fuerza de selección v0 = proxy por precio del top-15 (z-scores) → matchup. *(Elo con
      histórico free queda como mejora futura.)* *(2026-06-13)*
- [x] Ranking de profitability + `wcf rank` (`--by value|proj`, `--pos`, `--risk`): marca squad y
      scouting <5% *(2026-06-13)*
- [x] Recomendador de transfers (`recommender.py` + `wcf transfers`): greedy del mejor par
      salir/entrar sujeto a posición/presupuesto/máx-país, con umbral del dial de riesgo y
      justificación; "plantarse" es salida válida *(2026-06-13)*
- [x] Plan de capitanía: capitán/vice = top-2 proyección del XI, con timing de kickoff (P6) para
      la ventana de switch *(2026-06-13)*
- [x] Selección de XI + formación óptima (maximiza proyección entre las 7 válidas) + orden de
      banca para auto-subs *(2026-06-13)*
- [x] Reporte completo `outputs/md2-reporte.md` vía `wcf report` (transfers + XI + capitán +
      banca) *(2026-06-13)*
- [~] ~~Refresco pre-lockout (18 jun) con MD1 cerrado~~ — **superado:** las rondas 2 y 3 se
      decidieron a mano en el juego sin correr el repo. El primer refresco real del pipeline se hace
      ahora para la **ronda 4** (ver abajo). *(2026-06-26)*
- [x] Squad real actualizado en `data/my-team.md` y validado con `wcf myteam` (15/15, $99.3M,
      quedan $0.7M) — entrando a ronda 4 *(2026-06-26)*

## Fase 3 — Pipeline repetible (→ 24 jun 20:00 UTC+1)

- [ ] `wcf report`: refresh → ranking → reporte de ronda, en un comando
- [ ] Tracking de ownership entre deadlines (`roundsSelected` ya viene en `players.json` — validar si basta)
- [ ] Decisión Wildcard: ¿se justifica en MD3 o se guarda para octavos+?
- [ ] Backtest informal: proyección v0 de MD2 vs puntos reales → primera recalibración de pesos

## Fase 4 — El gran reset: optimizador R32 (→ 28 jun 20:00 UTC+1)

- [x] Optimizador ILP (PuLP): maximizar pts esperados sujeto a $105M, 2/5/5/3, máx 3/país,
      formaciones válidas → `src/wcf/optimizer.py` + `wcf optimize`. Modelo de dos niveles
      (squad + XI + capitán x2); reusa `report.select_xi`. Validado: 15/15, composición y cap
      exactos, formación válida. *(2026-06-26)*
- [ ] Modelo de avance multi-ronda (odds de casas o simulación Elo del bracket)
- [ ] Valor de opcionalidad por horario dentro de la ronda (P6)
- [ ] Plan de boosters del knockout (incluye el Mystery, que se revela al abrir el R32)
- [ ] Reporte R32: squad nuevo desde cero, justificado por jugador

## Fase 5 — Knockout + asistente in-play (4 jul → 18 jul)

- [ ] Loop por ronda: refresh → proyección → transfers limitadas (4/4/5/6) → reporte
- [ ] Asistente in-play: sub manual / captain switch / plantarse, por valor esperado
      (ojo: el primer cambio manual mata auto-subs y fallback del vice)
- [ ] Recalibrar proyecciones con los datos del propio torneo (3-4 partidos por selección)

## Fase 6 — Post-mortem (después de la final, 19 jul)

- [ ] Backtest completo: puntos del modelo vs míos vs ganador de la mini-league
- [ ] Documentar qué funcionó → base para Champions fantasy / FPL / WC 2030

---

## Loop de optimización — ✅ diseñado en [docs/05](docs/05-loop-de-optimizacion.md)

Cadencia de refresco, triggers de re-decisión, calibración y el ritual por ronda quedaron
resueltos ahí. **Faltan 2 decisiones de Mani** antes de construir la proyección v0:

1. **Horizonte:** greedy por ronda vs lookahead por bloque *(recomendado: lookahead, peso 1.0 al
   próximo MD y ~0.5 al siguiente)*.
2. **Apetito de riesgo:** conservador / moderado / agresivo — fija los umbrales de transfer y
   cuánto perseguir el ownership <5% *(default propuesto: moderado)*.
