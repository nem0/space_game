# Station Modules — Numerical Balance Draft

**Status:** First-pass prototype values, not final balance. These numbers are intended to make every module testable; tune them through playtests. All values use a 1-minute simulation tick, power in kW, storage/production in resource units (RU), mass in tonnes, and crew as assigned workers per 8-hour shift. Module size is a standardized footprint in meters. Construction costs are **steel / electronics / polymers / machine parts**; omitted resources cost 0. RU are abstract inventory units, not kilograms.

## Shared rules

- Modules connect through ports. A disconnected module does not receive power, atmosphere, cargo, or data. Module footprints use a 4 m station-building grid; listed dimensions are width × length × height.
- Power production and consumption are continuous rates. A module shuts down if its supply is insufficient; batteries cover deficits until depleted.
- Staffing is the recommended number of workers per shift. Modules may run understaffed at reduced effectiveness; unstaffed modules are idle unless marked automated.
- Construction takes **4 crew-hours per RU of construction cost** (sum all listed material units), minimum 1 hour. Costly projects can be built in stages.
- Basic crew consumption: **1 food RU, 1 water RU, and 0.8 oxygen RU per person per day**. Water recycling recovers 80% of water used; oxygen systems recover 70% of exhaled oxygen. These rates are station-wide baseline assumptions.
- Costs and outputs below are per module. Project modules are defined as multi-module project chains rather than one building that instantly grants an ending.

## Hull modules and internal racks

**Decision:** most pressurised modules are no longer separate kinds. The player builds an empty **hull** and fits **racks** inside it; the racks decide what the module does. Only modules whose *shape* is their function stay special. This replaces the Habitat, Hydroponics, Research Lab, Medical Bay, Storage, Refrigerator, Battery Bank and Greenhouse modules (their old rows below are kept for reference only), and gives the Workshop its home as a rack. Values are in kg / kW / L / kcal like `scripts/config.evox`; costs are **steel / electronics / polymers / parts**. The racks are tuned so a typical fit-out reproduces today's module numbers.

### Hulls

| Hull | Rings | Rack slots | Hull attachment slots | Cost (kg) | Mass | Volume | Power | Unlock |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Small hull** | 2 | 4 | 4 | 40 / 10 / 20 / 15 | 2.5 t | 30 m³ | 0.2 kW | start |
| **Standard hull** | 3 | 6 | 6 | 60 / 15 / 30 / 20 | 3.5 t | 50 m³ | 0.3 kW | Standard Hulls (50 RP) |
| **Large hull** | 5 | 10 | 10 | 100 / 25 / 50 / 35 | 6 t | 90 m³ | 0.5 kW | Large Structures (100 RP, needs Standard Hulls) |

A hull alone provides pressurised volume (dilutes CO₂), docking ports at both ends, hull attachment slots and nothing else. Its power is lighting and fans.

**Stay special modules:** Central Module (command hub, built-in life support), X Junction, Solar Wing, Radiator Wing, Gas Storage, Docking Hub (berths one shuttle for missions; later also an Airlock). These have no rack slots, except the Central Module (6). The Greenhouse is a Large hull full of greenhouse beds.

### Racks

Racks fill rack slots, one each. Like attachments they have HP (production scales with it, 0% = offline), add their mass to the station, are repaired with their module, and can be dismantled for 50% of their materials. A rack's power is drawn only while it is online.

| Rack | Effect | Power | Cost (kg) | Mass | Unlock |
|---|---|---:|---:|---:|---|
| **Berth** | +2 crew berths | 0.3 kW | 40 / 5 / 25 / 5 | 0.5 t | start |
| **O₂ generator** | +2,360 L O₂/day (4 crew) (later: uses water) | 2 kW | 20 / 10 / 10 / 10 | 0.5 t | start |
| **CO₂ scrubber** | removes 1,150 L CO₂/day (2.3 crew) | 1 kW | 15 / 10 / 10 / 5 | 0.3 t | start |
| **Hydroponics rack** | +5,000 kcal/day, +590 L O₂/day, removes 500 L CO₂/day | 1 kW | 25 / 10 / 40 / 15 | 0.6 t | Hydroponics (40 RP) |
| **Greenhouse bed** | +7,500 kcal/day, +1,060 L O₂/day, removes 890 L CO₂/day (more efficient than a hydroponics rack) | 1.2 kW | 30 / 10 / 50 / 15 | 0.8 t | Greenhouse (140 RP), Large hull only |
| **Water recycler** | Recovers 80% of used water (0% without one) | 1.5 kW | 20 / 15 / 20 / 10 | 0.4 t | Water Recycling (50 RP) |
| **Fuel producer** | Electrolysis: water → propellant; rate and power TBD. Needs power, cooling and water, and shows which is missing | TBD | TBD | TBD | Fuel Production (100 RP) |
| **Exercise machine** | Crew regain fitness here | 0.3 kW | 30 / 10 / 10 / 15 | 0.4 t | Exercise Machine (60 RP) |
| **Storage rack** | +40,000 kcal food storage, +800 kg cargo hold | 0.1 kW | 10 / 2 / 5 / 5 | 0.3 t | 20 RP |
| **Refrigerated rack** | +100,000 kcal food storage | 0.7 kW | 15 / 10 / 10 / 10 | 0.4 t | 60 RP |
| **Battery rack** | +10 kWh battery | — | 15 / 25 / 5 / 10 | 0.3 t | Energy Storage (40 RP) |
| **Research bench** | +3 RP/h | 4 kW | 30 / 45 / 15 / 20 | 0.4 t | start |
| **Workshop bench** | runs one Workshop job (see `resources.md` → *Workshop*): sorting 600 kg/day or one fabrication recipe | 6 kW working, 0.5 idle | 25 / 15 / 10 / 20 | 0.6 t | Workshop (40 RP) |
| **Medical rack** | treats minor injuries (see `crew.md`), +1 berth (patient bed) | 2.5 kW | 30 / 40 / 30 / 15 | 0.5 t | First Aid (90 RP) |
| **Robot bay** | docks 2 robots of any researched kind (Service, Builder, Long-range), which charge and are repaired here; a crew member builds a robot at a free dock (costs per kind in `crew.md` → *Robots*) | 0.5 kW docked + 0.1 kW per robot idle, 1.5 kW per robot working | 35 / 40 / 15 / 25 | 0.5 t | Robotics (180 RP) |

Later, with the crew system: benches (research, workshop, medical) need an assigned worker (a workshop bench can be staffed by a Service robot once Robotics is researched); berths, storage, generators and scrubbers are automatic.

### What the old modules become

| Old module | Equivalent fit-out | Same as before? |
|---|---|---|
| Habitat | Standard hull + 2 berths + O₂ generator + CO₂ scrubber (2 free) | 4 crew, 20 L/min O₂, 10 L/min scrubbing, ~4 kW; cost and mass within 10% |
| Hydroponics | Standard hull + 3 hydroponics racks (3 free) | 15,000 kcal/day, 15 L/min O₂, 12 L/min scrubbing |
| Greenhouse | Large hull + 10 greenhouse beds | 75,000 kcal/day, 90 L/min O₂, 70 L/min scrubbing; a hydroponics rack in any hull is the small version |
| Research Lab | Standard hull + 2 research benches + 1 berth | 6 RP/h, 2 crew |
| Storage / Refrigerator | Small hull + 4 storage racks / 3 refrigerated racks | ≥ old capacity |
| Battery Bank | Small hull + 3 battery racks | 30 kWh (the module is dropped; batteries are racks in any hull) |
| Workshop | any hull + workshop bench(es) | one bench = the designed Workshop; benches in parallel replace the dedicated Sorting Bay / Fabricator early on |

**No presets.** The player builds an empty hull and fits every rack by hand; the build tray has a STRUCTURE tab (hulls, junction, gas storage), a POWER tab (wings), a RACKS tab and an ATTACHMENTS tab - nothing named "Habitat".

### Central Module

**Produces nothing**: a module only radiates heat (19 kW cooling), holds tanks (600 L O₂, 1,000 kg propellant) and gives 150 m³ of air; life support, power and the rest come from racks, attachments and extensions and gains **6 rack slots**, pre-fitted with: 1 berth (2 crew), 2 storage racks (80,000 kcal, 1,600 kg hold), 1 O₂ generator and 1 CO₂ scrubber (the starting life support, both at 50% HP). 1 slot is free; the player must research and fit a workshop bench and a research bench (see `objectives.md`). Until a workshop bench exists the crew sort salvage by hand (240 kg/day, see `resources.md`). The Central Module starts at **50% HP** (see `objectives.md` → *The starting state*). Its own crew, food storage and cargo hold values move into those racks.

### Fitting and refitting

- **Fitting:** a RACKS tab in the build tray; arm a rack, click a module with a free rack slot. Selecting a module lists its racks (with HP) and free slots; each rack can be repaired or dismantled there.
- **Constraints:** a rack cannot be dismantled if that would leave more crew than berths, or more stored food / cargo than the remaining capacity (the panel says why).
- **Reading the station from outside:** a hull dresses itself after its fittings: portholes for berths, windows and green plates for hydroponics and greenhouse beds, grilles for scrubbers and batteries, plain plates for storage, blue for research. It re-dresses when its racks change. The selection panel and a hover tooltip name the dominant use ("Hull - Habitat").
- **Inside vs. outside:** racks are inside (pressurised work); hull attachments (`Attachments` below) are outside for things that need space: solar, vents, tanks, antennas, dishes.

**Unlocks for the infrastructure below.** Solar Wing: *Solar Arrays* (70 RP). Radiator Wing: *Thermal Management* (25 RP). Docking Hub: *Docking Operations* (60 RP). Shuttle: *Shuttle* (100 RP). Their costs include machine parts, so they need a workshop bench first. See `tech_tree.md` → *Opening technologies*.

## Core and crew survival

*Superseded where it conflicts with "Hull modules and internal racks" above: Habitat and Medical Bay are hull fit-outs now.*

| Module | Size (m) | Cost: steel / electronics / polymers / parts | Power | Staff | Exact effect |
|---|---:|---:|---:|---:|---|
| **Starter Habitat / Command** | 8×8×4 | 20 / 8 / 8 / 6 | 2 kW | 1 | Pressurized capacity for 4 crew; 20 RU general storage; provides station command and basic life-support controls. Starting module. |
| **Habitat** | 8×8×4 | 18 / 4 / 10 / 5 | 1 kW | 0 | Adds 6 crew capacity and 12 personal-storage RU. Each occupant needs an assigned berth. |
| **Life-Support Module** | 8×8×4 | 16 / 10 / 8 / 8 | 8 kW | 1 | Supports up to 20 crew; processes 20 water RU/day with 80% recovery and 16 oxygen RU/day with 70% recovery. Provides atmosphere monitoring and filtration. |
| **Galley and Hygiene** | 8×4×4 | 10 / 3 / 8 / 4 | 3 kW | 1 | Serves up to 12 crew. Reduces each served crew member's daily water use by 0.2 RU and prevents the hygiene condition penalty. Does not create food. |
| **Medical Bay** | 8×4×4 | 8 / 8 / 6 / 5 | 2 kW | 1 | Treats 2 patients per day; halves recovery time for treated injuries/illness. Can isolate 2 patients. |
| **Radiation Shelter** | 4×4×4 | 10 / 2 / 8 / 4 | 1 kW | 0 | Protects up to 8 crew. Reduces radiation dose received inside by 90% during an event. Crew must be assigned there before the event. |
| **Emergency Shelter / Safe Room** | 4×4×4 | 12 / 3 / 8 / 6 | 1 kW | 0 | Protects up to 6 crew during raids or local pressure incidents; reduces injury chance by 50% for sheltered crew. Does not protect against station-wide life-support failure. |

## Power and station infrastructure

| Module | Size (m) | Cost: steel / electronics / polymers / parts | Power | Staff | Exact effect |
|---|---:|---:|---:|---:|---|
| **Solar Array** | 4×12×1 | 8 / 4 / 2 / 3 | Produces 0–20 kW | 0 | Generates 20 kW in direct sunlight, 0 kW in planetary shadow; output scales linearly with damage/orientation, down to 0%. |
| **Battery Bank** | 4×4×4 | 4 / 8 / 2 / 3 | Up to 5 kW charge/discharge | 0 | Stores 100 kWh. Charge/discharge efficiency 90%; cannot supply modules beyond its 5 kW output. |
| **Reactor Module** *(research unlock)* | 8×8×4 | 18 / 12 / 6 / 10 | Produces 40 kW; uses 2 kW | 1 | Net output 38 kW while fueled; consumes 1 reactor-fuel RU per 10 days; requires 1 maintenance RU every 30 days. |
| **Thermal Control / Radiator** | 4×8×1 | 8 / 3 / 4 / 3 | 1 kW | 0 | Rejects up to 25 kW of waste heat. Excess heat above capacity raises connected module failure risk by 2 percentage points per 10 kW excess per day. |
| **Docking Hub and Airlock** | 8×8×4 | 14 / 8 / 8 / 7 | 3 kW | 1 | Supports 2 docked craft; processes 1 cargo transfer of up to 20 RU per 4-hour work period. Enables trade rendezvous and crew transfer. |
| **Reinforced Docking Collar** | 4×4×4 | 16 / 4 / 10 / 8 | 1 kW | 0 | Adds 50 percentage points to the time needed for hostile boarding; reduces successful forced-entry chance by 30 percentage points. |
| **Storage Module — Bulk** | 4×4×4 | 6 / 1 / 2 / 2 | 0.5 kW | 0 | Stores 100 RU of dry cargo. |
| **Storage Module — Refrigerated** | 4×4×4 | 6 / 3 / 4 / 3 | 2 kW | 0 | Stores 50 RU of food/medical cargo; spoilage reduced from 5% to 1% per 30 days. |
| **Storage Module — Pressurized** | 4×4×4 | 8 / 3 / 6 / 4 | 1 kW | 0 | Stores 50 RU of gases or other pressurized cargo. |
| **Storage Module — Secure** | 4×4×4 | 10 / 4 / 6 / 5 | 1 kW | 0 | Stores 30 RU of selected cargo. During a successful raid, cargo loss is reduced by 75%; capacity is lower due to compartmentalization. |

## Attachments

Small functional add-ons bolted onto a module's outer hull, like the small solar panels and vents on the Central Module. They are the cheap, fine-grained way to tune a station: a few kilowatts, a little cooling, one more tank, without spending a docking port on a whole module.

**Rules**
- **Slots.** Every module has a fixed number of hull **attachment slots**, separate from its docking ports and panel mounts: Central Module 8 (every other roof facet), tube modules 2 per hull ring (on the two diagonals, free on every hull variant; a 3-ring Habitat has 6, the 2-ring Battery Bank 4, the 5-ring Greenhouse 10), X Junction 0 (its side ports and mounting pads fill the hull), wings and Gas Storage 0. Each slot holds one attachment (`defs.slot`).
- **Placing.** An ATTACHMENTS category in the build tray; arm one, aim at a free slot on any module (free slots are shown while armed), click. R turns it in 90° steps where that matters (solar panels, dish).
- **Starting state.** New modules come with bare slots; their random decorative parts are dropped. The Central Module starts with 6 small solar panels and 2 heat vents on its roof; its bare hull now lists 5 kW and 19 kW cooling, so the total stays 17 kW / 25 kW. On the Central roof a solar panel or vent is a whole roof facet (`cen_roof_solar` / `cen_roof_vent`); elsewhere it is the small part model.
- **Power, mass, HP.** Attachments draw from and feed the station network, add their mass to the station (reboost fuel), and have their own HP that wears at the module rate; output scales with HP exactly like modules. Selecting a module lists its attachments with their HP; "Repair module" repairs the module and its attachments together.
- **Removing.** An attachment can be dismantled from the module panel, returning 50% of its materials. Attachments are lost with their host if the host is ever removed.
- **Functional only.** Every buildable attachment does something. Decoration (handrails and similar dressing) is not built: `modgen.evox` scatters it at random on the hull, never on attachment slots.
- **Limits.** Attachments never provide berths, pressurised volume or docking ports — those stay the job of modules.

**Catalogue** (costs in kg: steel / electronics / polymers / parts)

| Attachment | Kit model | Cost (kg) | Mass | Effect | Unlock |
|---|---|---:|---:|---|---|
| **Small solar panel** | `part_solar` | 10 / 15 / 5 / 5 | 0.1 t | +2 kW in sunlight, 0 in Earth's shadow | start |
| **Heat vent** | `part_vent` | 15 / 2 / 5 / 5 | 0.1 t | +3 kW cooling | start |
| **Storage crate** | `part_crate` | 20 / 0 / 10 / 2 | 0.2 t | +400 kg cargo hold (mixed salvage) | start |
| **Fuel tank** | `part_gastank` | 25 / 2 / 5 / 5 | 0.3 t | +250 kg propellant capacity | start |
| **Oxygen tank** | `part_gastank_white` | 25 / 2 / 5 / 5 | 0.3 t | +300 L oxygen capacity | start |
| **CO₂ scrubber pack** | `part_elec` | 10 / 20 / 10 / 10 | 0.2 t | Removes 390 L CO₂/day; draws 0.5 kW | 20 RP |
| **Work light** | `part_light` | 5 / 5 / 2 / 2 | 0.05 t | +10% sorting rate while the host module sorts (Central Module / Workshop); draws 0.3 kW | 20 RP |
| **Antenna** | `part_antenna` | 10 / 15 / 2 / 5 | 0.1 t | Distress calls are detected 20% sooner (interval −20%), at most one counts | 40 RP |
| **Comms dish** | `part_dish` | 20 / 25 / 5 / 10 | 0.3 t | Missions bring back +10% mixed salvage, at most two count | 60 RP |
| **Radar** | `part_radar` | 20 / 40 / 10 / 15 | 0.3 t | Finds mission contacts (derelicts, pods, asteroids); draws 1 kW. Without a working radar only nearby scrap is available | Radar (60 RP) |

**Balance intent.** Per kilowatt, a small solar panel costs about the same as a Solar Wing but needs no X junction and no panel mount; the wing wins on mass and slot use. Stacking caps (antenna, dish) stop attachment spam from replacing the dedicated modules (Sensor Mast, Salvage Control).

## Survey, salvage, and logistics

| Module | Size (m) | Cost: steel / electronics / polymers / parts | Power | Staff | Exact effect |
|---|---:|---:|---:|---:|---|
| **Sensor / Communications Mast** | 4×4×8 | 4 / 10 / 2 / 3 | 3 kW | 0 | Increases discovery scan radius by 50%; reveals salvage yield estimates with ±20% error instead of ±50%; communications range 10,000 km. |
| **Salvage Control Module** | 8×4×4 | 8 / 8 / 4 / 5 | 2 kW | 1 | Manages 2 active salvage operations; adds 10 percentage points to recovery yield and reduces mission incident chance by 10 percentage points. |
| **Cargo Handling / Transfer** *(candidate)* | 8×4×4 | 10 / 3 / 6 / 5 | 2 kW | 1 | Raises docking cargo throughput from 20 to 40 RU per 4-hour work period. Requires a Docking Hub. |
| **Secure Cargo / Decoy Locker** *(candidate)* | 4×4×4 | 6 / 2 / 4 / 3 | 0.5 kW | 0 | Stores 20 RU. When selected as decoy cargo, reduces chance pirates target protected cargo by 25 percentage points; decoy contents may be lost. |
| **Communications Array** *(candidate)* | 4×4×4 | 6 / 10 / 2 / 4 | 4 kW | 1 | Extends communications range to 100,000 km; improves contact identification and trade offer estimates by 25%. |

## Processing and manufacturing

*Early processing happens on Workshop benches (racks); the dedicated modules below are the later, faster upgrade.*

| Module | Size (m) | Cost: steel / electronics / polymers / parts | Power | Staff | Exact effect |
|---|---:|---:|---:|---:|---|
| **Workshop** | 8×4×4 | 12 / 6 / 6 / 6 | 6 kW while working | 1–2 | Early, general-purpose production room: runs **one job at a time** from a player-set queue. Jobs: *sort mixed salvage* (600 kg/day), *machine parts*, *maintenance kits*, *electronics recovery* and *damaged electronics repair* (the Fabrication recipes in `resources.md`, at 50% of their batch rate). Idle when the queue is empty (0.5 kW). One Workshop per station; dedicated modules below replace it as the station grows (see *Workshop* in `resources.md`). No research needed. |
| **Sorting Bay** | 8×8×4 | 14 / 4 / 6 / 6 | 5 kW | 2 | Sorts 10 RU mixed salvage per day into categorized materials; 80% material recovery, with 20% waste. Electronics skill raises recovery by up to 10 percentage points. |
| **Smelter / Materials Processor** | 8×8×4 | 18 / 6 / 8 / 8 | 12 kW | 2 | Processes 8 RU metal scrap/day into 6 RU steel stock (75% yield); produces 2 RU slag and 4 kW waste heat per operating hour. |
| **Fabricator** | 8×4×4 | 10 / 8 / 6 / 6 | 6 kW | 1 | Produces 4 machine-part RU/day from 4 steel + 2 electronics + 1 polymer RU. Recipe inputs and output are consumed/created as listed. |
| **Electronics Bench** | 4×4×4 | 4 / 8 / 4 / 4 | 4 kW | 1 | Repairs 2 RU damaged electronics/day, returning 1.5 RU usable electronics (75% recovery); alternatively fabricates 1 RU electronics/day from 2 electronics scrap + 1 copper/conductor RU. |
| **Robotics Bay** *(research unlock: Autonomous Maintenance)* | 8×8×4 | 12 / 12 / 6 / 8 | 8 kW | 2 | The late upgrade of the Robot bay rack: docks 6 robots and, with a worker attending, produces 1 robot of a chosen kind every 5 days from 5 steel + 4 electronics + 3 machine parts RU instead of a crew build job. Its robots are assigned to tasks like any other (`crew.md` → *Robots*). |

## Food and research

*Hydroponics, the Research Lab and the Greenhouse are hull fit-outs now (see "Hull modules and internal racks").*

| Module | Size (m) | Cost: steel / electronics / polymers / parts | Power | Staff | Exact effect |
|---|---:|---:|---:|---:|---|
| **Hydroponics Farm** | 8×8×4 | 8 / 4 / 12 / 5 | 8 kW | 2 | Produces 6 food RU/day; consumes 2 water RU/day and 1 nutrient RU/day. Crop output falls 50% if understaffed by one worker and stops if unstaffed. |
| **Seed / Food Bank** | 4×4×4 | 4 / 1 / 8 / 2 | 0.5 kW | 0 | Stores 40 RU seeds or food. Seeds preserve 100% viability for 1 year; food spoilage is 1% per 30 days. |
| **Greenhouse Expansion** | 8×8×4 | 10 / 4 / 14 / 6 | 10 kW | 3 | Produces 10 food RU/day; consumes 4 water RU/day and 2 nutrient RU/day. Requires a Hydroponics Farm and adds 2 comfort points to up to 8 crew assigned personal time there. |
| **Research Lab** | 8×4×4 | 8 / 10 / 4 / 5 | 5 kW | 2 | Produces 10 research points/day when fully staffed; consumes 1 data RU/day. Each technology has a stated research-point cost. |
| **Observatory / Survey Module** | 4×4×4 | 4 / 10 / 2 / 3 | 3 kW | 1 | Adds 25% to discovery scan radius and reveals survivors/opportunities 1 day sooner. Does not stack with another Observatory; use the best connected module. |

## Construction, defense, and major projects

| Module / project | Size | Cost | Power | Staff | Exact effect |
|---|---:|---:|---:|---:|---|
| **Construction Bay** | 8×8×4 | 20 / 8 / 8 / 10 | 8 kW | 2 | Enables projects marked “Construction Bay required”; reduces their construction time by 25%. |
| **Point-Defense / Nonlethal Deterrent** *(candidate)* | 4×4×4 | 12 / 10 / 4 / 6 | 6 kW | 1 | Reduces probability of a pirate attack succeeding by 20 percentage points during a defended encounter. Uses 1 maintenance RU per 30 days; may increase hostility after use. |
| **Escort Craft Berth** *(candidate)* | 8×8×4 | 16 / 8 / 8 / 8 | 3 kW | 1 | Supports 1 escort craft. An assigned escort reduces cargo-loss chance on one trade/salvage route by 30 percentage points; craft acquisition and upkeep are separate. |
| **Population Infrastructure Project** | Multi-module | TBD | TBD | TBD | Requires at least 4 Habitat modules, 2 Life-Support modules, 1 Hydroponics Farm, and 40 rescued/resident crew capacity. Completion enables the orbital-civilization ending path. |
| **Interplanetary Mission Project** | Multi-module | TBD | TBD | TBD | Requires Construction Bay, 2 reactor-class power sources, 1 mission habitat, and 100 RU mission supplies. Completion launches a mission toward another habitable world and enables that ending path. |
| **Earth Restoration Project** | Multi-module | TBD | TBD | TBD | Requires Research Lab, Observatory, 2 Life-Support modules, and 100 RU specialized research data. Completion enables the Earth-restoration ending path. Exact chain and feasibility remain narrative/balance decisions. |

## Numerical design notes / unresolved balance

- All numbers above are provisional and should be adjusted after the first playable station loop. In particular, validate that a 2–4 person starting crew can survive, staff critical work, and expand without requiring perfect play.
- Costs use abstract RU to keep this module list readable. Define exact resource recipe tables before implementation; map “steel,” “electronics,” “polymers,” “machine parts,” “data,” “nutrients,” and “reactor fuel” to the resource inventory in the economy spec.
- **Workshop vs. dedicated modules:** the Workshop is the jack-of-all-trades that gets production started; the Sorting Bay (1,000 kg/day), Fabricator and Electronics Bench each do one job faster, in parallel, and benefit from their technologies. A Workshop stays useful afterwards for jobs no dedicated module covers.
- Effects that depend on risk probabilities should use a bounded probability model (0–100%) and be previewed to the player. Do not allow stacked bonuses to exceed 100% or drop below 0%.
- Major project requirements are placeholders; the three goals are supported, but should require distinct chains and meaningful choices rather than simply meeting a crew-count threshold.

**Rule: modules do not produce.** A hull, junction or the Central Module only provides volume, ports, slots, tank capacity and heat radiation (cooling). Anything that makes power, air, food, research or fuel is a rack, an attachment or an extension (wings). The Central roof starts with 5 small solar panels, 2 heat vents and a **radioisotope generator** attachment (+5 kW day and night, unlocked later by Power Buses), which replaces the 5 kW the Central Module used to produce on its own.
