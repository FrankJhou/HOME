# Game Design Document: The Vanished Cartographer

## Overview
- **Genre:** Point-and-click escape room / puzzle
- **Platform:** Web browser (HTML/CSS/JS, single file, desktop + mobile)
- **Player count:** Single player
- **Session length:** 10–25 minutes
- **Tone:** Gothic-adventure, candlelit study, old maps and brass instruments

## Premise
The cartographer vanished three nights ago, leaving his manor locked from within. The player has until dawn to search three connected rooms — the Study, the Library, and the Observatory — find what each hides, and unlock the final door before the deadline.

## Core Loop
1. Click a hotspot in the current room to inspect it.
2. Read/solve what it presents (riddle, cipher, dial, keypad, word lock).
3. Collect items and clue text into a persistent **Journal** and **Inventory**.
4. Use clues from earlier hotspots to solve later ones, including the room's exit puzzle.
5. Solving a room's exit puzzle unlocks the next room's tab.
6. Repeat until the Final Door in the Observatory is solved — timer stops, win screen shown.

## Rooms & Puzzle Chain

### Room 1 — Study
| Hotspot | Puzzle Type | Output |
|---|---|---|
| Painting | Word-math riddle (MIDNIGHT − DUSK letters) | Digit 1 = 4 |
| Stopped Clock | Direct read (2:09) | Digits 2 = 2, 3 = 9 |
| Bookshelf Ledger | Caesar cipher, shift given by painting | Digit 4 = 7 (word SEVEN) |
| Desk Drawer | 4-digit keypad ("4729") | Brass Key 1 + bearing note (NW) |
| Wall Safe | Drag-to-bearing dial (315°, ±12°) | Unlocks Library |

### Room 2 — Library
| Hotspot | Puzzle Type | Output |
|---|---|---|
| Star Atlas | Symbol legend (reference only) | ☀=T ☾=I ★=D ⚓=E |
| Locked Cabinet | Word-entry lock using legend ("TIDE") | Brass Key 2 + globe bearing (200°) + plaque digits 5, 3 |
| Globe | Drag-to-bearing dial (200°, ±12°) | Unlocks Observatory |

### Room 3 — Observatory
| Hotspot | Puzzle Type | Output |
|---|---|---|
| Star Chart | Reference note | Azimuth target 65° |
| Telescope | Drag-to-bearing dial (65°, ±10°, tightest tolerance) | Brass Key 3 + final code "2953" |
| Final Door | 4-digit keypad, gated by having all 3 keys + telescope solved | Win condition |

## Systems

### Inventory
- Global, persists across rooms.
- Displays collected items as chips (icon + label).
- Used as a hard gate on the Final Door (must hold 3 keys before code entry unlocks).

### Journal
- Global, persists across rooms, grouped by room.
- Logs every clue the player has actually found — nothing is pre-filled.
- No hint system; the player must retain/re-derive combined answers themselves.

### Room Navigation
- Tab bar: Study / Library / Observatory.
- Locked tabs show a 🔒 icon and reject clicks with a flavor message until unlocked.
- Unlocking a room triggers a short transition modal and reveals its tab.

### Dial Widget (reusable)
- Draggable SVG needle, pointer/touch supported.
- Bearing computed via `atan2` relative to dial center.
- "Lock it in" button checks angular distance vs. target within tolerance; wrong attempts trigger a shake animation + resistance message.

### Keypad Widget (reusable)
- On-screen numeric pad, fixed-length buffer, Enter/Clear.
- Wrong code clears buffer and shows an inline message; no penalty beyond time.

### Timer
- Starts on first hotspot interaction (not on page load).
- Runs continuously until Final Door is solved.
- Displayed as MM:SS, shown again on the win screen as the score.

## Difficulty Design Notes
- Each room requires synthesizing 2–3 separate clues before its exit puzzle can be attempted — no single hotspot is self-sufficient.
- Tolerances on the drag-dials tighten room to room (±12° → ±12° → ±10°) to escalate precision demands.
- The Final Door adds a compound gate (inventory count AND code AND prior puzzle state) rather than a single check, to prevent sequence-breaking.
- No hint button by design; difficulty is sustained by requiring the player to hold/recall combined information rather than by obscuring individual clues unfairly — every needed fact is stated plainly somewhere, just not in one place.

## Win/Loss State
- **Win:** Final Door code accepted → timer stops → win modal shows elapsed time and a "Play again" reset (full page reload).
- **Loss:** None; the game is untimed against a countdown, only scored by elapsed time, so there is no fail state — only replay-for-a-better-time incentive.

## Art & Audio Direction
- **Palette:** deep ink navy (#0e1526–#22304f), aged paper cream (#ece0bd), brass/gold (#c9a24d/#e8c876), oxblood wax accent (#8a3324), muted teal (#3f6259).
- **Type:** Cormorant Garamond (display/headers), EB Garamond (body/notes), Courier Prime (UI chrome, ciphers, keypads).
- **Visuals:** Flat SVG scenes per room (no external image assets), brass-outlined hotspots that glow gold on hover.
- **Audio:** None implemented in current build; candidate future addition (ambient room tone, dial click, drawer creak, door unlock sting).

## Tech Notes
- Single HTML file, vanilla JS, no build step, no external JS dependencies (Google Fonts only).
- Event delegation on a single scene container so room-swapping via `innerHTML` doesn't require re-binding listeners.
- All puzzle state held in one `state` object; rooms are pure functions returning SVG markup strings.

## Future Expansion Ideas
- 4th room ("Vault") as a harder postgame/bonus chain.
- Leaderboard via best elapsed time (would need persistent storage).
- Optional hint system with a time penalty, for accessibility.
- Sound design pass.
