# Content branch: what this adds to Battle Drones

Battle Drones is created by [Simon Willison](https://github.com/simonw/battledrones) (Apache-2.0).
This branch (`content`) adds gameplay on top of his `v14`; the `main` branch only changes the look.
Everything here changes the simulation, so **replays recorded on `v14` still verify** (the showcase
record ends on the same world hash, `fb0e5718`) but a duel between this build and stock v14 cannot
pair: `CODEC_VERSION` is 3.

## Juggernaut (unit)

Siege artillery walker, built at the Fab Plant behind the Tech Lab (`UNITS.juggernaut` in `src/sim/balance.ts`).

| | Juggernaut | Mortar (for scale) |
|---|---|---|
| Cost | 650 | 275 |
| HP / armour | 900 / heavy | 195 / light |
| Range / min range | 13 / 4 | 8 / 2.5 |
| Shell | 1 per 5 s, splash 1.6, explosive | 1 per 3 s, splash 1.1 |
| Speed / sight | 0.9 / 6 | 1.5 / 6 |

It needs a spotter (its sight is short), cannot fire inside 4 tiles and cannot hit air.
The AI builds up to two once the enemy has two or more defences and it has an army of six.

Cost-equal duel matrix (`npx vite-node tools/balance.ts duels`, 1,800 scrap each, + = Juggernaut wins):
Flak +1.08, Mortar +0.86, Trooper +1.00, Rocket Squad +0.94, Sniper +1.02, Stinger +0.45, Raptor +0.11;
Mastodon −0.31, Lancer −0.32, Wasp −0.59, Hornet −0.24. It out-ranges light armies and infantry; heavy
tanks, Lancers and anything fast close the distance and win.

## Repair (building command)

Select a damaged building and press **Repair** (HQ included): it regains 4% of its max HP per second
for 30% of its price per full bar, paid in whole scrap each second. It pauses for 3 s after a hit and
while scrap is short, and switches itself off at full health. `ECONOMY.repairRate`, `repairCost` and
`repairQuiet` hold the numbers; the command type is `repair`, encoded like `sell`.

## How to check a change

`npx tsc --noEmit`, `npx vitest run`, and
`npx vite-node tools/check-record.ts battles/showcase/2026-10-11-riverlands-42-gpt-6-luna-vs-gpt-6-luna.json`
(must print `final fb0e5718`). Use Node 24: on Node 20 seven timer-based tests fail.
