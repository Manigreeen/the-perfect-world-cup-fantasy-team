# Handoff — World Cup Fantasy

> Memoria viva del repo para retomar sin perder el hilo. El detalle de fases y el tracker de
> tareas viven en [ROADMAP.md](../../ROADMAP.md); este doc apunta a artefactos, no los copia.

## Memory

### 2026-06-26 — Registro R3, realineación al torneo real y optimizador ILP (Fase 4)

**Contexto que cambió todo:** el ROADMAP apuntaba a "MD2 / 18 jun", pero `wcf rounds` mostró que el
torneo ya iba en **ronda 3 (en juego)** y que el próximo lockout real es **ronda 4 = R32, 28 jun
20:00 UTC+1 (= 14:00 hora Colombia)**. Las rondas 2 y 3 se decidieron a mano en el juego, sin correr
el repo. Todo se realineó a esa realidad.

**Qué se hizo:**
- **Squad real registrado.** Mani pasó su equipo vigente (distinto al de MD1: entraron L. Martínez,
  Molina, Freeman, Manzambi; salieron Elvedi, Stanisic, Mojica, Gravenberch). Volcado en
  [data/my-team.md](../../data/my-team.md), validado `wcf myteam` 15/15, costo $99.3M.
  **Budget real restante: $3.1M** (cap sube a $105M en R32). Capitán Mbappé, vice Haaland, ningún
  booster usado.
- **Historial por ronda nuevo:** [data/historial-rondas.md](../../data/historial-rondas.md) — Mani
  quiere registrar equipo + puntos por ronda. Arranca en R3 (parcial: la ronda sigue en juego).
  Joya: **Manzambi** (0.2-0.7% own, 15+13 en R2/R3). Lastre: **Bruno Fernandes** (1 pt en 3 rondas).
  **Haaland DNP en R3 = 0** (confirmado por Mani).
- **Optimizador ILP (Fase 4 adelantada):** [src/wcf/optimizer.py](../../src/wcf/optimizer.py) +
  comando `wcf optimize`. PuLP, **modelo de dos niveles** (squad 15 + XI + capitán x2). Maximiza la
  proyección del XI con capitán al doble, NO la suma de los 15 (clave: no malgasta budget en banca).
  Restricciones: 2/5/5/3, $105M, máx 3/país, formación válida (rangos de titulares = las 7
  formaciones legales de config). Reusa `report.select_xi`. Escribe `outputs/<ronda>-reset.md`.
  Validado: 15/15, composición y cap exactos, formación 3-4-3, XI consistente.

**Decisiones clave:**
- **No optimizar R32 hoy = a propósito.** Al 26 jun el bracket no está cerrado (solo 2/15 jugadores
  con cruce asignado; ninguna selección de Mani eliminada). `wcf optimize` corre pero da banco alto
  ($19.7M sin gastar) = señal de pool parcial. Con transfers ilimitadas en R32, esperar es gratis:
  reconstruir cuando R3 cierre y el bracket esté fijo, antes del lockout del 28.
- **Límites del modelo (dije a Mani):** la proyección v0 usa `avgPoints` + prior de precio +
  matchup. **No** pondera forma reciente ni mete las noticias al número (RSS es feed aparte para
  leer). El ILP optimiza perfecto sobre números estimados: el próximo salto de calidad es
  **recalibrar pesos con puntos reales R1-R3 (Fase 3 backtest)**, no afinar el solver.

**Commits:** `946b0da` (registro R3 + realineación) · `8cf17b5` (optimizador ILP).

**Agendado:** recordatorio one-time para **28 jun 9:00 AM Colombia** (`wcf-r32-lockout-reminder` en
`~/.claude/scheduled-tasks/`) que arranca el reset de R32 con `wcf optimize` antes del lockout.

**Próximas skills sugeridas:** `/tdd` o codear directo la **Fase 3 (backtest + recalibración de
pesos)** — es el mayor ROI ahora. El día del lockout, dejar que corra el recordatorio agendado.

## Roadmap

> Tracker canónico y por-fase: [ROADMAP.md](../../ROADMAP.md). Resumen del estado para retomar:

**Now (próximo lockout R32 — 28 jun 20:00 UTC+1):**
- Esperar a que cierre R3 (grupos completos, bracket fijo) → correr `wcf optimize` para el reset.
  El recordatorio agendado lo dispara. Después: registrar R4 en `historial-rondas.md`, actualizar
  `my-team.md`, cerrar el R3 parcial.

**Next:**
- **Fase 3 — backtest + recalibración:** comparar la proyección v0 vs puntos reales R1-R3 (ya en el
  snapshot del pool) y ajustar constantes de `projection.py`. Mayor ROI: el optimizador ya es bueno,
  los números que lo alimentan no tanto.
- Pipeline repetible de un comando; tracking de ownership entre deadlines; decisión de Wildcard.

**Later (Fase 4+ restante):**
- Modelo de avance multi-ronda (odds/Elo del bracket), valor de opcionalidad por horario, plan de
  boosters del knockout (incl. Mystery). Fase 5 (asistente in-play) y Fase 6 (post-mortem).
