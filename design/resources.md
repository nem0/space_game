# Resources and Economy — Real-Unit Draft

**Status:** Prototype economy spec using physical units where meaningful. These are gameplay-scale engineering approximations, not a detailed spacecraft life-support simulator. Balance remains provisional. See [`modules.md`](modules.md), [`crew.md`](crew.md), and [`tech_tree.md`](tech_tree.md); their earlier RU figures should be treated as superseded placeholders wherever they conflict with this document.

## Unit conventions

- **Solid materials and cargo mass:** kilograms (kg); bulk cargo capacity and module storage are shown in cubic metres (m³) as well as mass where useful.
- **Liquids:** litres (L). For water, 1 L ≈ 1 kg.
- **Gases:** kilograms (kg) in stores and kg/day in life-support flows. Tank volume is shown in litres or m³.
- **Food:** kilocalories (kcal) for nutrition; packaged food mass in kg for cargo.
- **Power:** kilowatts (kW) for rate and kilowatt-hours (kWh) for stored/used energy.
- **Research:** research points (RP) and digital data in gigabytes (GB).
- **Time:** rates use a 24-hour station day; crew work is in worker-hours (wh).
- **Construction costs:** `kg material`; module mass is distinct from its construction-material bill. Cargo volume is distinct from cargo mass.

## Resource inventory

| Resource | Unit | Main sources | Main uses / storage |
|---|---|---|---|
| **Mixed salvage** | kg, m³ | Salvage operations, derelicts | Unsorted cargo; requires sorting. Capacity is limited by cargo mass and volume. |
| **Steel stock** | kg | Steel scrap processing, trade, intact recovered stock | Hulls, frames, machinery, construction. Dry bulk storage. |
| **Aluminum stock** | kg | Aluminum-bearing scrap processing, trade | Lightweight structures, radiators, craft parts. Dry bulk storage. |
| **Copper/conductors** | kg | Electronics and cable salvage, processing | Wiring, motors, fabrication. Secure/dry storage. |
| **Polymers** | kg | Polymer scrap processing, trade | Seals, hoses, insulation, farm fittings. Dry storage. |
| **Glass / ceramics** | kg | Silicate processing, trade | Viewports, labware, heat-resistant parts. Fragile storage. |
| **Electronics** | kg | Recovered intact, electronics repair, trade | Sensors, controls, module construction. Secure dry storage. Track electronics as discrete components as well as mass when recipe identity matters. |
| **Machine parts** | kg | Fabrication, intact salvage, trade | Repairs and machinery construction. Dry storage. |
| **Water** | L | Ice processing, recycling, trade | Drinking, hygiene, farms, electrolysis. Tanks; account for leakage. |
| **Water ice** | kg | Salvage, extraction, trade | Melted and purified into water. Insulated storage. |
| **Oxygen** | kg | Life support, electrolysis, trade | Atmosphere and emergency reserve. Pressurized tanks. |
| **Food** | kcal and kg | Farms, trade, salvage | Crew nutrition. Refrigerated mass storage; shelf-life losses apply. |
| **Nutrients** | kg | Manufacture, trade, salvage | Hydroponics. Dry storage. |
| **Hydrogen** | kg | Water electrolysis | Potential fuel/industrial feedstock after research. Pressurized storage. |
| **Propellant (fuel)** | kg | Salvage, trade; later hydrogen from electrolysis | Orbit reboost burns, later salvage craft. Pressurized tanks (Central Module, Gas Storage). |
| **Reactor fuel** | kg | Salvage, trade, specialized production | Reactor operation. Secure, shielded storage. Fuel type and energy density TBD. |
| **Maintenance supplies** | kg | Fabrication, trade, salvage | Scheduled repairs and upkeep. Dry storage. |
| **Digital data** | GB | Surveys, recovered records, trade | Research input; does not occupy physical cargo volume unless carried on hardware. |
| **Waste / slag** | kg, m³ | Sorting, refining, crew activity, production | Stored until recycled or disposed of; output must not disappear without a system. |

**Power is not an inventory resource.** Crew labor, health, fatigue, morale, and radiation dose are also separate simulation values.

## Cargo capacity and mass

To avoid an arbitrary “resource unit,” every cargo stack has a mass and a bulk volume. Initial planning densities (adjustable):

| Cargo | Approx. bulk density |
|---|---:|
| Steel / aluminum stock | 2,000 kg/m³ |
| Copper / conductors | 1,500 kg/m³ |
| Polymers | 600 kg/m³ |
| Glass / ceramics | 1,200 kg/m³ |
| Food packages | 500 kg/m³ |
| Water | 1,000 kg/m³ |
| Mixed salvage | 300 kg/m³ (loose, irregular cargo) |
| Electronics / machine parts | 500 kg/m³ |

Cargo capacity is the lower of the mass limit and volume limit. Trade and salvage interfaces display both. Unsorted salvage occupies more volume than sorted materials; sorting reduces volume by 30% on average.

## Crew consumption and life support

Baseline for a healthy adult crew member per 24-hour day:

- **Food:** 2,500 kcal/day. Use an average packaged ration energy density of 2,500 kcal/kg, so this is approximately **1.0 kg food/day/person**. Actual fresh crops may have different mass and energy density; recipes track nutrition in kcal, not merely kilograms.
- **Water:** **3.0 L/day gross potable/drinking use**. Hygiene and food preparation are modeled separately through module demand; for an initial simplified total station water budget, use **10 L/person/day** including drinking, hygiene, and food preparation.
- **Oxygen:** **0.84 kg/person/day gross metabolic consumption**; carbon dioxide output is approximately 1.0 kg/person/day and must be scrubbed or stored/processed. These are rounded game values.
- **Power:** Personal consumption is represented by habitat/module loads, not subtracted as a separate crew resource.

### Water recovery

**Opening state:** the station starts with a finite water tank and **no recycling**, so net use equals gross use and the tank drains every day. Recovery (80%) only starts once a **water recycler** rack is fitted (researched via *Water Recycling*). Without one the only source is water ice from EVA hauls.

Life-support water recovery is a fraction of wastewater collected, not a magical net addition:

- Baseline recovery target: **80% of the 10 L/person/day station water use**.
- Net make-up water at baseline: **2 L/person/day**, plus losses from leaks, crop consumption, and processing.
- Galley/hygiene technology should modify the total demand only if specified; do not apply a second overlapping water discount.
- Farms consume water that is partly transpired/retained in crops. Set farm recipe consumption separately and avoid counting it again as crew wastewater.

### Oxygen and carbon dioxide

- Baseline oxygen recovery: **70% of crew metabolic oxygen demand** if the life-support module has sufficient power and capacity; make-up oxygen is **0.252 kg/person/day**.
- Carbon dioxide capture must be represented as a separate process or included in life-support capacity. For the initial model, life support captures 1.0 kg CO₂/person/day and does not convert it to oxygen unless a technology explicitly unlocks that process.
- A Life-Support Module's capacity must be expressed in people (e.g. 20 people) and checked against the above mass flows. Do not use the old RU/day capacities.

## Salvage yield and uncertainty

A typical local salvage operation targets **1,000 kg of recovered cargo** before its risk/yield modifiers. Example manifest (illustrative, site-dependent):

- 400 kg mixed ferrous/non-ferrous scrap
- 200 kg polymers and silicates
- 100 kg electronic scrap
- 100 kg intact parts or equipment
- 200 kg variable cargo: water ice, packaged food, data hardware, additional scrap, or waste

Scans show estimates with ±50% mass error initially; Sensor / Communications Mast reduces error to ±20%. Salvage Control increases recovered mass by 10 percentage points and reduces incident chance by 10 percentage points (subject to probability bounds). The operation's craft and docking capacity may cap cargo mass and volume; excess material is left behind unless another trip is arranged.

## Processing recipes (initial targets)

All recipes show inputs and outputs by real mass/volume. Processed output can be less than input due to contamination, sorting losses, and slag. Power draw is stated separately and is never an ingredient. Rates assume a fully staffed, operating module for 24 hours.

### Workshop

The early production room (see `modules.md`). It runs one job at a time from a queue the player orders; switching jobs is free, and a job with missing inputs is skipped with a message rather than stalling the queue.

| Job | Inputs → outputs | Rate | Power | Staff |
|---|---|---:|---:|---:|
| Sort mixed salvage | Mixed salvage → same split as the Sorting Bay batch below | 600 kg/day (25 kg/h) | 6 kW | 1 |
| Machine parts | 40 kg steel + 10 kg conductors + 10 kg polymers → 50 kg machine parts + 10 kg waste | 0.5 batch/day | 6 kW | 1 |
| Maintenance kits | 20 kg machine parts + 5 kg polymers → 20 kg maintenance supplies + 5 kg waste | 0.5 batch/day | 4 kW | 1 |
| Electronics recovery | 20 kg electronic scrap + 5 kg conductors → 10 kg electronics + 15 kg waste | 0.5 batch/day | 4 kW | 1 |
| Damaged electronics repair | 20 kg damaged electronics + 2 kg machine parts → 15 kg electronics + 7 kg waste | 0.5 batch/day | 4 kW | 1 |

- A second assigned worker raises the rate by 50% (not 100%: one bench, shared tools). Fabrication skill applies as for the dedicated modules.
- Without a Workshop, the crew can still hand-sort in the Central Module at **240 kg/day** (10 kg/h, 5 kW), enough to survive but not to grow.
- Until conductors, electronic scrap and damaged electronics exist as resources, the prototype folds them into electronics.

**Current prototype (implemented):** a workshop bench (rack) runs one job, chosen with its job button in the module panel, while a crew member is staffed at it: **sort** salvage (25 kg/h), **machine parts** (40 kg steel + 10 kg polymers + 5 kg electronics -> 45 kg parts, 10 h) or **repair kits** (15 kg steel + 6 kg polymers -> 1 kit, 3 h). Batches take their inputs at the start and wait when inputs are missing. A kit covers the repair material of 1.5 t of station; with enough kits a repair uses them instead of steel and polymers and takes 30 min. Values in `scripts/config.evox` (workshop jobs).

### Sorting Bay

**Current prototype (implemented):** salvage runs return 400–900 kg of mixed salvage (plus sealed propellant tanks, which need no sorting). Until the Workshop / Sorting Bay modules exist, the Central Module sorts it automatically at 40 kg per game hour (above the 10 kg/h hand-sorting target, so the loop stays playable without a Workshop) (station efficiency applies, 5 kW while running, at least one crew aboard) into 45 % steel, 20 % polymers, 10 % electronics, 10 % machine parts and 15 % waste; aluminum, conductors and glass are folded into those four until they become resources, and waste is discarded until it is tracked. Mixed salvage needs cargo hold space: 1,500 kg in the Central Module, 3,000 kg per Storage module; a haul beyond it is left behind. Values are in `scripts/config.evox`.

**Mixed salvage sorting, one daily batch:**
- Input: 1,000 kg mixed salvage, occupying approximately 3.33 m³.
- Output: 360 kg steel-bearing scrap; 120 kg aluminum-bearing scrap; 100 kg conductors/electronic feed; 160 kg polymers; 100 kg silicate/glass feed; 60 kg recoverable electronics/parts; 100 kg waste.
- Rate: 1 batch/day; 2 workers per shift; 5 kW while operating.
- Output totals 1,000 kg; sorting changes categories and volume, not mass. Refining later removes contaminants into waste/slag.

### Materials processing

- **Steel refining:** 500 kg steel-bearing scrap → 350 kg steel stock + 150 kg slag. One batch/day; 12 kW while operating; 2 workers.
- **Aluminum refining:** 200 kg aluminum-bearing scrap → 140 kg aluminum stock + 60 kg slag. One batch/day; 8 kW; 1 worker.
- **Polymer recovery:** 200 kg polymer scrap → 120 kg usable polymers + 80 kg waste. One batch/day; 5 kW; 1 worker.
- **Silicate processing:** 200 kg silicate feed → 140 kg glass/ceramics + 60 kg waste. One batch/day; 6 kW; 1 worker.
- These recipes are independent; a processor can only run one recipe at a time unless a later multi-line module explicitly permits parallel processing.

### Fabrication

- **Machine parts:** 40 kg steel + 10 kg conductors + 10 kg polymers → 50 kg machine parts + 10 kg waste. Rate: 1 batch/day; 6 kW; 1 Fabrication worker.
- **Maintenance kits:** 20 kg machine parts + 5 kg polymers → 20 kg maintenance supplies + 5 kg waste. Rate: 1 batch/day; 4 kW; 1 worker.
- **Electronics recovery:** 20 kg electronic scrap + 5 kg conductors → 10 kg usable electronics + 15 kg waste. Rate: 1 batch/day; 4 kW; 1 worker.
- **Damaged electronics repair:** 20 kg damaged electronics + 2 kg machine parts → 15 kg usable electronics + 7 kg waste. Rate: 1 batch/day; 4 kW; 1 worker.

### Water, oxygen, and food

- **Ice purification:** 100 kg water ice → 90 L potable water + 10 kg mineral waste. Rate: 100 kg/day per processing line; 3 kW; 1 worker. (90 L water is approximately 90 kg.)
- **Electrolysis:** 9 L water → 1.0 kg oxygen + 0.125 kg hydrogen. Consumes approximately 5 kWh per batch; outputs rounded for gameplay, with remaining mass treated as process loss/condensate. Requires an electrolysis-capable module and pressurized tanks.
- **Hydroponics:** 100 L water + 2 kg nutrients + 8 kWh → 6,000 kcal food/day, packaged mass approximately 2.4 kg. Requires 2 Agriculture workers per shift. Water is largely transpired and not instantly reusable; a later condensation loop may recover a defined fraction.
- **Greenhouse expansion:** Additional 100 L water + 1 kg nutrients + 2 kWh → 4,000 kcal food/day (approximately 1.6 kg packaged mass); requires 1 additional worker. Combined output: 10,000 kcal/day, enough for 4 adults at 2,500 kcal/day, before crop losses.
- For farms, power is a rate: 8 kW for a full day would equal 192 kWh. If the intended module draw is 8 kW continuous, list the daily energy budget explicitly in the UI.

## Construction and repair

The old module catalog expressed bills in generic material units. Convert those costs to **kilograms** before implementation. Initial conversion rule: each listed construction-cost number in `modules.md` equals **10 kg** of the named material. Example: Starter Habitat / Command costs 200 kg steel, 80 kg electronics, 80 kg polymers, and 60 kg machine parts. This is a provisional conversion and should be tuned against module mass and salvage throughput.

- Module **mass** is separate from its construction bill; don't assume cost equals final mass because processing losses and imported components are included.
- Construction worker effort: **4 worker-hours per 10 kg total construction inputs**, minimum 8 worker-hours. Large modules can be built in stages; each stage consumes its listed materials on completion.
- **Module condition (HP), current prototype:** every module has HP 0–100% (built at 100%) that wears down by 2% per game day. A module's production — power generated, oxygen, food, research, cooling, CO₂ scrubbing — is multiplied by its HP (50% HP = half output); its power draw, berths and storage capacity are not. Repair costs 10 kg steel + 4 kg polymers per tonne of module mass per 100% HP restored ("Repair station" in the Systems panel repairs everything at once, or an even share of it if material runs short; selecting a module in the world shows its HP and stats and repairs just that module). At 0% HP a module is offline — no production and no power draw — but it is not destroyed: it keeps its berths and storage and can be repaired. Values in `scripts/config.evox`.
- Later: repairs take crew time (Engineering), use maintenance supplies, and can be prioritised per module. The earlier rule "25% integrity costs 10% of the construction bill" is superseded by the mass-based cost.
- Recovered intact components substitute for the same component type and mass at a 1:1 ratio.
- Canceling a staged project returns 75% of unspent material; spent material is lost.

## Power and storage

- Power is measured in kW; energy in kWh. A 1 kW load operating for 1 hour uses 1 kWh.
- A module's listed kW is its instantaneous operating load. If active for 24 hours, daily consumption is `kW × 24` kWh. Idle draw is 10% of listed load unless its module entry specifies otherwise.
- Storage tanks list both capacity and working pressure. Water tanks use litres; gas tanks use kg capacity and m³ volume. A leak event should report estimated loss in L/day or kg/day.
- Refrigerated food spoilage target: **1% mass and kcal per 30 days**. Uncooled food: **5% per 30 days**. Spoilage removes both cargo mass and calories proportionally.

## Orbit and propellant

The station orbits low enough to feel atmospheric drag. Values are game-scale (the game clock is compressed; the real ISS loses roughly 2 km per month and reboosts every few weeks). Current tuning lives in `scripts/config.evox`.

- **Altitude:** starts at about **350 km** (the opening in `objectives.md` needs the station already close to the warning level; the first goal is an emergency reboost, the later goal is **420 km** with fuel production running). Warning below **330 km**; the station re-enters and is lost at **200 km**. Reboosts are capped at **450 km**.
- **Decay:** **6 km per game day at 400 km**, doubling every **40 km** lower (denser air): about 20 km/day at 330 km and runaway below 250 km. An unattended station re-enters in about 9 game days.
- **Reboost:** a thruster burn raises the orbit by **10 km per game hour** until the target altitude (**420 km**) or until the fuel runs out; the player can stop it early. Propellant use is **0.2 kg per km per tonne of station mass** (ISS-like: ~0.55 m/s per km at ~300 s specific impulse). Every module adds its mass; the starting station is 20 t, so a 20 km reboost costs 80 kg.
- **Propellant production:** the fuel producer rack (researched via *Fuel Production*) electrolyses water into propellant (see *Water, oxygen, and food*). It needs power, cooling and water, so it is built after solar arrays, a radiator, the water recycler and a workshop bench (objectives #9–#13). Rate TBD.
- **Propellant:** stored in kg. Start with **600 kg** (the opening wants less: enough for one or two emergency burns); the Central Module holds **1,000 kg**, Gas Storage adds **1,500 kg**. Salvage runs recover **30–120 kg**. Later: hydrogen from electrolysis (see *Water, oxygen, and food*) as a station-made propellant.
- **HUD:** altitude in the top bar; the resources table shows fuel (stock, burn rate, km of reboost it buys) and altitude (decay rate, time to the warning level or to reentry); the Systems panel holds the reboost control.

## Barter

- Trade uses no currency. Each community has finite stocks and current needs.
- A trade proposal lists exact mass, volume, and food calories, plus a predicted local-value balance from −100 to +100. Zero is approximately equal value; positive favors the player.
- A partner accepts at balance ≤ +10, may counteroffer from +11 to +30, and normally rejects above +30. Local scarcity and demand set value; no fixed galaxy-wide price exists.
- A community cannot trade away its last **10 days** of food, water, or oxygen reserves.
- Transfer capacity is displayed in both RU-free physical units: kg and m³ per work period. Docking Hub baseline target: **2,000 kg or 10 m³ per 4-hour period, whichever limit is reached first**; Cargo Handling doubles both limits.

## Data and research

- Data is measured in **GB** stored on station servers and recovered data hardware.
- A fully staffed Research Lab generates **10 RP/day** and processes up to **10 GB/day**. Technologies state their one-time data requirement in GB, separate from RP cost. This replaces the earlier ambiguous 1 Data RU/day rule.
- Example: a 100 RP, 20 GB technology takes 10 days at one lab and consumes 20 GB when completed, not 1 GB/day plus a completion fee.
- A research project pauses if it lacks RP throughput, staffing, power, or its required data at completion. RP progress is retained.

## Reserves and alerts

Show survival forecasts in real time using actual quantities and rates, e.g. “Water: 240 L; 3.0 days at current demand.” Suggested warnings:

- Food reserve below 3 days of crew calories.
- Potable water below 3 days of net make-up demand, or below 1 day of gross demand if recycling is offline.
- Oxygen reserve below 3 days of net make-up demand, or below 1 day of gross demand if life support fails.
- Steel, Electronics, or Machine Parts below the next planned repair/build recipe.
- Waste storage above 80% capacity.

## Consistency checklist

- Replace all generic RU quantities in `modules.md` with physical material bills, storage mass/volume, kcal, L, kg gas, kW, kWh, or GB as appropriate.
- Recalculate the Life-Support Module's people capacity from actual water and oxygen throughput. Capacity must not be stated in incompatible RU/day.
- Reconcile farm water and power: distinguish kW continuous load from kWh/day, and ensure food calories cover crew demand.
- Adjust salvage operation throughput and cargo craft capacity together so 1,000 kg is physically recoverable and storable.
- Technology effects that cite RU/day or Data RU should use physical units or RP/GB instead.

**Implemented units (litres per day).** Oxygen and CO₂ are tracked in litres with real per-person rates, so rack outputs and the HUD are in L/day like food (kcal/day) and water (L/day): a crew member breathes **590 L of oxygen a day** (the 0.84 kg above) and exhales **510 L of CO₂** (about 1 kg). The Central Module's tanks hold 4,000 L of oxygen (about 3.4 days for two crew). An O₂ generator rack makes 2,360 L a day (4 crew), a CO₂ scrubber rack removes 1,150 L a day, and the cabin air is 150 m³ (so one person adds about 3,400 ppm of CO₂ a day when nothing scrubs it). `scripts/config.evox` stores the rates per game minute (`O2_PER_CREW` = 0.41, `CO2_PER_CREW` = 0.354); the HUD multiplies by 1,440.
