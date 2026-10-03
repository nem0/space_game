# Objectives — Opening Chain

**Status:** First-pass design. Reward and trigger numbers are provisional. Objectives are the game's tutorial and its pacing: they name a *problem*, never the solution. The late game is deliberately left open (see the end of this file).

## Philosophy

- **Hardcore survival.** The opening is a pile of simultaneous crises. The player is expected to die and restart a few times before finding the right order. A restart must be quick (new game in seconds, no setup).
- **Problems, not instructions.** Each objective shows its symptom and live numbers ("CO₂ 7 400 ppm and rising"), not what to build. Failure consequences are not forecast beyond the raw HUD numbers; the player works out that no food means death.
- **Scarcity is the puzzle.** The start gives no spare materials worth building with, and nothing may be dismantled that the station still needs. The first real materials come from the first EVA haul.
- **Only non-research objectives grant RP.** Completing a *research* objective grants nothing but the unlock. Every *build / act* objective grants RP (sizes below), so objectives fund the first techs and the research bench funds the rest. RP banked before the bench exists is kept.
- **Needs trigger unlocks.** Medical, fitness and greenhouse objectives appear when the need appears, not at a fixed point in the list.

RP reward sizes: **S = 30**, **M = 60**, **L = 100**. For scale, the opening techs cost 25–150 RP (see `tech_tree.md` → *Opening technologies*).

## The starting state

- **Crew:** 2–3.
- **Central Module:** damaged. HP 50%, so CO₂ scrubbing runs at half output and the cabin CO₂ climbs.
- **Materials:** a small starter stock of steel, polymers and electronics, enough to pay for *part* of the module repair, not all of it.
- **Orbit:** low and decaying. Start altitude is lowered so the station is already close to the warning level (target ≈ 350 km; warning 330 km). Start fuel pays for one or two emergency burns, not for the climb to 420 km.
- **Water:** a finite tank with **no recycling**. Net use equals gross use, so water falls steadily.
- **Food:** about 8 days for a crew of 2 (50 000 kcal), and no farm.
- **Power:** the six roof panels and nothing else. No battery, so every orbital night is a blackout.
- **Unlocked at start:** the research bench rack, basic hull, berth, O₂ generator, CO₂ scrubber, small solar panel, heat vent, crate, fuel and O₂ tanks. Everything else is researched.

## Phase 1 — Survive (all active from the start)

| # | Objective | Problem shown | Completes when | Reward |
|---|---|---|---|---|
| 1 | **Fix the CO₂** | CO₂ ppm rising; Central Module at 50% HP | Cabin CO₂ below the warning level (5 000 ppm) and the Central Module repaired | S |
| 2 | **Stop the descent** | Altitude falling, with a time-to-warning forecast | One emergency reboost burn done and altitude back above 375 km | S |
| 3 | **Build the research bench** | Nothing can progress without research | A research bench rack is fitted and staffed | M |
| 4 | **First EVA haul** | No materials to build or fix anything | The first nearby-scrap run returned | M |
| 5 | **Survive the night** | Everything shuts down on the dark side | A battery rack is built (after researching *Energy Storage*) and the station gets through one eclipse with no blackout | M |
| 6 | **Feed the crew** | Food below 3 days of reserve | Hydroponics online (after researching it) and food production ≥ consumption | M |
| 7 | **Stop the water loss** | Water falling every day | A water recycler rack online (after researching it) and recovery ≥ 80% | M |

Notes:
- **#1 is the opening dilemma.** The starter stock cannot repair the module alone. The gap is covered by dismantling something (50% of its materials come back). The small solar panel is the only good choice: dismantling another source of repair material costs life support, cooling or storage the station needs. Removing the panel costs 2 kW, which makes #5 more urgent.
- **#2 and the fuel chain.** The emergency burn uses the starting fuel. Fuel production is Phase 2.
- **#4 is not optional in practice.** The materials for #5, #6, #7 and the recycler all come from the EVA haul, and nothing else can be dismantled safely.
- **Research objectives** (*Energy Storage*, *Hydroponics*, *Water Recycling*) appear inside #5, #6, #7 as their first step. They are research tasks with no RP reward; the build step carries the reward.

## Phase 2 — Foundations (unlock after #3 and #4)

| # | Objective | Trigger | Completes when | Reward |
|---|---|---|---|---|
| 8 | **Build another module** | ≥ 80% of rack slots in use | A second hull is built and connected | M |
| 9 | **Research fuel production** | After #3 | *Fuel Production* researched | none |
| 10 | **Research and build solar arrays** | After #9 (the fuel producer needs more power than small panels give) | *Solar Arrays* researched; one Solar Wing built | M |
| 11 | **Research and build a radiator** | After #9, or when waste heat exceeds cooling | *Thermal Management* researched; one Radiator Wing built | M |
| 12 | **Research and build a workshop bench** | After #3 | *Workshop* researched; one workshop bench fitted and staffed. Workshop parts feed the solar array build | M |
| 13 | **Build a fuel producer** | After #9, #10, #11 and #12 | Fuel producer online and making propellant | L |
| 14 | **Reach high orbit** | After #13 | Altitude ≥ 420 km | L |

Notes:
- The fuel producer needs power (solar arrays), cooling (radiator), water (from the recycler, #7) and machine parts (from the workshop). The chain is intentionally long; each link is a visible block on the producer's panel ("needs 6 kW more power", "needs water").
- **Orbit.** 420 km is the target a reboost burn stops at. Decay at 420 km is lower than at 350 km but never zero, so station-keeping fuel stays an ongoing cost; #14 is a milestone, not the end of the problem.

## Phase 3 — Needs-triggered

These appear when the need shows up.

| # | Objective | Trigger | Completes when | Reward |
|---|---|---|---|---|
| 15 | **Research a medical rack** | First crew injury | *First Aid* researched | none |
| 16 | **Build a medical rack** | After #15 | Rack fitted; an injured crew member treated | M |
| 17 | **Research a medical bay** | First serious injury | *Medical Bay* researched | none |
| 18 | **Build a medical bay** | After #17 | Medical bay built; a seriously injured crew member nursed back to health by another crew member | M |
| 19 | **Research an exercise machine** | Any crew member's fitness below 50% | *Exercise Machine* researched | none |
| 20 | **Build an exercise machine** | After #19 | Machine fitted; a crew member uses it | S |
| 21 | **Research a greenhouse** | Food production cannot feed one more crew member while a berth is free | *Greenhouse* researched | none |
| 22 | **Build a greenhouse** | After #21 | Greenhouse beds online | L |

### Robots (needs-triggered, design only)

| # | Objective | Trigger | Completes when | Reward |
|---|---|---|---|---|
| 30 | **Research robotics** | After #12, and at least two jobs have waited with nobody free for a game day (a paused or unstarted job while every crew member is busy) | *Robotics* researched | none |
| 31 | **Put a robot to work** | After #30 | A Robot bay is fitted, a Service robot built, and it finishes a job | M |
| 32 | **Research orbital robotics** | A Service robot has finished a job and a docking hub is built | *Orbital Robotics* researched | none |
| 33 | **Send a robot outside** | After #32 | A Builder robot finishes an external job or an EVA run | M |
| 34 | **Fly unmanned** | After #33 and the shuttle (#28) | *Autonomous Navigation* researched and a Long-range robot has brought a mission back | L |

Problem text for #30: "There is more work than hands." The objective names the symptom; the player works out that robots are the answer. #32 to #34 follow the same pattern for the Builder and Long-range robots.

## Phase 4 — Reaching out

| # | Objective | Completes when | Reward |
|---|---|---|---|
| 23 | **Research radar** | *Radar* researched | none |
| 24 | **Build radar** | A radar attachment is fitted and online | M |
| 25 | **Research a docking port** | *Docking Operations* researched | none |
| 26 | **Build a docking port** | A docking hub built | M |
| 27 | **Research a spaceship** | *Shuttle* researched | none |
| 28 | **Build a spaceship** | A shuttle built and docked | L |
| 29 | **Run a mission** | First mission with the shuttle returned | L |

## The late game (open)

Left open on purpose. After the first mission the game opens up to the broad design in `game.md`: rescuing survivors, trade, pirates and the three long-term endings (orbital civilization, a new world, Earth restoration). Their objectives will be written once those systems exist. Until then the win condition stays the one in `scripts/config.evox`.

## Implementation status

Implemented in `scripts/config.evox`, `scripts/objectives.evox` (the chain and its triggers), `scripts/sim.evox`, `scripts/state.evox`, `scripts/hud.evox` and `ui/hud.ui` (OBJECTIVES tab, water, the new tech tree). Deviations and tuning choices:

- **Start state:** altitude 360 km, fuel 160 kg, water 160 L (no recycling), the Central Module at 50% HP, and a starter stock of 90 steel, 36 polymers, 40 electronics and 20 machine parts (`START_*`), plus an O₂ generator rack on the Central Module (at 50% HP its own oxygen is not enough for two crew). The stock repairs the module to about 95%; the last few kg for "fixed" (HP ≥ 99%) come from dismantling something (the small solar panel is the cheap choice). Playtested: the unattended CO₂ reaches 12,000 ppm in 10 h; a repair started at once peaks near 12,500 ppm and the crew survive. Repairs take 6 min per kg (was 10).
- **Night:** solar power (attachments and solar wings) is zero in Earth's shadow, about 39% of each orbit. The radioisotope generator (+5 kW, an attachment, preinstalled on the Central roof) keeps running. Objective #5 counts an eclipse passed on batteries with no brownout.
- **Sorting:** with no workshop bench anywhere the crew hand-sort salvage at 10 kg/h. Once a workshop bench exists it must be staffed.
- **EVA:** the existing "nearby scrap" run is the EVA haul (#4). It brings a little water and 2–8 kg of fuel; debris and asteroid missions bring more water.
- **Injuries:** 4% per crew member per day, 12% after a mission (35% after a failed one), a quarter of them serious. The Medical Bay is not a separate rack: it is a working medical rack once *Medical Bay* is researched. The caregiver is assigned automatically (an idle crew member).
- **Techs:** 29 technologies (the original 20 plus water recycling, first aid, medical bay, exercise machine, solar arrays, workshop, radar, shuttle, fuel production). *Medical Training* now only speeds fitness recovery. Racks 13 (water recycler) and 14 (fuel producer) reuse placeholder card sprites (`ui/rth_13.spr`, `rth_14.spr`).
- **Not done:** the late game (open); water use by hydroponics and by the fuel producer's heat; sprites for the new racks.
