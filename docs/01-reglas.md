# Reglas oficiales — FIFA World Cup Fantasy 2026

> **Fuente:** reglas oficiales de FIFA, play.fifa.com/fantasy/help/guidelines (capturadas 2026-06-11).
> Esta es la fuente de verdad. Las discrepancias contra la guía de FPL Mate (primera versión de este
> doc) están listadas al final en §10 — varias afectan al modelo.

## 1. Armado de la plantilla

- **Presupuesto:** $100M para 15 jugadores de una lista curada con precio fijo por jugador.
- **Composición fija del squad:** 2 GK, 5 DEF, 5 MID, 3 FWD.
- **Límite de jugadores por selección, según fase:**

| Fase | Máx. por país |
|---|---|
| Fase de grupos | 3 |
| Round of 32 | **3** |
| Round of 16 | 4 |
| Cuartos de final | 5 |
| Semifinales | 6 |
| Final | 8 |

- **Starting XI + 4 en banca.** Solo el 11 titular suma puntos (los suplentes puntúan visiblemente, pero no cuentan para tu score salvo que entren).
- **Formaciones válidas (lista cerrada):** 4-4-2, 4-3-3, 4-5-1, 3-4-3, 3-5-2, 5-4-1, 5-3-2.
- Al guardar por primera vez: capitán = jugador más caro, vice = segundo más caro (se puede cambiar). Formación default 4-4-2.
- Cambios ilimitados hasta el kickoff del primer partido del Mundial (11 jun 2026).

## 2. Presupuesto y precios

- Presupuesto inicial: **$100M**.
- **Fase eliminatoria: el presupuesto sube +$5M (→ $105M)**, aplicado automáticamente cuando cierra la Ronda 3 y abren las transfers del Round of 32.
- **Los precios de jugadores son fijos todo el torneo** — no cambian con el rendimiento.

## 3. Capitán y vice-capitán

- El capitán **duplica** sus puntos. Si no juega ningún minuto, duplica el vice.
- **Advertencia clave:** el vice-capitán solo duplica si **NO hiciste ningún cambio manual** a tu equipo durante la ronda en vivo.
- **Cambio de capitán in-play:** ilimitado durante la ronda, siempre que (a) el nuevo capitán **aún no haya jugado**, y (b) tu capitán anterior **ya haya completado** su partido. No se puede tocar al capitán mientras su partido está en curso.
- Al cambiar de capitán pierdes los puntos dobles del anterior; el nuevo duplica.

## 4. Sustituciones

Conceptos oficiales:
- **Locked player:** su selección está jugando un partido **en este momento**.
- **Unlocked player:** su selección aún no juega.

### Automáticas
- Solo si **no hiciste ningún cambio manual** en la ronda en vivo (una sola sub manual o cambio de capitán/vice las cancela para esa ronda).
- Reemplazan a titulares DNP (did not play) al **final de la ronda**.
- La banca tiene **prioridad 1–3** entre jugadores de campo: el suplente de prioridad 1 entra primero, siempre que la formación resultante sea válida.

### Manuales (durante la ronda en vivo)
- Puedes meter a un suplente **que aún no jugó** por un titular **que no esté jugando en vivo** (antes de que empiece su partido o después de que termine), manteniendo formación válida.
- Tras la sub, solo puntúa el que entra. Si el que sale ya completó su partido, **no puede volver** al XI.
- Reglas de locked/unlocked:
  - Unlocked del XI ↔ unlocked de la banca: intercambiables las veces que quieras.
  - Locked del XI: intocable hasta que su partido termine.
  - Suplente que ya completó su partido: no puede entrar por un unlocked del XI.
  - Locked ↔ locked: prohibido siempre.
  - Dos jugadores que ya completaron su partido: no se pueden intercambiar.

## 5. Transfers

| Momento | Transfers libres |
|---|---|
| Pre-torneo | Ilimitadas |
| Antes del Matchday 2 | 2 |
| Antes del Matchday 3 | 2 |
| Antes del Round of 32 | **Ilimitadas** |
| Antes del Round of 16 | 4 |
| Antes de Cuartos | 4 |
| Antes de Semifinales | 5 |
| Antes de la Final | 6 |

- **Rollover:** en fase de grupos puedes arrastrar 1 transfer no usada a la siguiente ronda de grupos. No hay rollover hacia el R32 (porque ahí son ilimitadas).
- **Exceso:** cada transfer por encima de tu asignación cuesta **−3 puntos** (descontados cuando la ronda cierra).
- Una transfer confirmada **no se puede revertir**.
- Las transfers solo aplican a la **siguiente ronda programada**: si las haces durante una ronda en vivo, no afectan tu equipo actual.

## 6. Lockout

- **Lockout fijo** para transfers (al kickoff del primer partido de la ronda) + **rolling lockout** durante la ronda en vivo para cambios de equipo (el sistema locked/unlocked de §4).

## 7. Boosters (5)

- Cada uno se usa **una sola vez**; no se pueden usar dos a la vez.
- **Todos son reversibles antes del lockout de la ronda** (botón "deactivate"), **excepto el Wildcard**, que es irreversible desde la confirmación.

| Booster | Efecto | Restricciones |
|---|---|---|
| **Wildcard** | Transfers ilimitadas en una ronda | No usable para la primera ronda de grupos **ni para el Round of 32**. Irreversible |
| **12th Man** | 1 jugador adicional que puntúa esa ronda | Sin límite de presupuesto ni de país; no puede ser sustituido, capitaneado ni transferido; no puede estar ya en tu squad |
| **Maximum Captain** | La capitanía se asigna automáticamente al jugador de tu XI con más puntos de la ronda | — |
| **Qualification** | +2 a cada jugador del XI cuyo equipo avance de ronda (o gane la final), si jugó ≥1 min | Solo desde el R32. **El +2 NO se duplica con la capitanía** |
| **Mystery** | Se revela cuando cierra la Ronda 3 y abre el R32 | Usable en una ronda del knockout, incluida la final |

## 8. Sistema de puntos

### Todos los jugadores

| Acción | Puntos |
|---|---|
| Aparición (hasta 60 min) | +1 |
| Aparición 60+ min | +1 (adicional) |
| Asistencia | +3 |
| Tarjeta amarilla | −1 |
| Tarjeta roja | −2 |
| Autogol | −2 |
| Ganar un penal | +2 |
| Conceder un penal | −1 |

### Por posición

| Acción | GK | DEF | MID | FWD |
|---|---|---|---|---|
| Gol | **+9** | **+7** | **+6** | **+5** |
| Clean sheet (60+ min) | +5 | +5 | +1 | — |
| Primer gol recibido | 0 | 0 | — | — |
| Cada gol recibido adicional | −1 | −1 | — | — |
| Penal atajado (no tandas) | +3 | — | — | — |
| Cada 3 atajadas | +1 | — | — | — |
| Cada 3 tackles | — | — | +1 | — |
| Cada 2 chances creadas | — | — | +1 | — |
| Cada 2 remates al arco | — | — | — | +1 |

### Bonus

| Acción | Puntos |
|---|---|
| Gol de tiro libre directo (además de los puntos de gol) | +1 |
| **Scouting bonus:** jugador con **más de 4 pts** en el partido y en **menos del 5%** de los equipos globales | +2 |

## 9. Leaderboards y mini leagues

- **Overall:** todos los usuarios; también ranking por ronda individual.
- **Country Supported:** compites contra fans de tu misma selección.
- **Country Championship:** suma de puntos de todos los fans de cada selección.
- **Confederation Challenge:** agregado por confederación.
- **Mini leagues:** públicas o privadas, ilimitadas, por código/link.

## 10. Discrepancias: guía FPL Mate (video) vs. reglas oficiales

Correcciones que cambian decisiones del modelo:

1. **Round of 32: máx 3 jugadores por país, NO 4.** El video decía 4 en MD4-5; oficial: R32=3, R16=4. El gran reset del R32 sigue con la restricción de grupos.
2. **Presupuesto knockout: +$5M explícito ($105M).** El video solo decía "aumenta".
3. **Scouting bonus: "más de 4 pts" (≥5), no "≥4".** El umbral real es 5+ puntos en el partido.
4. **Vice-capitán condicionado:** cualquier cambio manual en la ronda anula el doblete del vice. El video no lo mencionaba.
5. **Qualification booster: el +2 no se duplica con la capitanía.**
6. **Wildcard reversibilidad matizada:** los demás boosters SÍ se pueden desactivar antes del lockout; el video sugería que ninguno.
7. **Rolling lockout / jugadores locked:** no puedes sacar a un titular mientras su partido está en vivo; el video simplificaba a "ya jugó / no ha jugado".
8. **Auto-subs con prioridad 1–3 de banca y se ejecutan al final de la ronda** — puedes hacer subs manuales hasta el inicio del último partido de la ronda.
9. **Formaciones: lista cerrada de 7**, no "cualquier formación con mínimos".
10. **Transfers en vivo aplican a la siguiente ronda** — confirmación explícita oficial.
11. Sin confirmar en las reglas oficiales: el detalle de "penal ganado no suma asistencia si se convierte" y la distinción roja directa vs. doble amarilla (oficial solo dice "Red Card −2"). Tratar el texto oficial como autoridad.
