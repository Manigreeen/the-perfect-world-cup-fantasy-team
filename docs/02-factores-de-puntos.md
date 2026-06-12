# Factores que influyen en los puntos — lista priorizada

Derivados directamente de las reglas oficiales ([01-reglas.md](01-reglas.md)). Cada factor es
candidato a variable en la fórmula de profitability. Prioridad 1 = mayor impacto esperado en
puntos totales.

## P1 — Minutos esperados (el multiplicador de todo)

Ningún otro factor importa si el jugador no juega. +1 por aparecer, +1 por 60+ min, y todos los
demás puntos (goles, clean sheets, stats) requieren estar en cancha.
- **Señales:** titularidad en su selección, rotación esperada (grupos ya definidos → rotación en R3),
  lesiones, sanciones (amarillas acumuladas), minutos recientes en club y selección.

## P2 — Probabilidad de avance del equipo (el factor torneo)

Un jugador eliminado vale 0 en adelante y consume transfers (limitadas: 2-6 por ronda, −3 el hit).
Además habilita el Qualification booster (+2/titular desde el R32, no duplicable por capitanía) y
los límites por nación crecientes (3 → 3 en R32 → 4 → 5 → 6 → 8) premian cargarse de selecciones
que llegan lejos. **Ojo:** en el R32 el límite sigue siendo 3 por país pese al reset de transfers
ilimitadas; la primera subida real es en octavos (4).
- **Señales:** odds de avance (casas de apuestas / Elo / simulaciones de bracket), dificultad de
  grupo y de cruce proyectado.

## P3 — Goal involvement ajustado por posición

Los goles no valen igual: GK 9, DEF 7, MID 6, FWD 5. Asistencia +3 para todos. Un **defensor
goleador** (córners, penales, laterales ofensivos) es el activo más rentable del juego por punto
de costo: gol 7 + clean sheet 5 posibles en el mismo partido.
- **Señales:** xG/xA recientes, rol en pelota parada (penales, libres directos: +1 bonus, córners),
  posición real en cancha vs. posición listada en el juego (MID listado que juega de delantero, etc.).

## P4 — Clean sheet esperado (GK/DEF) y castigo por goleada

Clean sheet +5 es generoso, pero del 2.º gol recibido en adelante cada gol resta 1. La distribución
importa: un equipo que alterna 0-0 y 0-4 es peor que uno que recibe 1 gol estable.
- **Señales:** xGA del equipo, solidez defensiva reciente, calidad del rival del MD (matchup por
  fixture, no promedio del torneo).

## P5 — Scouting bonus: ownership <5%

+2 por partido (condicional a **más de 4 pts**, o sea ≥5) es enorme acumulado en 8 rondas.
Convierte el ownership en una variable de decisión de primer orden: entre dos jugadores de
proyección similar, el <5% domina.
- **Señales:** % selected en el juego al deadline (hay que consultarlo antes de cada deadline
  porque cambia), proyección propia de P(pts ≥ 5).

## P6 — Calendario dentro del matchday (valor de opcionalidad)

Las subs manuales y el captain switching solo funcionan hacia jugadores **unlocked** (que aún no
juegan), y solo se puede sacar/des-capitanear a quien no esté jugando en vivo. Un jugador que juega
tarde en la ronda vale más en banca; uno que juega temprano vale más como titular/capitán inicial.
Diversificar naciones multiplica las ventanas de switch. **Costo oculto:** el primer cambio manual
de la ronda anula las auto-subs Y el fallback del vice-capitán — al activar gestión manual hay que
gestionarlo todo manual.
- **Señales:** horario del fixture de cada jugador dentro de la ronda (dato estructural,
  determinístico).

## P7 — Volumen estadístico por posición

Puntos "silenciosos" que se acumulan sin goles:
- **FWD:** +1 / 2 remates al arco → tiradores de volumen.
- **MID:** +1 / 2 chances creadas y +1 / 3 tackles → creadores y box-to-box. MID también +1 por clean sheet.
- **GK:** +1 / 3 atajadas → arqueros de equipos defensivos que reciben muchos tiros pero pocos goles
  (perfil "underdog sólido"), +3 por penal atajado.
- **Señales:** shots on target p90, key passes p90, tackles p90, saves p90 (datos de club + selección).

## P8 — Riesgo disciplinario y de eventos negativos

Amarilla −1, roja directa −2, autogol −2, penal concedido −1. Marginal por partido pero relevante
para perfiles específicos (defensores agresivos, equipos que defienden en bloque bajo todo el partido).
- **Señales:** tarjetas p90, faltas p90, penales concedidos históricos.

## P9 — Precio / eficiencia de presupuesto

Con precios congelados todo el torneo, el value se calcula una vez por jugador y solo cambia su
proyección. $100M para 15 implica ~$6.7M promedio ($105M desde el knockout): cada premium obliga
enablers baratos que también puntúen (ver P1 y P7).
- **Señal:** puntos esperados por millón (ePts/$M), restricción dura del optimizador.

## P10 — Estructura de transfers y timing de boosters

No es un atributo del jugador sino del plan: transfers ilimitadas pre-torneo y antes del R32 son
los dos momentos de rearmado total (planear la plantilla por "bloques" grupos y knockout). Rollover
de 1 transfer entre rondas de grupos. Wildcard guardado para emergencias en MD2-3 o desde octavos
(no es usable en MD1 ni R32). Qualification booster óptimo cuando los 11 titulares tienen máxima
probabilidad conjunta de avanzar (su +2 no se duplica con capitanía). Mystery booster se revela al
abrir el R32 — reservar juicio hasta entonces.

---

## Implicaciones para la fórmula de profitability (borrador)

```
profitability(jugador, MD) =
    E[pts_base | minutos]                    # P1, P3, P4, P7, P8 → proyección por partido
  × P(juega)                                  # P1
  + bonus_scouting(ownership<5%, P(pts≥4))    # P5
  + valor_opcionalidad(horario_fixture)       # P6 (titular temprano / banca tarde / capitán)
  ponderado por:
    P(equipo avanza a MD+1, MD+2, ...)        # P2 → horizonte multi-ronda
    costo / restricciones del optimizador     # P9, límites de nación, composición
```

Pendiente: definir pesos, horizonte de optimización (¿greedy por MD vs. lookahead al bloque?),
y el modelo de proyección de pts_base.
