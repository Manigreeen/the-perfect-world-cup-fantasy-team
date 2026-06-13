# ROADMAP — tracker vivo del proyecto

> **Única fuente de verdad del estado de las tareas.** Se actualiza al completar cada una.
> El *porqué* de cada fase y los principios de trabajo viven en
> [docs/04-plan-de-ejecucion.md](docs/04-plan-de-ejecucion.md).

**Ahora:** cerrando Fase 1, arrancando Fase 2.
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
- [ ] **Mani:** completar [data/my-team.md](data/my-team.md) (va 3/15) — validar con `wcf myteam`
- [ ] **Mani:** crear cuenta API-Football y pegar la key en `.env`
- [ ] Validar cobertura API-Football WC2026: stats por jugador en selecciones, `injuries`,
      cuota del free tier → decidir si toca plan pago
- [ ] *(opcional, fuera del camino crítico)* Evaluar news aggregator de RapidAPI

## Fase 2 — MVP de decisión para MD2 (→ 18 jun 17:00 UTC+1)

- [ ] **Brainstorm: loop de optimización dinámica** (preguntas abajo) → decisión en `docs/05-loop-de-optimizacion.md`
- [ ] Proyección v0 de puntos esperados por jugador para MD2 (heurística, sin ML)
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

## Brainstorm pendiente — cómo se adapta la estrategia (optimización dinámica)

La data es viva (FIFA carga puntos tras cada partido y el ownership cambia intradía), pero la
estrategia **no debe ser nerviosa**: las transfers son escasas y el hit cuesta −3. Preguntas a
resolver en el brainstorm (primera tarea de Fase 2):

1. **Cadencia de refresco:** ¿`wcf pool` 1× al día + siempre justo antes del lockout? ¿stats de
   API-Football solo tras cada matchday? ¿injuries diario únicamente en ventana de decisión?
2. **Triggers de re-decisión:** ¿qué cambio amerita recalcular el plan? (lesión/banca de un
   titular propio, caída de proyección sobre un umbral, un target cruzando el 5% de ownership)
3. **Horizonte:** ¿greedy por ronda o lookahead por bloque (grupos / R32→final)? ¿cuánto pesa
   la ronda siguiente vs las posteriores?
4. **Calibración:** tras cada ronda, comparar proyección vs puntos oficiales (vienen en
   `players.json`) y ajustar pesos. ¿Proceso manual documentado o automático?
5. **Estabilidad vs reactividad:** umbral mínimo de ganancia esperada para justificar una
   transfer (¿+X pts proyectados sobre el que sale?) y para romper el plan de capitanía.

Resultado esperado: `docs/05-loop-de-optimizacion.md` con cadencia, triggers y umbrales decididos.
