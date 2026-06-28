# Reset R32 — squad óptimo (ILP)

> `wcf optimize` · presupuesto **$105.0M** · máx **3/país** · pool del 2026-06-28
> ⚠️ Óptimo sobre la **proyección v1** (form fix + clean sheet model). Cambios vs v0: usa `form`
> en lugar de `avgPoints` (corrige inflación por DNPs), y añade expectativa incremental de CS para GK/DEF.
> Constraints manuales: Manzambi forzado, Chávez y R. Vargas excluidos.
> Banca forzada: E. Martínez + Medina (Argentina, vs Cabo Verde), Rúben Dias (Portugal), Nmecha (Alemania).

## XI titular — 3-4-3 (proj 104.2, incluye capitán x2)

| Pos | Jugador | Sel | $ | Proj | CS | Own |
|---|---|---|---|---|---|---|
| GK | Unai Simón | Spain | 5.0 | 6.27 | +1.09 | 7.8% |
| DEF | Aymeric Laporte | Spain | 5.5 | 7.75 | +1.09 | 7.8% |
| DEF | Ezri Konsa | England | 4.8 | 7.44 | +1.52 | 2.2% |
| DEF | Marcos Llorente | Spain | 5.5 | 7.02 | +1.09 | 4.4% |
| MID | Ousmane Dembélé (V) | France | 10.0 | 10.26 | +0.26 | 19.1% |
| MID | Vinícius Júnior | Brazil | 10.0 | 9.77 | +0.20 | 31.8% |
| MID | Jude Bellingham | England | 8.3 | 8.19 | +0.30 | 14.2% |
| MID | Johan Manzambi | Switzerland | 5.6 | 7.62 | +0.09 | 1.9% |
| FWD | Lionel Messi (C) | Argentina | 10.0 | 10.84 | 0 | 37.4% |
| FWD | Kylian Mbappé | France | 10.5 | 10.0 | 0 | 57.4% |
| FWD | Deniz Undav | Germany | 6.6 | 8.18 | 0 | 3.3% |

**Costo total:** $101.4M · **banco:** $3.6M

**Capitán:** Messi · **Vice:** Dembélé

## Banca (orden de auto-subs)

- GK: Emiliano Martínez (Argentina, $5M, proj 5.70, cs +1.41 — vs Cabo Verde)
1. Felix Nmecha (MID Germany, $5.6M, proj 6.29, cs +0.19 — vs Paraguay)
2. Rúben Dias (DEF Portugal, $5M, proj 5.98, cs +0.80 — vs Croacia)
3. Facundo Medina (DEF Argentina, $4M, proj 5.88, cs +1.41 — vs Cabo Verde)

## Por qué cambió vs la versión anterior

| Swap | Motivo |
|---|---|
| Haaland ($10.5M, proj 7.42) → Undav ($6.6M, proj 8.18) | Fix de DNP: Haaland bajó de 9.70 a 7.42 al corregir `avgPoints→form`. Undav (R1:14, R2:14, R3:1 rotation) tiene forma real de 9.7 y matchup fácil (Alemania vs Paraguay). Ahorra $3.9M. |
| Sánchez México → Konsa Inglaterra | CS model: Konsa (Inglaterra vs Congo DR, diff +2.83) recibe +1.52 pts CS esperados — el bonus más alto de R32. Era invisible para el modelo anterior. |

## Matchups del XI

| Jugador | Equipo | Rival | Diff z | Certeza | CS bonus |
|---|---|---|---|---|---|
| Bellingham, Konsa | Inglaterra | Congo DR | +2.83 | muy fácil | +1.52 (DEF) |
| Messi | Argentina | Cabo Verde | +2.62 | muy fácil | 0 (FWD) |
| Dembélé, Mbappé | Francia | Suecia | +2.42 | muy fácil | 0 (FWD) |
| Simón, Llorente, Laporte | España | Austria | +2.04 | muy fácil | +1.09 (GK/DEF) |
| Vini | Brasil | Japón | +1.90 | fácil | 0 (FWD) |
| Undav | Alemania | Paraguay | +1.76 | fácil | 0 (FWD) |
| Manzambi | Suiza | Argelia | +0.93 | moderado | +0.09 (MID) |

## ⚠️ Verificar antes del lockout

- **Undav**: R3=1pt fue rotación (no lesión). Confirmar que arranca vs Paraguay.
- **Konsa**: matchStatus no confirmado aún. Verificar XI de Inglaterra antes del 1 Jul.
