# Mi equipo — estado actual

> Estado inicial de toda recomendación (Fase 1). Actualizar tras cada deadline.
> Última actualización: 2026-06-13 — squad MD1 inscrito (validado con `wcf myteam`).

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
| **Rol MD1** | `Titular` o `Banca`, según tu XI actual | El orden de la banca va en el bullet de abajo |

## Squad (15)

| # | Jugador | Selección | Pos (juego) | Precio | Rol MD1 |
|---|---------|-----------|-------------|--------|---------|
| 1 | Emiliano Martínez | Argentina | GK | $5m | Titular |
| 2 | Thibaut Courtois | Belgium | GK | $4.9m | Banca |
| 3 | Joshua Kimmich | Germany | DEF | $5.5m | Titular |
| 4 | Nico Elvedi | Switzerland | DEF | $4.3m | Titular |
| 5 | Josip Stanisic | Croatia | DEF | $4.3m | Titular |
| 6 | Kim Min-Jae | Korea Republic | DEF | $5m | Titular |
| 7 | Johan Mojica | Colombia | DEF | $3.9m | Banca |
| 8 | Vitinha | Portugal | MID | $6.4m | Titular |
| 9 | Raphinha | Brazil | MID | $8.2m | Titular |
| 10 | Ryan Gravenberch | Netherlands | MID | $6.1m | Titular |
| 11 | Luis Díaz | Colombia | MID | $8.1m | Banca |
| 12 | Bruno Fernandes | Portugal | MID | $8.5m | Banca |
| 13 | Kylian Mbappé | France | FWD | $10.5m | Titular |
| 14 | Erling Haaland | Norway | FWD | $10.5m | Titular |
| 15 | Mikel Oyarzabal | Spain | FWD | $8.1m | Titular |

- **Formación:** 4-3-3 (XI: Martínez · Kimmich, Elvedi, Stanisic, Kim Min-Jae · Vitinha, Raphinha, Gravenberch · Mbappé, Haaland, Oyarzabal)
- **Capitán:** _(pendiente — confirmar)_ · **Vice:** _(pendiente — confirmar)_
- **Orden de banca (1–3, solo jugadores de campo):** _(pendiente — confirmar entre Mojica, Luis Díaz, Bruno Fernandes)_
- **Presupuesto sin gastar:** ~$0.7M (costo $99.3M anotado; confirmar con `wcf myteam`)

## Recursos

- **Transfers libres para MD2:** 2
- **Boosters intactos:** Wildcard · 12th Man · Maximum Captain · Qualification · Mystery
