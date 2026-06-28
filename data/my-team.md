# Mi equipo — estado actual

> Estado inicial de toda recomendación. Actualizar tras cada deadline.
> Última actualización: 2026-06-28 — squad vigente entrando a la **ronda 4 / R32** (lockout 28 jun 20:00).
> Validar con `wcf myteam` contra el snapshot del pool del día.

## Cómo llenar esto

Todo sale de play.fifa.com → Fantasy: la vista de **tu equipo** (XI, banca, capitán/vice,
formación) y la pantalla de **Transfers** (lista de los 15 con precio y presupuesto restante).
Tras cada edición corre `wcf myteam`: confirma jugador por jugador contra el pool oficial y
avisa de typos, precios distintos, posiciones mal anotadas y límites violados.

| Columna | Qué va | Formato / dónde verlo |
|---|---|---|
| **Jugador** | Nombre tal como aparece en su tarjeta del juego | **Obligatorio.** Tildes y mayúsculas dan igual; el apellido solo alcanza si no es ambiguo |
| **Selección** | País del jugador, **en inglés, como lo muestra el juego** ("Germany", no "Alemania") | **Obligatorio** — desambigua homónimos |
| **Pos (juego)** | `GK` / `DEF` / `MID` / `FWD`, la posición que el juego le asigna (no la real en cancha) | Opcional: si la dejas vacía, `wcf myteam` te muestra la oficial |
| **Precio** | El precio de su tarjeta | Opcional: `$5m`, `5.5` o `$7.0M`, todo vale; el validador lo cruza con el oficial |
| **Rol** | `Titular` o `Banca`, según tu XI actual | El orden de la banca va en el bullet de abajo |

## Squad (15)

| # | Jugador | Selección | Pos (juego) | Precio | Rol | Ownership |
|---|---------|-----------|-------------|--------|-----|-----------|
| 1 | Unai Simón | Spain | GK | $5.0m | Titular | 7.8% |
| 2 | Aymeric Laporte | Spain | DEF | $5.5m | Titular | 7.8% |
| 3 | Ezri Konsa | England | DEF | $4.8m | Titular | 2.2% |
| 4 | Marcos Llorente | Spain | DEF | $5.5m | Titular | 4.4% |
| 5 | Ousmane Dembélé | France | MID | $10.0m | Titular | 19.1% |
| 6 | Vinícius Júnior | Brazil | MID | $10.0m | Titular | 31.8% |
| 7 | Jude Bellingham | England | MID | $8.3m | Titular | 14.2% |
| 8 | Johan Manzambi | Switzerland | MID | $5.6m | Titular | 1.9% |
| 9 | Lionel Messi | Argentina | FWD | $10.0m | Titular | 37.4% |
| 10 | Kylian Mbappé | France | FWD | $10.5m | Titular | 57.4% |
| 11 | Deniz Undav | Germany | FWD | $6.6m | Titular | 3.3% |
| 12 | Emiliano Martínez | Argentina | GK | $5.0m | Banca | 28.4% |
| 13 | Felix Nmecha | Germany | MID | $5.6m | Banca | 8.5% |
| 14 | Rúben Dias | Portugal | DEF | $5.0m | Banca | — |
| 15 | Facundo Medina | Argentina | DEF | $4.0m | Banca | 7.8% |

- **Formación:** 3-4-3 (XI: Simón · Laporte, Konsa, Llorente · Dembélé, Vini, Bellingham, Manzambi · Messi, Mbappé, Undav)
- **Capitán:** Messi · **Vice:** Dembélé
- **Orden de banca:** E. Martínez (GK) + campo: Nmecha, Rúben Dias, Facundo Medina
- **Costo total:** $101.4M · **Presupuesto sin gastar:** $3.6M

## Recursos

- **Transfers libres para ronda 4:** ilimitadas (reset knockout)
- **Boosters intactos:** Wildcard · 12th Man · Maximum Captain · Qualification · Mystery
  _(ninguno usado hasta la ronda 3)_
