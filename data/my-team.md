# Mi equipo — estado actual

> Estado inicial de toda recomendación. Actualizar tras cada deadline.
> Última actualización: 2026-06-26 — squad vigente entrando a la **ronda 4** (lockout 28 jun 20:00).
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
| 1 | Emiliano Martínez | Argentina | GK | $5m | Titular | 26.3% |
| 2 | Joshua Kimmich | Germany | DEF | $5.5m | Titular | 25.8% |
| 3 | Lisandro Martínez | Argentina | DEF | $4.6m | Titular | 5.5% |
| 4 | Nahuel Molina | Argentina | DEF | $4.4m | Titular | 2.8% |
| 5 | Alexander Freeman | USA | DEF | $4m | Titular | 4.9% |
| 6 | Luis Díaz | Colombia | MID | $8.1m | Titular | 14.3% |
| 7 | Johan Manzambi | Switzerland | MID | $5.6m | Titular | 0.7% |
| 8 | Bruno Fernandes | Portugal | MID | $8.5m | Titular | 37.5% |
| 9 | Kylian Mbappé | France | FWD | $10.5m | Titular | 54.8% |
| 10 | Erling Haaland | Norway | FWD | $10.5m | Titular | 26.3% |
| 11 | Mikel Oyarzabal | Spain | FWD | $8.1m | Titular | 11.7% |
| 12 | Thibaut Courtois | Belgium | GK | $4.9m | Banca | 12.5% |
| 13 | Kim Min-Jae | Korea Republic | DEF | $5m | Banca | 2.2% |
| 14 | Vitinha | Portugal | MID | $6.4m | Banca | 9.5% |
| 15 | Raphinha | Brazil | MID | $8.2m | Banca | 11.5% |

- **Formación:** 4-3-3 (XI: E. Martínez · Kimmich, L. Martínez, Molina, Freeman · Luis Díaz, Manzambi, Bruno Fernandes · Mbappé, Haaland, Oyarzabal)
- **Capitán:** Mbappé · **Vice:** Haaland _(ambos ya jugaron en la ronda en curso)_
- **Orden de banca:** Courtois (GK) + campo: Raphinha, Vitinha, Kim Min-Jae _(confirmar orden 1–3)_
- **Costo total:** $99.3M · **Presupuesto sin gastar:** _(confirmar con `wcf myteam`)_

## Recursos

- **Transfers libres para ronda 4:** _(confirmar en el juego)_
- **Boosters intactos:** Wildcard · 12th Man · Maximum Captain · Qualification · Mystery
  _(ninguno usado hasta la ronda 3)_
