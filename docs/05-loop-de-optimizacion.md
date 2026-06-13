# Loop de optimización dinámica — cómo se adapta la estrategia

> Primera tarea de Fase 2. Responde: la data es viva (FIFA carga puntos tras cada partido y el
> ownership cambia intradía), pero las transfers son escasas y el hit cuesta −3. ¿Cuándo
> recalcular, con qué horizonte, y con qué umbral para no hacer cambios nerviosos?
>
> **Estado:** decidido (2026-06-13). Horizonte = **lookahead por bloque**; apetito de riesgo =
> **moderate por default, pero es un dial ajustable** (`WCF_RISK` en `.env` o `--risk` en el CLI).
> Ambos están encodeados en `src/wcf/strategy.py`. Los números se recalibran con el backtest de MD2.

## Principio rector: optimizar ≠ reaccionar

El modelo se actualiza seguido; **las decisiones no**. Entre dos deadlines la información cambia,
pero actuar sobre cada cambio quema transfers (−3 cada exceso) y ownership (pierdes la ventaja del
<5%). La regla: **recalcular el ranking a diario es barato; cambiar el equipo solo cuando la
ganancia supera un umbral.** El loop separa esas dos velocidades.

## Hallazgo que de-riesga el timeline

El pool de FIFA (`players.json`) ya trae, sin API-Football:

| Campo | Para qué |
|---|---|
| `roundPoints` `{'1': 10}` | **Puntos fantasy oficiales por ronda** — señal de proyección y verdad para el backtest |
| `form`, `avgPoints` | Forma reciente del jugador en el propio torneo |
| `roundsSelected` `{'1': 3.8, '2': 3.9}` | **Ownership histórico por ronda** — tendencia para anticipar cruces del 5% |
| `nextFixtureFromScheduledRound` | Próximo partido del jugador |

Y `rounds.json` da los 24 matchups de cada ronda con rival y horario. **Por eso el MVP de MD2
sale con datos de FIFA solos.** API-Football entra como mejora (stats granulares: tiros, tackles,
chances, xG, injuries) para una proyección más fina, no como prerrequisito.

## 1. Cadencia de refresco de datos

Event-driven, no obsesivo. Los snapshots quedan versionados en `data/snapshots/<fecha>/`.

| Dato | Cuándo refrescar | Comando |
|---|---|---|
| Pool FIFA (precios, ownership, puntos) | 1×/día en ventana de decisión + **siempre justo antes del lockout** | `wcf pool` |
| Rondas/fixtures/resultados | Tras cada jornada de partidos | `wcf rounds` |
| Injuries (API-Football) | Diario solo en los 3 días previos al lockout | `wcf injuries` |
| Stats por jugador (API-Football) | 1× después de que cierra cada matchday | `wcf players` |

Fuera de la ventana de decisión (3-4 días antes de cada lockout) no hace falta tocar nada: los
precios son fijos y el ownership casi no se mueve lejos del deadline.

## 2. Triggers de re-decisión

Qué evento obliga a recalcular el plan **antes** del refresco diario normal:

- **Titular propio lesionado/sancionado/en banca** confirmado → recalcular ese slot ya.
- **Un target cae** (lesión/rotación) → reordenar el ranking de candidatos.
- **Un jugador mío cruza el 5% de ownership** al alza → pierde el scouting bonus; evaluar si su
  proyección lo justifica igual.
- **Cambio de fixture** (suspensión, reprogramación) → afecta el plan de capitanía por horario.
- **48h antes del lockout:** corrida completa obligatoria pase lo que pase.

Sin trigger activo, el equipo no se toca aunque el ranking se mueva un poco. Esa es la defensa
anti-nerviosismo.

## 3. Horizonte de decisión — ✅ lookahead por bloque

Dos modos:

- **Greedy por ronda:** maximiza los puntos del próximo matchday. Simple, pero quema transfers en
  jugadores de equipos que pueden quedar eliminados.
- **Lookahead por bloque (recomendado):** optimiza sobre el bloque restante (grupos = MD2+MD3;
  knockout se replanea entero en el R32). Pondera la proyección del próximo MD con la probabilidad
  de que el equipo siga vivo en el siguiente. Evita gastar una transfer en alguien que juega un
  partido y se va a casa.

**Decidido:** lookahead por bloque con descuento — peso **1.0** al próximo MD, **0.5** al
siguiente (`strategy.HORIZON_WEIGHTS`). El R32 es el reset donde se planea desde cero.

## 4. Umbrales de estabilidad — ✅ dial de riesgo (default moderate)

El gatillo que convierte "el ranking cambió" en "vale la pena el cambio". **Es un parámetro
ajustable, no fijo** — `WCF_RISK` en `.env` o `--risk` en el CLI; vive en `strategy.RISK_PROFILES`.
Default **moderate**:

| Decisión | conservative | **moderate** | aggressive |
|---|---|---|---|
| Transfer libre (entrante supera al saliente) | ≥ +3.0 | **≥ +2.0** | ≥ +1.0 |
| Transfer pagando el hit −3 (ganancia neta) | ≥ +5.0 | **≥ +4.0** | ≥ +3.5 |
| Romper el plan de capitanía | ≥ +2.5 | **≥ +1.5** | ≥ +1.0 |
| Peso del scouting bonus (<5%) en el ranking | 0.5× | **1.0×** | 1.5× |

(Todos en puntos esperados sobre el horizonte del bloque.) La sub in-play es aparte: solo si el
titular hizo DNP o su proyección viva cae bajo la del banca. Estos números son el punto de
partida; se recalibran con el backtest de MD2.

## 5. Loop de calibración

Cada ronda cierra el ciclo aprendizaje:

1. Tras el matchday, `wcf pool` trae los `roundPoints` oficiales.
2. Comparar proyección emitida (en `outputs/<ronda>-reporte.md`) vs puntos reales.
3. Medir error por posición y por factor; ajustar pesos de la fórmula de profitability
   ([02](02-factores-de-puntos.md)).
4. Documentar el ajuste en el propio reporte de la ronda siguiente (trazabilidad).

Por eso cada reporte se versiona: el backtest necesita saber qué dijo el modelo *antes* de conocer
el resultado.

## 6. El ritual por ronda (lo que se ejecuta)

```
T-4 días   wcf pool ; wcf rounds        # refrescar estado, ver matchups de la ronda
           → recalcular ranking, calibrar pesos con la ronda anterior
T-3..T-1   wcf injuries (diario)         # vigilar titulares propios y targets
           → re-decidir solo si salta un trigger (§2)
T-48h      corrida completa              # ranking + recomendador de transfers + plan capitanía
           → outputs/<ronda>-reporte.md
T-0 lockout wcf pool (último refresh)    # ownership final → confirmar scouting picks
           → ejecutar transfers en play.fifa.com, fijar capitán
en vivo    asistente in-play (Fase 5)    # subs/switches por valor esperado
```

---

## Decisiones tomadas (2026-06-13)

1. **Horizonte (§3):** lookahead por bloque (pesos 1.0 / 0.5).
2. **Apetito de riesgo (§4):** moderate por default, **ajustable** vía `WCF_RISK` — Mani lo sube a
   aggressive para perseguir diferenciales o lo baja a conservative para proteger el squad, sin
   tocar código.

Ambas viven en `src/wcf/strategy.py`. Con esto fijo, el modelo (proyección v0 → ranking →
recomendador) se construye encima.
