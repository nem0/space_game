# Technology Tree — Numerical Draft

**Status:** First-pass progression proposal. Research is optional in sequencing but important for advanced modules and all major ending projects. It should not become a grind or block basic survival. Values are provisional and intended to pair with [`modules.md`](modules.md), [`resources.md`](resources.md), and [`crew.md`](crew.md).

## Research rules

- A Research Lab staffed with 2 Science workers produces **10 Research Points (RP)/day** and consumes **1 Data RU/day** while actively researching, matching the current module draft.
- RP are assigned to one selected technology at a time per lab. Multiple labs can work on different technologies; their RP outputs add together.
- Research pauses if the lab lacks staffing, power, or Data. Existing RP progress is retained.
- Completing a technology consumes its listed Data RU once; ongoing lab operation consumes the daily Data specified above. **Implementation decision:** to avoid charging twice, use the daily 1 Data RU as the research input and remove any separate completion charge unless a technology explicitly lists a one-time data requirement.
- Research points are abstract work; they are not an inventory resource. Research uses crew work hours and station power through the lab.
- Each technology lists prerequisites. Prerequisites gate only advanced capabilities, not the minimum systems needed to survive the opening.
- Salvaged prototypes and survey discoveries can unlock a technology's research option; they do not automatically grant the completed technology unless explicitly stated.
- Base research time at one fully staffed lab is `RP cost ÷ 10` days. Example: 100 RP takes 10 days. Unstaffed time does not advance research.

## Opening technologies

The opening chain in [`objectives.md`](objectives.md) needs these technologies, so basic food, water recycling, batteries and workshop work are **researched, not given**. This replaces the older rule that no technology gates food or water recycling. The game is a hardcore survival game: the starting station survives the first days on its stock, and the player must research its way out. What stays free is only what the opening needs to be *survivable*: the research bench, scrubbers, O₂ generators, small panels and the first EVA haul.

Costs are provisional and tuned against the first objective rewards (30 / 60 / 100 RP) and a research bench rack (+3 RP/h).

| Technology | Cost | Prerequisites | Unlock / effect | Objective |
|---|---:|---|---|---|
| **Energy Storage** | 40 RP | none | Battery rack | #5 Survive the night |
| **Hydroponics** | 40 RP | none | Hydroponics rack | #6 Feed the crew |
| **Water Recycling** | 50 RP | none | Water recycler rack: recovery 0% → 80% | #7 Stop the water loss |
| **Workshop** | 40 RP | none | Workshop bench rack (sorting, machine parts, repair kits) | #12 |
| **Fuel Production** | 100 RP | Water Recycling | Fuel producer rack (electrolysis: water → propellant) | #9 |
| **Solar Arrays** | 70 RP | Energy Storage | Solar Wing module (needs machine parts) | #10 |
| **Thermal Management** | 25 RP | none | Radiator Wing module | #11 |
| **First Aid** | 90 RP | none | Medical rack (treats minor injuries) | #15 |
| **Medical Bay** | 150 RP | First Aid | Medical Bay: a working medical rack nurses seriously injured crew, with another crew member as caregiver | #17 |
| **Exercise Machine** | 60 RP | none | Exercise machine rack | #19 |
| **Greenhouse** | 140 RP | Hydroponics | Greenhouse bed (Large hull only) | #21 |
| **Radar** | 60 RP | none | Radar attachment (finds mission contacts) | #23 |
| **Standard Hulls** | 50 RP | none | Standard hull (6 rack slots); the Small hull is the only one available at the start | Orbit lane |
| **X Junctions** | 50 RP | Standard Hulls | X junction: four docking ports and the panel mounts that wings and gas storage need | Orbit lane |
| **Docking Operations** | 60 RP | none | Docking hub | #25 |
| **Shuttle** | 100 RP | Docking Operations | Shuttle (missions) | #27 |

These sit alongside the six branches below. Where a branch technology overlaps (for example **Efficient Water Recovery**, 80% → 88%), the opening technology is the prerequisite.

## Tree overview

Six connected branches provide survival upgrades, industrial capacity, automation, exploration, and three long-term futures. Players can research in different orders, but major projects require capabilities from multiple branches.

### A. Life Support & Medicine

| Technology | Cost | Prerequisites | Unlock / exact effect |
|---|---:|---|---|
| **Atmosphere Diagnostics** | 40 RP | Starter technology | Shows atmosphere reserve forecast and leak source estimates with ±20% error. |
| **Efficient Water Recovery** | 80 RP | Atmosphere Diagnostics | Life-Support water recovery increases from 80% to 88%. |
| **Oxygen Scrubbing** | 100 RP | Atmosphere Diagnostics | Oxygen recovery increases from 70% to 80%. |
| **Crop Nutrient Cycling** | 100 RP | Efficient Water Recovery | Hydroponics nutrient use falls from 1 to 0.75 RU/day per farm; food output unchanged. |
| **Advanced Medical Protocols** | 120 RP | Atmosphere Diagnostics | Medical Bay treats 3 patients/day instead of 2; treatment still halves recovery time. |
| **Radiation Dosimetry** | 100 RP | Atmosphere Diagnostics | Sensor forecasts radiation events 24 hours earlier; shelter dose reduction improves from 90% to 93%. |
| **Closed-Loop Habitat** | 220 RP | Efficient Water Recovery + Oxygen Scrubbing | Life-Support water recovery becomes 92% and oxygen recovery 85%; unlocks high-capacity Life-Support Module variant. |

### B. Materials & Fabrication

| Technology | Cost | Prerequisites | Unlock / exact effect |
|---|---:|---|---|
| **Salvage Classification** | 50 RP | Starter technology | Reduces sorting manifest estimate error by 10 percentage points (minimum error 10%). |
| **Workshop** | 40 RP | Starter technology | Researched in the opening (see *Opening technologies*): the general-purpose sorting and fabrication room. The technologies below improve the dedicated modules, not the Workshop. |
| **Precision Sorting** | 100 RP | Salvage Classification | Sorting Bay useful-material recovery increases by 5 percentage points, from 90% to 95%. |
| **Alloy Processing** | 140 RP | Precision Sorting | Unlocks advanced alloy recipe: 3 Steel Stock + 1 Aluminum Stock → 3 Alloy Stock. Alloy Stock replaces steel 1:1 in eligible module recipes and reduces those modules' mass by 15%. |
| **Component Reclamation** | 120 RP | Salvage Classification | Intact components appear in salvage manifests 20% more often (relative increase); no effect on the total quantity of salvage. |
| **Modular Fabrication** | 160 RP | Precision Sorting | Fabricator output rises from 4 to 5 Machine Parts per batch; recipe inputs unchanged. |
| **Electronics Refurbishment** | 180 RP | Component Reclamation | Electronics Bench repair yield rises from 75% to 90%. |
| **Advanced Materials** | 250 RP | Alloy Processing + Modular Fabrication | Unlocks high-strength structural recipe; eligible construction recipes use 20% fewer Steel Stock, rounded up per resource line. |

### C. Power & Thermal

| Technology | Cost | Prerequisites | Unlock / exact effect |
|---|---:|---|---|
| **Solar Tracking** | 60 RP | Starter technology | Solar Arrays produce 10% more power in direct sunlight (22 kW instead of 20 kW). |
| **Battery Management** | 80 RP | Solar Tracking | Battery charge/discharge efficiency increases from 90% to 95%. |
| **Radiator Engineering** | 100 RP | Starter technology | Radiators reject 30 kW instead of 25 kW; power draw remains 1 kW. |
| **High-Efficiency Cells** | 160 RP | Solar Tracking | Solar Array direct-sun output increases to 26 kW. Replaces, not stacks with, Solar Tracking's 22 kW value. |
| **Compact Reactor Design** | 240 RP | Battery Management + Radiator Engineering | Unlocks Reactor Module; lowers reactor fuel use from 1 to 0.8 RU per 10 days. |
| **Thermal Recycling** | 180 RP | Radiator Engineering | Production modules generate 15% less waste heat; electrical power consumption unchanged. |
| **Fusion Power Systems** | 400 RP | Compact Reactor Design + Thermal Recycling | Unlocks an advanced reactor variant: 60 kW gross output, 2 kW self-use (58 kW net), 1 fuel RU per 15 days. Requires 2 Radiators. |

### D. Automation & Logistics

| Technology | Cost | Prerequisites | Unlock / exact effect |
|---|---:|---|---|
| **Production Forecasting** | 50 RP | Starter technology | Production panel forecasts stock depletion and recipe completion 30 days ahead. |
| **Priority Routing** | 100 RP | Production Forecasting | Unlocks minimum stock reserves and automated queue pausing; no direct production bonus. |
| **Cargo Handling Systems** | 120 RP | Production Forecasting | Unlocks Cargo Handling / Transfer module; docking transfer capacity doubles from 20 to 40 RU per 4-hour work period. |
| **Robotics** | 180 RP | Workshop | Unlocks the **Robot bay** rack and the **Service robot**: works inside the hulls (racks, interior repairs, workshop benches) at ×0.8 (`crew.md` → *Robots*). Not available at the start; the opening is survived by the crew alone. |
| **Orbital Robotics** | 160 RP | Robotics + Docking Operations | Unlocks the **Builder robot**: builds and dismantles modules, fits and repairs attachments, repairs hulls, and makes short EVA runs without a shuttle. |
| **Autonomous Navigation** | 200 RP | Orbital Robotics + Shuttle | Unlocks the **Long-range robot**: flies a shuttle unmanned on debris, satellite and asteroid missions. Survivor missions still need a crew pilot. |
| **Servo Upgrades** | 140 RP | Robotics | Service and Builder robots work 0.2 faster (×1.0 and ×1.2). |
| **Hardened Electronics** | 120 RP | Robotics | Service and Builder robots keep working through radiation events and solar storms (otherwise disabled for 6 h outside a shelter). |
| **Autonomous Maintenance** | 220 RP | Robotics | Robots wear half as fast (1% condition per 8 h of work); robots reduce maintenance supply consumption by 25% for up to 4 connected production modules; unlocks the **Robotics Bay** module (holds 6 robots and builds them on its own). |
| **Automated Salvage Planning** | 200 RP | Cargo Handling Systems + Robotics | Salvage Control manages 3 active operations instead of 2; does not reduce mission risk further. |
| **Station-Wide Logistics** | 300 RP | Autonomous Maintenance + Automated Salvage Planning | One operator can supervise up to 4 connected production modules without reducing output; does not eliminate module minimum staffing for hazardous work. |

### E. Orbital Operations

| Technology | Cost | Prerequisites | Unlock / exact effect |
|---|---:|---|---|
| **Orbital Survey Methods** | 50 RP | Starter technology | Reveals one additional nearby discovery opportunity per survey cycle. |
| **Signal Analysis** | 80 RP | Orbital Survey Methods | Improves contact identity and survivor-count estimate from ±1 person to exact count for signals within sensor range. |
| **Debris Trajectory Prediction** | 100 RP | Orbital Survey Methods | Reduces debris-impact incident chance by 25% relative to current chance; provides 12 hours warning. |
| **Long-Range Communications** | 140 RP | Signal Analysis | Unlocks Communications Array and extends trade/contact communications range to 100,000 km. |
| **Salvage Risk Models** | 150 RP | Debris Trajectory Prediction | Improves salvage operation risk estimate from ±10 percentage points to ±5; does not lower actual risk. |
| **Rescue Triage Protocols** | 180 RP | Signal Analysis + Salvage Risk Models | Rescued survivors arrive with +10 Health on average (capped at 100); rescue mission incident probability reduced by 2 percentage points. |
| **Deep-Orbit Navigation** | 280 RP | Long-Range Communications + Salvage Risk Models | Unlocks long-range trade routes and distant discovery sites; travel time reduced by 20%. |

### F. Major Projects

These are multi-technology commitments and ending routes. They do not force a single ending: players may pursue several, but each consumes substantial resources and capacity.

| Project technology | Cost | Prerequisites | Unlock / exact effect |
|---|---:|---|---|
| **Orbital Population Planning** | 250 RP | Closed-Loop Habitat + Station-Wide Logistics | Unlocks Population Infrastructure project stages; enables habitat/support modules for large-scale settlement. |
| **Interplanetary Propulsion** | 300 RP | Fusion Power Systems + Deep-Orbit Navigation | Unlocks propulsion fabrication and the first mission-vehicle stage. |
| **Long-Duration Mission Life Support** | 220 RP | Closed-Loop Habitat + Interplanetary Propulsion | Unlocks mission habitat and supply-loop stage; reduces mission water/food reserves required by 20%. |
| **Earth Systems Assessment** | 180 RP | Orbital Survey Methods + Signal Analysis | Unlocks analysis of Earth's surface and atmosphere; identifies restoration constraints. |
| **Environmental Restoration Engineering** | 350 RP | Earth Systems Assessment + Advanced Materials + Closed-Loop Habitat | Unlocks the Earth restoration infrastructure stages and specialized environmental production recipes. |
| **Humanity's Future** *(integration milestone)* | 500 RP | Any two of Orbital Population Planning, Long-Duration Mission Life Support, Environmental Restoration Engineering | Unlocks simultaneous completion planning for multiple ending projects; no direct resource or production bonus. |

Robots in the tree: *Robotics* is the gate, then each further kind has its own research: the Service robot (inside) first, the Builder robot (outside, after Docking Operations) next, and the Long-range robot (unmanned missions, after the Shuttle) last. It is a mid-game lane on purpose (180 RP, after the Workshop), so the opening stays a small-crew survival puzzle and robots arrive when the station has more jobs than hands. Robots never unlock research, medicine or survivor missions; those stay with people.

## Example progression

1. **Opening survival:** Atmosphere Diagnostics, Production Forecasting, and Orbital Survey Methods provide visibility and manageable decisions without requiring advanced machinery.
2. **Stabilization:** Efficient Water Recovery and Solar Tracking improve the two most pressing station budgets; Salvage Classification improves recovery planning.
3. **Expansion:** Cargo Handling Systems, Precision Sorting, and Radiator Engineering address logistics and production bottlenecks.
4. **Specialization:** Choose automation, better life support, advanced power, rescue capacity, or long-range operations based on the station's needs and discovered opportunities.
5. **Endgame:** Invest in one or more Major Projects; their prerequisite branches and resource chains create distinct strategic paths.

## Research UI and balance rules

- Each technology card shows RP remaining, estimated days at current lab staffing, prerequisite status, daily Data use, and all exact unlock effects.
- Use mutually clear additive or replacement bonuses. A later Solar technology explicitly replaces earlier output (26 kW), rather than ambiguously stacking percentages.
- Probability modifiers are bounded from 0% to 100% and displayed as actual before/after values.
- No technology is required to repair the starter module, fit a scrubber or O₂ generator, staff a research bench, or perform the first EVA haul. Hydroponics, water recycling, batteries and the workshop are researched (see *Opening technologies*): the opening is designed so a careful player survives long enough to research them, and a careless one restarts.
- Research choices should compete with crew labor and power, not require repetitive clicks. Queueing the next eligible technology is allowed.
- Recovered prototypes and procedural discoveries can reveal options or grant a one-time RP discount of 20%; they do not make a technology mandatory or randomly unavailable forever.

## Consistency decisions still needed

- `modules.md` lists Research Lab output as 10 RP/day and 1 Data RU/day, while earlier economy text says data is consumed when research completes. This document treats 1 Data RU/day as the ongoing input and recommends removing a separate completion charge to avoid double-charging.
- `modules.md` lists Solar Tracking-compatible baseline values; the research tree explicitly replaces output at each tier to avoid stacked bonuses.
- Confirm whether projects can be researched before all required materials are available. Recommended: yes; research unlocks project stages, while construction separately consumes materials.
- Major Project RP costs are independent from their construction costs; define exact module and resource bills for project stages after the module catalog is finalized.
