# Plan de ejecución por fases

El reloj manda: el torneo ya empezó (MD1 en vivo desde el 11 jun 2026) y el equipo inicial ya está
inscrito. Cada fase entrega algo usable ANTES de un deadline real. Mejor un ranking simple a tiempo
que un optimizador perfecto tarde.

**Fechas ancla (verificar contra el calendario oficial):** deadline MD2 ≈ 18 jun · deadline MD3 ≈
~24 jun · deadline R32 (reset grande: transfers ilimitadas + $105M) ≈ ~28 jun · final 19 jul.

---

## Fase 0 — Fundamentos documentales ✅

- [x] Reglas oficiales documentadas y verificadas contra play.fifa.com ([01-reglas.md](01-reglas.md))
- [x] Lista priorizada de factores de puntos ([02-factores-de-puntos.md](02-factores-de-puntos.md))
- [x] Onboarding para novatos ([00-onboarding.md](00-onboarding.md))
- [x] Mapa de fuentes de datos ([03-fuentes-de-datos.md](03-fuentes-de-datos.md))

## Fase 1 — Base de datos del torneo (ahora → 14 jun)

Objetivo: tener los datos crudos fluyendo y el estado propio capturado.

- [ ] Registrar el equipo actual en el repo (`data/my-team.md` o JSON): 15 jugadores, precios,
      titulares/banca, capitán/vice, transfers disponibles, boosters intactos. Es el estado inicial
      de toda recomendación.
- [ ] Crear cuenta API-Football, validar cobertura WC2026: id de liga, stats por jugador,
      `injuries` en selecciones, límites del free tier. Decidir si toca plan pago.
- [ ] Inspeccionar endpoints del fantasy en play.fifa.com (network tab): pool de jugadores,
      precios, **% ownership**, posiciones del juego. Documentar en 03.
- [ ] Snapshot inicial: pool completo de jugadores con precio + posición + ownership → `data/`.
- [ ] Evaluar el news aggregator de RapidAPI (señal/ruido, filtros).
- [ ] Esqueleto del repo: `src/` (Python sugerido), `data/`, `.env.example`, `.gitignore`.

**Done cuando:** puedo correr un script que descarga fixtures, stats e injuries del Mundial y
tengo el pool fantasy con ownership en disco.

## Fase 2 — MVP de decisión para MD2 (→ antes del deadline MD2, ~18 jun)

Objetivo: la primera decisión real (2 transfers de MD2) sale del modelo, no del feeling.

- [ ] Proyección v0 de puntos esperados por jugador para MD2: heurística ponderada con los datos
      de Fase 1 (minutos esperados × stats base por posición × matchup del rival), sin ML todavía.
- [ ] Ranking de profitability v0: proyección + flag de scouting bonus (<5% y P(pts≥5)) + horizonte
      a MD3 (no quemar transfers en jugadores de equipos casi eliminados).
- [ ] Recomendador de transfers: dadas las 2 libres (+regla de rollover), proponer el mejor par
      sustituir-entrar con justificación.
- [ ] Plan de capitanía MD2: orden de switches por horario de fixture con umbrales stick-or-twist.
- [ ] Output legible en `outputs/md2-reporte.md`.

**Done cuando:** existe un reporte MD2 con transfers recomendadas, XI, orden de banca y plan de capitán.

## Fase 3 — Pipeline repetible (→ deadline MD3)

Objetivo: lo de Fase 2 deja de ser artesanal y se corre con un comando.

- [ ] Script único `make report` (o similar): refresca datos → recalcula ranking → emite reporte de ronda.
- [ ] Tracking de ownership entre deadlines (histórico para anticipar quién cruza el 5%).
- [ ] Evaluación de Wildcard: ¿se justifica en MD3 o se guarda para octavos+?
- [ ] Backtest informal: comparar la proyección v0 de MD2 contra los puntos reales → ajustar pesos.

**Done cuando:** el reporte de MD3 sale con un comando y la v0 tiene su primera calibración.

## Fase 4 — El gran reset: optimizador completo para el R32 (→ deadline R32)

El momento de mayor apalancamiento del torneo: transfers ilimitadas, $105M, 16 selecciones vivas,
máx 3 por país todavía, Mystery booster revelado.

- [ ] Optimizador combinatorio (ILP con PuLP/OR-Tools): maximizar puntos esperados del squad
      sujeto a presupuesto, 2/5/5/3, máx 3 por país, formaciones válidas.
- [ ] Modelo de avance del torneo (P2): probabilidades de bracket vía odds o simulación Elo,
      para ponderar proyecciones multi-ronda (R32 + octavos al menos).
- [ ] Optimización del calendario interno (P6): titulares temprano / banca tarde / diversificación
      de naciones para ventanas de captain-switch.
- [ ] Plan de boosters del knockout: cuándo Qualification (máxima prob. conjunta de avance),
      qué hace el Mystery, cuándo quemar Wildcard/12th Man/Max Captain.
- [ ] Reporte R32 completo: squad nuevo desde cero.

**Done cuando:** el squad del R32 sale del optimizador con justificación por jugador.

## Fase 5 — Rondas de knockout + asistente in-play (R16 → Final)

- [ ] Loop por ronda: refresh → proyección → transfers limitadas (4/4/5/6) → reporte.
- [ ] Asistente in-play: dado el estado live de la ronda (quién ya jugó, puntos acumulados),
      recomendar sub manual / captain switch / plantarse, usando valor esperado del siguiente
      candidato vs. puntos en mano. (Recordar: el primer cambio manual mata auto-subs y vice.)
- [ ] Ajuste de proyecciones con datos del propio torneo (ya habrá 3-4 partidos por selección).

## Fase 6 — Post-mortem (después de la final)

- [ ] Backtest completo: puntos del modelo vs. mis puntos reales vs. ganador de la mini-league.
- [ ] Documentar qué funcionó y qué no → base para Champions League fantasy / FPL / WC 2030.

---

## Principios de trabajo

1. **Deadline-first:** cada fase existe para una decisión con fecha; si el tiempo no alcanza, se
   recorta sofisticación, nunca la entrega.
2. **Todo documentado:** decisiones de diseño en `docs/`, recomendaciones emitidas en `outputs/`
   (para poder auditar después qué dijo el modelo y qué pasó).
3. **El modelo recomienda, Mani decide:** el output siempre incluye el porqué, no solo el qué.
4. **Versionar los snapshots de datos** que alimentan cada recomendación (reproducibilidad del backtest).
