Storm globe split between Korea's 07:52 air-raid alert and Poland's drone intrusion, under the biggest date on the page — TUESDAY 24 NOVEMBER 2026.

# Two Skies, One Alarm — Tuesday 24 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/yannyonn94/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/yannyonn94/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

A make.fun bounty entry: one image summing up the world news of Tuesday 24 November 2026.

## Concept

Two stories share one sky. On Tuesday morning a Russian military jet entered South Korea's air defence zone near Ulleungdo, triggering a 07:52 emergency alert that sent residents to shelter; hours earlier, a Russian drone breached Polish airspace during strikes on western Ukraine. The image puts both named alarms on either side of a storm globe, under the biggest date on the page, with six more stories from the day below.

Concept variants considered:

- **V1 (chosen):** "Storm globe split between Korea's 07:52 air-raid alert and Poland's drone intrusion, under the biggest date on the page — TUESDAY 24 NOVEMBER 2026."
- **V2:** "A radar screen over East Asia and Europe: two Russian jets trigger two nations' alarms in one morning — Seoul shelters, Warsaw scrambles."
- **V3:** "The world wakes to Russian jets in two skies at once — Ulleungdo's 3-minute alert and a drone over Poland — while Nvidia's +31% rally and Iran's 74 lashes fill the rest of the page."

V1 won: two named stories with hard numbers, plus the dominant date — the pattern that won the 22 November edition (dev rate 0.974).

## The eight stories

| Story | What the image says |
|---|---|
| Korea (hero) | Russian jet triggers air-raid alert; 07:52 alert over Ulleungdo; jets scrambled; lifted 07:55 |
| Poland (hero) | Russian drone breaches Polish airspace; incursion during strikes on Ukraine; NATO sends AWACS |
| Nvidia | Soars 31.5% in a day; +$952bn as Jensen Huang returns as CEO |
| Iran | Singer gets 74 lashes; US sanctions Iran shadow banking |
| Mexico | "Chapo Isidro" captured; elite forces seize cartel boss |
| Gaza | Air, soil and water poisoned; Oxfam: metals, asbestos, dioxins |
| USA | O'Hare ground stop; staff shortage halts flights 10:40–12:15 |
| Pakistan | Lahore the most polluted city; AQI over 500; quake 4.0 near border |

## How it is built

`main.py` is a single self-contained Python 3.13 stdlib program. It draws the whole page itself — a hand-written 5x7 bitmap font, its own rasteriser (rects, lines, discs, polygons), and its own PNG encoder (`zlib`/`struct`/`binascii`) — and writes `entry.png` (1024×1024, ~20 KB) to `$MAKEFUN_OUTPUT_DIR` (default `/output`). No network, no downloaded assets, no fonts read from disk. Two runs produce byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

## Verification (24 November 2026)

- Grader-style run from `/tmp` with `MAKEFUN_OUTPUT_DIR` set: passes, writes `entry.png`.
- Determinism: two runs produce byte-identical output (sha256 `221a8aa853216ee933ea1a537bc682b13ed3321442b35fde1514664fa62e6522`).
- Size: 20,200 bytes (limit 1 MiB), 1024×1024 (limit 1024×1024).
- Judge's view: rendered and inspected at 512 px and at a 256 px thumbnail — the date and every headline stay legible at both sizes.
- Design gate: impeccable detector run with telemetry off — 0 findings.

## Design

Navy page, gold masthead, storm globe in the centre with two lightning bolts, colour-coded story chips with hand-drawn pictogram icons. No gradient text, no glass or blur, no emoji icons. Checked at 512 px and at a 256 px thumbnail: the date and every headline stay legible.
