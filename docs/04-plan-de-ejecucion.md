# Plan de ejecución por fases — el porqué

> **El estado vivo de las tareas se lleva en [ROADMAP.md](../ROADMAP.md)** (única fuente de
> verdad de qué está hecho y qué falta). Este doc conserva la lógica de cada fase: para qué
> existe, qué decisión habilita y cuándo se considera cumplida.

El reloj manda: el torneo ya empezó (MD1 en vivo desde el 11 jun 2026) y el equipo inicial ya
está inscrito. Cada fase entrega algo usable ANTES de un deadline real. Mejor un ranking simple
a tiempo que un optimizador perfecto tarde.

**Fechas ancla (verificadas 2026-06-12 contra `rounds.json` del juego; hora local UTC+1):**
lockout MD2 = **18 jun 17:00** · MD3 = 24 jun 20:00 · R32 (reset grande: transfers ilimitadas +
$105M) = 28 jun 20:00 · R16 = 4 jul · QF = 9 jul · SF = 14 jul · Final = 18 jul 22:00.
Fuente viva: `wcf rounds`.

---

## Fase 0 — Fundamentos documentales ✅

Reglas oficiales verificadas ([01-reglas.md](01-reglas.md)), factores priorizados
([02-factores-de-puntos.md](02-factores-de-puntos.md)), onboarding ([00](00-onboarding.md)),
mapa de fuentes ([03](03-fuentes-de-datos.md)). Sin esto, cualquier modelo optimiza las reglas
equivocadas (la guía de FPL Mate tenía 10+ discrepancias contra lo oficial).

## Fase 1 — Base de datos del torneo (→ 14 jun)

**Para qué:** tener los datos crudos fluyendo y el estado propio capturado antes de modelar nada.
Incluye el esqueleto del repo, los clientes de datos (FIFA + API-Football) y el registro del
equipo actual — el estado inicial de toda recomendación.

**Done cuando:** puedo correr un comando que descarga fixtures, stats e injuries del Mundial, y
tengo el pool fantasy con ownership en disco junto con mi plantilla validada.

## Fase 2 — MVP de decisión para MD2 (→ 18 jun 17:00)

**Para qué:** que la primera decisión real (2 transfers de MD2 + capitanía) salga del modelo, no
del feeling. Heurística simple y a tiempo; el refinamiento llega después. Arranca con el
brainstorm del **loop de optimización dinámica** (cadencia de refresco, triggers de re-decisión,
umbrales — ver ROADMAP) porque define cómo se usa todo lo demás.

**Done cuando:** existe `outputs/md2-reporte.md` con transfers recomendadas, XI, orden de banca
y plan de capitán, cada una con su porqué.

## Fase 3 — Pipeline repetible (→ 24 jun 20:00)

**Para qué:** lo de Fase 2 deja de ser artesanal: un comando refresca datos, recalcula el ranking
y emite el reporte de ronda. Además, primera calibración del modelo contra los puntos reales de
MD2 (vienen oficiales en `players.json`).

**Done cuando:** el reporte de MD3 sale con un comando y la proyección v0 fue recalibrada una vez.

## Fase 4 — El gran reset: optimizador completo para el R32 (→ 28 jun 20:00)

**Para qué:** el momento de mayor apalancamiento del torneo — transfers ilimitadas, $105M, 16
selecciones vivas, máx 3 por país todavía, Mystery booster revelado. Aquí sí se justifica el
optimizador combinatorio (ILP) y el modelo de avance del bracket: el espacio de decisión es
"squad entero desde cero", no "un par de transfers".

**Done cuando:** el squad del R32 sale del optimizador con justificación por jugador.

## Fase 5 — Rondas de knockout + asistente in-play (R16 → Final)

**Para qué:** cada ronda restante es el mismo loop con transfers limitadas (4/4/5/6), más la
gestión en vivo: subs manuales y captain switching por valor esperado (recordando que el primer
cambio manual mata las auto-subs y el fallback del vice). Las proyecciones ya se alimentan de
datos del propio torneo.

## Fase 6 — Post-mortem (después de la final)

**Para qué:** cerrar el ciclo: modelo vs realidad vs mini-league, y documentar qué funcionó.
Este proyecto es también el prototipo para Champions fantasy / FPL / WC 2030.

---

## Principios de trabajo

1. **Deadline-first:** cada fase existe para una decisión con fecha; si el tiempo no alcanza, se
   recorta sofisticación, nunca la entrega.
2. **Todo documentado:** decisiones de diseño en `docs/`, recomendaciones emitidas en `outputs/`
   (para poder auditar después qué dijo el modelo y qué pasó).
3. **El modelo recomienda, Mani decide:** el output siempre incluye el porqué, no solo el qué.
4. **Versionar los snapshots de datos** que alimentan cada recomendación (reproducibilidad del
   backtest) — por eso el modelo lee de `data/snapshots/`, nunca HTTP directo.
