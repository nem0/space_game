# Working Title: **Still Above: Orbital Refuge**

## High Concept
A 3D, post-apocalyptic space-station building strategy game. Earth below is a ruined, uninhabitable world; the player begins with one fragile orbital module and turns it into a self-sufficient station—and, eventually, a foothold for humanity's future. Scavenge, extract, refine, manufacture, and build while keeping the station alive amid scarcity and orbital hazards.

## Player Fantasy
Be the resourceful founder of a new home: make hard choices with limited supplies, watch a tiny outpost grow into a functioning orbital settlement, and decide what humanity's next chapter should look like.

## Setting & Tone
- **Earth:** Visible beneath the station, beautiful from orbit but devastated and unsafe to return to at the outset. Its condition and the cause of the collapse are mysteries to uncover.
- **Starting situation:** One aging, minimally equipped module; a small crew; limited power, oxygen, food, and spare parts.
- **Tone:** Grounded survival and engineering, balanced with wonder and hard-won optimism. The station should feel vulnerable and lived-in, not like an abstract factory diagram.

## Core Gameplay Loop
1. **Survey:** Scan nearby wreckage, orbital debris, and points of interest; assess risk and potential yield.
2. **Plan:** Choose a salvage operation or station project based on current needs and capacity.
3. **Gather:** Assign managed salvage operations to recover materials from debris and derelicts. Direct-control missions are a possible later addition, not part of the initial design.
4. **Process:** Sort and refine raw salvage into useful materials; manage power, throughput, storage, and waste.
5. **Build:** Attach modules and infrastructure to expand production, life support, storage, research, and habitation.
6. **Sustain:** Keep critical systems supplied and crew safe as the station grows and demands more resources.
7. **Discover:** Unlock technologies, story fragments, and new opportunities that change the station's priorities.

## Design Pillars
- **Every resource has a story:** Supplies are finite and consequential; a hull plate might become a new room or a critical repair.
- **Readable, tactile 3D construction:** Build from a strategic 3D view using snap-based module placement; see the station's silhouette and activity change as it grows.
- **Interdependent systems:** Power, life support, logistics, production, and crew needs create meaningful trade-offs without busywork.
- **Expansion with purpose:** New space should solve a problem, create a capability, or open a strategic choice.
- **Hope earned through survival:** Progress should feel like rebuilding against the odds, not simply scaling numbers.

## Resources (Draft)
Keep the economy legible: a short list of bulk materials, a few specialized components, and essential consumables. Salvage is a source, not a universal build resource; it must be sorted and processed.

### Raw materials
- **Ferrous scrap:** Common structural debris; refined into steel.
- **Non-ferrous scrap:** Copper and aluminum-bearing debris; useful for wiring, radiators, and lightweight structures.
- **Polymers:** Insulation, seals, pipes, and interior fittings.
- **Silicates:** Glass, ceramics, and specialist industrial uses.
- **Water ice:** Recovered from cargo, wrecks, or later extraction; processed into water, oxygen, and hydrogen.
- **Volatile gases:** Feedstock for atmosphere and chemical production; rare and valuable.
- **Electronic scrap:** Damaged circuit boards and sensors; sorted for components rather than smelted as bulk metal.

### Refined materials and parts
- **Steel and aluminum stock:** Structural frames, pressure hull repairs, and machinery.
- **Conductors:** Power cables, motors, and electrical equipment.
- **Polymers and sealants:** Pressure seals, hoses, insulation, and life-support consumables.
- **Glass/ceramics:** Viewports, labware, and heat-resistant parts.
- **Electronics:** Control units, sensors, and automation; may require recovered rare components.
- **Machine parts:** Standard manufactured parts used by most modules.

### Consumables and capacity
- **Food:** Produced in farms or rationed from stockpiles.
- **Water:** Drinking, hygiene, and crop use; recycled with losses.
- **Oxygen / breathable atmosphere:** Generated and buffered; atmosphere is also lost through leaks and EVA use.
- **Propellant (fuel):** Burned by the station's thrusters to reboost its decaying orbit (see *Orbit maintenance*), and later by salvage craft. Recovered by salvage; later made from water electrolysis hydrogen.
- **Power:** A production/consumption rate and stored capacity, rather than a boxed inventory good.
- **Data:** Research and recovered records unlock technologies and story clues; not a physical construction material.

**Economy rule of thumb:** Salvage operations return uncertain mixes of raw materials, components, and hazards. Processing takes time, power, labor, and storage. Shortages should create choices and repair priorities, not routine dead ends.

### Production-chain detail
Production is a station-planning puzzle: players choose what to process, where scarce inputs go, and which bottlenecks to fix. Avoid requiring the player to click every batch or manage individual machine timers.

1. **Recover:** A salvage operation yields a manifest of mixed scrap, intact parts, consumables, and possible damage or contamination. Estimates improve with sensors, crew skill, and prior knowledge; results retain some uncertainty.
2. **Receive and store:** Salvage occupies cargo capacity. Unsorted cargo cannot be used freely in recipes. Dedicated storage protects sensitive electronics, food, gases, and water; poor storage can cause loss or hazards.
3. **Sort:** Assign a sorting bay and workers to convert mixed salvage into usable material categories. Electronics and intact parts may be recovered instead of being broken down. Sorting throughput and skill affect yield and waste.
4. **Refine:** Process scrap into metal stock, polymers, glass/ceramics, and other feedstocks. Refining consumes power and labor, takes time, and creates heat and residues. Different recipes trade yield, speed, energy, and equipment wear.
5. **Fabricate:** Convert refined stock into common machine parts, conductors, seals, electronics, and specialist components. Recipes have input requirements and may need the appropriate machine or crew skill.
6. **Construct or repair:** Modules and repairs consume inventories of parts and materials. Construction also needs an available port, power, crew labor, and sometimes a construction bay. Critical repairs can be prioritized over planned expansion.

**Production management interface:** Use recipe queues with priorities and optional input limits (for example, reserve a minimum stock of electronics for repairs). Show input availability, projected completion, power draw, required staffing, output, and waste. Provide station-wide stock targets and alerts; pause or redirect queues when critical reserves are threatened.

**Bottlenecks and trade-offs:** Cargo volume, sorting throughput, refinery capacity, skilled labor, power, radiator capacity, and storage can each constrain growth. Players should be able to inspect the limiting factor and solve it through construction, scheduling, research, or a different salvage plan.

**Failure and recovery:** A missing input pauses a recipe with a clear explanation rather than silently consuming partial resources. Allow useful salvage to bypass processing when recovered intact. Early game should offer emergency options—rationing, cannibalizing noncritical equipment, or postponing expansion—before an unavoidable death spiral.

## Station Modules (Draft Catalog)
Modules attach at standardized ports in the strategic 3D view. Their connections determine which systems can reach them; each module has a footprint, mass, power draw, crew capacity (if any), and maintenance burden.

### Core and survival
- **Starter habitat / command module:** Initial pressurized refuge, basic controls, and a small amount of storage.
- **Habitat module:** Berths, personal work/rest space, and capacity for additional crew.
- **Life-support module:** Air revitalization, water recycling, filtration, and emergency reserves.
- **Galley and hygiene module:** Food preparation and hygiene capacity; reduces crew penalties from poor living conditions.
- **Medical bay:** Treats illness and injury, supports monitoring and quarantine.
- **Radiation shelter:** Compact storm shelter for crew during solar radiation events.

### Attachments
- **Hull attachments:** Small add-ons on any module's hull slots: solar panel, heat vent, storage crate, fuel or oxygen tank, CO₂ scrubber pack, work light, antenna, comms dish. See `modules.md`.

### Power and station infrastructure
- **Solar array:** Renewable power, vulnerable to damage and orientation constraints.
- **Battery bank:** Stores power for eclipses, peaks, and emergencies.
- **Reactor module (later technology):** Higher, steadier output with fuel and maintenance requirements.
- **Thermal control / radiator:** Rejects waste heat; production expansion may require more radiator capacity.
- **Docking hub and airlock:** Connects visiting craft and enables crew EVA if that feature is added later; can be reinforced to better protect against hostile boarding or docking incidents.
- **Storage modules:** Bulk, refrigerated, pressurized, or secure storage variants; secure compartments can reduce losses during raids.

### Salvage, logistics, and production
- **Sensor / communications mast:** Finds opportunities, improves operation estimates, and extends communications.
- **Salvage control module:** Assigns crews or craft to management-driven recovery operations; improves yield and reduces risk.
- **Workshop:** The first production room: sorts mixed salvage and makes basic parts, kits and electronics, one job at a time. Slower than the dedicated modules below, which take over as the station grows.
- **Sorting bay:** Separates mixed salvage into material categories and recoverable components.
- **Smelter / materials processor:** Converts raw scrap into standardized stock; consumes power and emits heat/waste.
- **Fabricator:** Produces common machine parts, tools, and replacement equipment.
- **Electronics bench:** Repairs or manufactures electronics from scarce inputs; requires skilled technicians.
- **Robot bay / Robotics bay (research unlock):** Docks, builds and repairs the three robot kinds (Service, Builder, Long-range); see `crew.md` → *Robots*.

### Food, research, and long-term projects
- **Hydroponics farm:** Produces food and recycles some water; uses power, water, and crew labor.
- **Seed / food bank:** Stores seeds and emergency rations, protecting against crop failure.
- **Research lab:** Turns staff time, power, and data into technology unlocks.
- **Observatory / survey module:** Improves orbital mapping and discovery of salvage and extraction sites.
- **Greenhouse expansion:** Higher food output and crew wellbeing potential at greater resource and maintenance cost.
- **Construction bay:** Enables large projects and specialized structures, such as new habitats, propulsion, or Earth-recovery infrastructure.

## Crew (Draft)
Crew are individuals managed through assignment and scheduling, not direct character control. Each person has a name, role, skills, condition, and daily routine. Relationships are not simulated.

### Roles and skills
Crew can have a primary specialty plus secondary abilities. Candidate skills use a simple rating scale (for example, novice to expert):
- **Engineering:** Repairs, power systems, thermal control, and construction.
- **Science:** Research, surveys, and analysis of recovered data.
- **Operations:** Salvage planning, logistics, inventory, and station coordination.
- **Medicine:** Diagnosis, treatment, and health monitoring.
- **Agriculture:** Crop yield, seed management, and farm maintenance.
- **Fabrication:** Refining, machine operation, and production quality.

Specialties improve work speed, efficiency, quality, or safety, but avoid making any one crew member an absolute requirement for basic survival. Cross-training and automation should provide resilience.

### Robots
Research unlocks three kinds of robot, docked at a Robot bay and assigned from the same "who does this?" popup as crew. **Service robots** work inside the hulls (racks, interior repairs, workshop benches); **Builder robots** build and repair outside and make short EVA runs; **Long-range robots** fly a shuttle unmanned on salvage missions. They are extra hands for physical work, slower or costlier than a good crew member, need power and wear down, and cannot do research, medicine, rescues or survivor missions, so crew stay essential. Robots are not people: no needs, skills, schedule or morale.

### Needs and condition
- **Oxygen, water, and food:** Immediate survival needs; shortages cause deteriorating condition and eventually death.
- **Rest:** A schedule must provide sleep; fatigue reduces work effectiveness and raises accident risk.
- **Health:** Injury and illness reduce capacity and may require medical treatment or isolation.
- **Safety:** Radiation exposure, pressure leaks, machinery incidents, and dangerous assignments create risk.
- **Morale / comfort:** Optional station-wide or individual condition affected by habitat quality, crowding, lighting, and access to recreation. Keep it distinct from relationships.

### Schedules and assignment
- Divide the day into **work, rest, and personal time** blocks. Assign crew to stations, shifts, or salvage operations; specialized staff should not be scheduled around the clock.
- Workplaces have staffing needs and shift capacity. Overwork can temporarily raise output at the cost of fatigue and accidents.
- Crew may be reassigned and trained; schedules should be inspectable and editable without micromanaging every minute.
- **Population growth:** Begin with a very small crew (roughly two to four people; exact count TBD). Rescue survivors from derelicts, escape pods, and other discovered locations to grow the population. Each rescue is a strategic commitment: assess survival odds, prepare berths and life-support capacity, and decide whether the station can support the newcomers. Rescued people may arrive injured, lack a needed specialty, or require a period of recovery. No births or relationship system is planned for the initial design.

## Core Simulation Rules (Draft)
- **Production chain:** Managed recovery → sorting → refining → component fabrication → module construction and repairs.
- **Station needs:** Power, oxygen/atmosphere, water, food, temperature control, and structural integrity. Crew additionally need rest and medical care.
- **Module condition:** Every module has HP that slowly wears down; its output scales with HP, so neglect erodes the whole economy gradually rather than failing it at once. Repairs cost steel and polymers in proportion to the damage and the module's mass (numbers in `resources.md` → *Construction and repair*).
- **Construction:** Snap modules to compatible ports; connections carry power, air, and logistics. Expansion increases upkeep, labor demand, and maintenance.
- **Hulls and racks:** Most pressurised modules are generic hulls (small, standard, large) whose function comes from the racks fitted inside: berths, storage, O₂ generators, scrubbers, hydroponics, research and workshop benches. Racks can be refitted at any time; presets keep one-click building. Only modules whose shape is their function (Central Module, junctions, greenhouse, wings, gas storage) stay special. Details in `modules.md` → *Hull modules and internal racks*.
- **Attachments:** Besides modules, the player bolts small functional attachments onto module hull slots — small solar panels, heat vents, crates, tanks, scrubber packs, lights, antennas, dishes. They are cheap, fine-grained upgrades that never add berths or ports. Rules and catalogue in `modules.md` → *Attachments*.
- **Orbit maintenance:** The station flies low enough that the thin upper atmosphere drags it down. Altitude is tracked continuously and shown in the HUD; decay accelerates as the orbit lowers (the air gets denser), so neglect turns a slow chore into an emergency. The player reboosts from time to time: a thruster burn raises the orbit at a fixed rate and burns propellant in proportion to the station's mass, so every module added makes station-keeping more expensive. Below a warning altitude the HUD alerts with a time-to-reentry forecast; at the reentry altitude the station is lost. Numbers are in `resources.md` → *Orbit and propellant*.
- **Threats:** Supply shortages, equipment failures, debris impacts, radiation, risky salvage operations, and pirate activity. Incidents should be forecastable enough to plan around rather than constant surprise punishment.
- **Pirates:** Hostile scavenger crews and pirate groups compete for salvage and may threaten trade routes, isolated craft, or the station itself. Encounters are handled through strategic decisions, not direct combat: detect and evade, secure cargo, pay or barter a toll, negotiate, call for help, or risk a defensive response. Threat level and likely consequences should be signaled so players can prepare. Defensive options may include reinforced docking areas, decoy cargo, escorts, communications, and nonlethal deterrents; defenses cost resources and cannot make the station invulnerable. Pirate groups can have distinct capabilities and motives, creating opportunities for avoidance, diplomacy, or conflict without requiring every encounter to become a battle.
- **Trade and other stations:** Trade with other orbital settlements is a planned mid-to-late-game system, not an assumption of a busy interplanetary market. Procedural discoveries can reveal stations, enclaves, or independent ships. Establishing communications and safe routes opens negotiated, asynchronous exchanges: offer surplus materials, manufactured goods, or services in return for scarce supplies, specialist components, data, or rescue support. Trade is constrained by distance, cargo capacity, timing, and risk, so it complements rather than replaces salvage and production.
  - **Contact:** Detect a signal or encounter a vessel; identify the community and its needs through scans and communications.
  - **Terms:** Review current wants and offers, then propose a cargo-for-cargo exchange. Use barter, not a universal currency: each community has current needs, offers, and finite inventories. Show an estimated fairness indicator based on relative value and demand, but let players negotiate cargo quantities and accept an uneven deal when the situation warrants it.
  - **Delivery:** Assign a craft or organize a rendezvous. Travel takes time and can expose cargo and crew to hazards; early trade may be limited to nearby contacts.
  - **Consequences:** Reliable deals can unlock repeat exchanges, information, rescue opportunities, or joint projects. Breaking agreements or sending unsafe cargo can damage trust. Keep trade a strategic logistics decision, not a dialogue-management game.
  - **Design limits:** Other stations have their own survival needs and finite stocks. Trade should create dilemmas—sell a rare component now or reserve it for repairs—not become a frictionless fix for every shortage.
- **Progression:** Research and recovered data reveal improved modules, automation, safer operations, and optional pieces of Earth's history.
- **Research and technology:** Yes—there is a planned tech progression, but the full tree is not locked down. Use a set of interconnected technology branches rather than one linear ladder. Research consumes crew time, power, and data; unlocking a technology grants new recipes, modules, or operating efficiencies. Some discoveries require salvaged prototypes or survey findings, so expansion and exploration feed research.
- **Draft research branches:**
  - **Life Support & Medicine:** More efficient recycling, better crop yields, improved treatment, and safer rescue recovery.
  - **Materials & Fabrication:** Better sorting and refining yields, advanced alloys, electronics repair, and new fabrication recipes.
  - **Power & Thermal:** More efficient solar/batteries, improved radiators, and later-generation power systems.
  - **Automation & Logistics:** Robotics (assignable work robots), improved storage and routing, reduced routine labor, and smarter production controls.
  - **Orbital Operations:** Better sensors, salvage planning, communications, and safer long-range operations.
  - **Major Projects:** Technologies required for large endings-related projects: orbital population infrastructure, interplanetary propulsion and life support, and Earth restoration/return systems.
- **Research design guardrails:** Avoid mandatory research grinding. Give meaningful choices between near-term survival improvements and long-term capabilities; make branches cross-link at key milestones, while leaving multiple viable routes to each major goal. Research should not make crew specialties or physical resources obsolete.
- **End goals:** Support all major futures: establish a durable orbital civilization, build and launch a mission to another habitable world, and develop a path to restore or safely reinhabit Earth. These are substantial projects that can compete for resources but should not be mutually exclusive by default; player decisions and the station's condition determine which are completed and the resulting ending. Additional outcomes may include preserving a small, sustainable refuge or failing to maintain the station.

## Early-Game Arc

The opening is a hardcore survival scramble, specified in [`objectives.md`](objectives.md). The player starts with a damaged module and several simultaneous crises (rising CO₂, a decaying orbit, little food, no water recycling, no batteries) and no materials to fix them. Dying and restarting a few times before finding the right order is expected.

1. Stabilize the starting module: the starter stock repairs it only if the player dismantles something (the small solar panel is the one good choice).
2. Do the first **EVA haul** of nearby scrap, the only source of materials at first (no radar or shuttle needed).
3. Research and build the research bench, then batteries, hydroponics and a water recycler, in whatever order survives.
4. Build a second module, then work up the fuel chain: solar arrays, radiator, workshop, fuel producer, and a boost to 420 km.
5. Respond to needs as they appear: medical rack, medical bay, exercise machine, greenhouse.
6. Reach out: radar, docking port, a shuttle, and a first mission.

The late game is deliberately left open for now.

## Open Questions
- Is this primarily a **single-player campaign**, a sandbox, or both? The campaign should support multiple endings.
- Who is the player in-world: a station commander, an AI, a crew collective, or something else? How many people are aboard at the start?
- **Resolved:** The main play view is a strategic 3D view with snap-based module construction. Salvaging is handled through management decisions; direct-control missions may be explored later.
- **Resolved:** Crew are individuals with needs, skills, and schedules; relationships are out of scope.
- **Resolved:** Earth's destruction is background story; day-to-day survival is the main focus. How much optional lore should players be able to uncover?
- What is the intended mood: bleak survival, hopeful rebuilding, or a balance? How punishing should failure be?
- **Resolved:** Support a broad range of long-term goals and multiple endings, including sustaining a large orbital population, reaching another world, and restoring Earth. Players should be able to pursue different goals rather than being locked to a single victory condition.
- **Resolved:** Pirates are a threat. Encounters are strategic choices rather than direct-control combat; define how costly, frequent, and avoidable they should be.
- **Resolved:** Start with a tiny crew of roughly two to four people and grow by rescuing survivors. Support orbital civilization, reaching another world, and restoring Earth as long-term goals.
- **Resolved:** Rescued survivors are found through procedural discoveries. How large should a successful station population be?
- **Resolved:** Trade uses barter shaped by each community's needs and finite inventory. How hands-on should arranging deliveries and rendezvous be?
- What platform and scope are we designing for (PC/console, solo project/team, target session length)?
