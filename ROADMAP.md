# ROADMAP — tracker vivo del proyecto

> **Única fuente de verdad del estado de las tareas.** Se actualiza al completar cada una.
> El *porqué* de cada fase y los principios de trabajo viven en
> [docs/04-plan-de-ejecucion.md](docs/04-plan-de-ejecucion.md).

**Ahora:** Fase 1 cerrada salvo la key de API-Football (Mani). Fase 2 en marcha: loop de
optimización diseñado, falta proyección v0.
**Próximo deadline: lockout MD2 — 18 jun 2026, 17:00 (UTC+1).** Fuente viva: `wcf rounds`.

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
- [ ] **Mani:** crear cuenta API-Football y pegar la key en `.env` *(no bloquea el MVP de MD2 —
      ver hallazgo en [docs/05](docs/05-loop-de-optimizacion.md): FIFA solo alcanza para v0)*
- [ ] Validar cobertura API-Football WC2026: stats por jugador en selecciones, `injuries`,
      cuota del free tier → decidir si toca plan pago *(mejora, no prerrequisito)*
- [ ] *(opcional, fuera del camino crítico)* Evaluar news aggregator de RapidAPI

## Fase 2 — MVP de decisión para MD2 (→ 18 jun 17:00 UTC+1)

- [x] **Diseño del loop de optimización dinámica** → [docs/05](docs/05-loop-de-optimizacion.md)
      *(2026-06-13)*
- [x] Decisiones de estrategia (Mani): horizonte **lookahead por bloque** + apetito de riesgo
      **moderate, dial ajustable** (`WCF_RISK`) → `src/wcf/strategy.py` *(2026-06-13)*
- [x] Capa de datos `pool.py` + `wcf matchups`: fixtures de la próxima ronda para mi squad
      (rival, horario, flag scouting <5%) *(2026-06-13)*
- [ ] Proyección v0 de puntos esperados por jugador para MD2 (heurística, sin ML; sale con
      datos de FIFA solos: `roundPoints` + `form` + matchup de `rounds.json`).
      *Calidad plena recién el 18 jun, cuando MD1 cierre y haya 1 dato real por jugador.*
- [ ] Ranking de profitability v0: proyección + flag scouting (<5% y P(pts≥5)) + horizonte MD3
- [ ] Recomendador de transfers: mejor par salir/entrar con las 2 libres (+rollover), con justificación
- [ ] Plan de capitanía MD2: orden de switches por horario con umbrales stick-or-twist
- [ ] Reporte legible en `outputs/md2-reporte.md`
- [ ] Refresco pre-lockout: `wcf pool` justo antes de decidir (ownership al día)

## Fase 3 — Pipeline repetible (→ 24 jun 20:00 UTC+1)

- [ ] `wcf report`: refresh → ranking → reporte de ronda, en un comando
- [ ] Tracking de ownership entre deadlines (`roundsSelected` ya viene en `players.json` — validar si basta)
- [ ] Decisión Wildcard: ¿se justifica en MD3 o se guarda para octavos+?
- [ ] Backtest informal: proyección v0 de MD2 vs puntos reales → primera recalibración de pesos

## Fase 4 — El gran reset: optimizador R32 (→ 28 jun 20:00 UTC+1)

- [ ] Optimizador ILP (PuLP): maximizar pts esperados sujeto a $105M, 2/5/5/3, máx 3/país, formaciones válidas
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
