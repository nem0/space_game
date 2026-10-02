# Crew — Numerical Design Draft

**Status:** First-pass rules and balance targets for the individual crew simulation. Crew are managed from the strategic station view; there is no direct character control and no relationship simulation. Values are provisional and should be playtested with the resource rules in [`resources.md`](resources.md) and module capacities in [`modules.md`](modules.md).

## Design goals

- Crew members are distinct people with names, skills, needs, schedules, health, and a personal history.
- The player assigns people to work and chooses schedules; the simulation handles routine activity.
- Start with a very small crew, then grow mainly by finding and rescuing survivors through procedural discoveries.
- A specialist improves work but is not an irreplaceable key. Cross-training and automation prevent a single death or injury from making the game unwinnable.
- Robots (three kinds, research unlocks) are extra hands for physical work and unmanned missions, not people: see *Robots*.
- No romance, friendship, rivalry, or relationship meters. Crew reactions are driven by their condition and station circumstances, not social graphs.

## Crew member data

Each person has:

- **Name, age, pronouns, portrait, and biography:** Presentation and optional narrative context; age does not affect baseline consumption in the initial system.
- **Primary specialty:** One of Engineering, Science, Operations, Medicine, Agriculture, or Fabrication.
- **Skill ratings:** Six values from 0 to 5. Rating 0 is untrained; 1 novice; 2 capable; 3 skilled; 4 expert; 5 master.
- **Condition values:** Health 0–100, fatigue 0–100, morale 0–100, radiation dose, and current medical status.
- **Schedule and assignment:** Current shift template, assigned workplace or duty, and task priority.

Starting crew target: **3 people** (acceptable range 2–4), with varied specialties rather than a full set of experts. A starting crew of 2 should still be viable through the Starter Habitat's basic controls and early salvage opportunities.

## Work: every action needs a crew member and takes time (implemented)

- Every order that needs a worker opens a **"who does this?" popup** listing the people who are free (name, what they do now, STR / INT / DEX / END and fitness); the player picks one and the order starts with them. Nothing is selected beforehand. The same popup also lists free robots once they exist (see *Robots*). With nobody free it says so. The TASKS panel at the bottom of the screen lists every job under way with its worker, time left and progress.
- **Building** a module, **fitting** a rack or attachment, **dismantling**, and **repairing** become jobs on the item: it shows as a ghost while being built and does nothing until finished. Duration = materials × `WORK_MIN_PER_KG` (5 game min per kg; a Standard hull ~10 h, a berth ~6 h); dismantling takes half; repairs 20 min per kg of repair material. Materials are paid at the start.
- **Shuttle missions and reboost burns** take the crew member away for their duration. Missions come from radar contacts (README, scripts/config.evox MissionKind): survivors arrive when the shuttle returns, settlers fly over on their own; every mission has a failure chance.
- **Benches** (workshop, research) only produce while a crew member is assigned to them (*staff* button in the module panel). Taking a bench worker for another job frees the bench.
- A crew member who dies (suffocation, starvation, CO₂) leaves their job paused; click the item and pick someone else to resume it.
- Later: skills speed jobs up (`1 + skill × 0.1`), fatigue slows them, schedules decide when people work.

## Robots (research unlock; design only, not implemented)

Robots are a second kind of worker, unlocked by research (`tech_tree.md` → *D. Automation & Logistics*). They answer one problem: a small crew with more jobs than hands. They are deliberately not people, so they never replace the crew for the work that needs a person. There are **three kinds**, each built for one place to work, unlocked one after another:

| Kind | Id | Works | Can do | Cannot do | Unlock |
|---|---|---|---|---|---|
| **Service robot** | SV-1… | Inside the hulls | Fit and remove racks, repair racks and a module's interior, staff a **workshop bench** (sorting, machine parts, repair kits, drills) | Anything outside the hull; research, medicine, missions | *Robotics* |
| **Builder robot** | BD-1… | Outside the hull and in open space | Build and dismantle **modules**, fit, dismantle and repair **attachments**, repair a module's hull, build a shuttle at a docking hub, and make **short EVA runs without a shuttle** (nearby scrap) | Racks, benches, anything in the pressurised interior; missions that need a shuttle | *Orbital Robotics* |
| **Long-range robot** | LR-1… | Away from the station | Flies a **shuttle on its own** (no pilot) on unmanned missions: debris fields, dead satellites, asteroids (it takes the mining drill like a crew member would) | Survivor missions (derelicts, pods, settlers), EVA, any job at the station | *Autonomous Navigation* |

A job a kind cannot do simply does not list that kind in the assign popup. Whole-station repair and a single module's repair accept a Service or a Builder robot (the Service robot works the interior and racks, the Builder the hull). Reboost burns, research, exercise machines, nursing, rescues and survivor missions stay with **people**.

**What a robot is**

- A unit with an id, a **kind**, a **condition** 0–100% and a current job. It has no name, skills, needs, morale, fatigue, injuries, schedule or fitness, eats and breathes nothing, and does not count toward berths, food, water, oxygen, crew caps or the crew win goal. It works at any time of day; shifts do not apply.
- **Work rate:** Service ×0.8, Builder ×1.0 (heavy-duty actuators). A Long-range robot has no work rate: a mission takes its normal flight time, with an average pilot's risk. An average crew member is ×1.0, a strong one up to ×1.4. *Servo Upgrades* adds +0.2 to the rate of Service and Builder robots.
- **Power:** Service 1.0 kW and Builder 1.5 kW while working, 0.1 kW while idle and docked; a Long-range robot draws nothing while its shuttle is away. The draw is part of the station power budget; in a brownout docked robots stop and their jobs pause, like a job with nobody on it.

**Assigning robots**

- Robots use the same popup as crew: free robots that can do the order are listed below the people, tagged with their kind (SV / BD / LR), condition and work rate, and picking one starts the order with it. A job a robot is on shows its id in the module panel and in the TASKS panel (`BD-2: Building Small Hull, 40 min left`). A robot that is working, or away on a mission, cannot be picked again until it is back.
- A paused job can be resumed by clicking it and choosing a robot, exactly as with crew.
- When a robot breaks down its job pauses; it never fails silently.

**Getting robots**

- Robots are docked in **Robot bay** racks (`modules.md`): each rack holds 2 robots of any kind. A robot always counts against a dock, even while away. Without a free dock no robot can be built. The later **Robotics Bay** module holds 6 and builds robots by itself.
- A robot is built as a job by a *crew member* at a Robot bay (robots cannot build robots), taking the usual build time for its mass. Costs, steel / electronics / polymers / machine parts: **Service 25 / 30 / 10 / 15** (80 kg), **Builder 50 / 40 / 15 / 30** (135 kg), **Long-range 70 / 80 / 20 / 50** (220 kg, with a navigation core). Electronics are heavy on purpose, since they are scarce. A robot can be dismantled for half its materials.

**Wear, breakdowns and losses**

- Working wears a robot down by **2% condition per 8 hours of work** (a mission day counts as a work day), on top of the general module wear. Below 25% condition its work rate halves. At 0% it is **disabled** (it cannot be assigned and its job pauses) but never destroyed by wear.
- A crew member repairs a robot at its bay for 20% of its materials, using the usual repair rules. A repaired robot returns at full condition.
- **Radiation and solar storms** disable a Service or Builder robot outside a shelter for 6 hours unless *Hardened Electronics* is researched (Long-range robots are shielded). Robots do not die; they just stop.
- **Losses:** a Builder robot on an EVA run, or a Long-range robot on a mission, is **lost** when the run fails (the mission's normal failure chance). No injury is possible, but the robot is gone and has to be built again; its dock becomes free.

**Balance goals**

- With 2–3 crew a station is always short of hands. Two Service robots (160 kg) should roughly double the parallel interior jobs mid-game; Builder robots (135 kg) take the slow external building off the crew; one Long-range robot (220 kg) lets a shuttle fly while every person is busy or the mission is not worth a life.
- Robots do not remove the need for people: research, medicine, rescues and the win goal still need crew, and survivor missions can never be automated. Nothing a robot does is needed for basic survival, so losing every robot never loses the game.
- Each kind costs materials (mostly electronics), a dock and power, so the player chooses between more robots and, say, another hull or solar wing.
- Robots must not make the TASKS list or the assign popup longer to use; they appear in the same flow as people.

## Skills and work effects

A crew member's effective work multiplier is:

`1.0 + (skill rating × 0.10)`

Thus skill 0 works at 100% base rate; skill 5 works at 150%. For a task with two relevant skills, use the primary relevant skill only, avoiding stacked multipliers. Fatigue and health modify this rate as described below.

| Skill | Applies to | Example benefit |
|---|---|---|
| **Engineering** | Repairs, power, thermal systems, construction | Shorter construction/repair duration; fewer machinery incidents |
| **Science** | Research, surveys, data analysis | More research points or more accurate discovery estimates |
| **Operations** | Salvage planning, logistics, inventory, trade | Better salvage manifests, lower mission risk, faster cargo handling |
| **Medicine** | Diagnosis, treatment, health monitoring, rescue triage | More patients treated; faster recovery |
| **Agriculture** | Hydroponics, seeds, farm upkeep | Improved food yield; fewer crop failures |
| **Fabrication** | Sorting, refining, machine operation, electronics repair | Better recovery yield and production throughput |

**Skill progression:** Each completed 8-hour work shift grants 1 relevant experience point, capped at 20 points per skill level. Skill level-up costs 20 experience for levels 1–2, 30 for level 3, 40 for level 4, and 50 for level 5. Training occupies 2 work-hours/day and provides 1 additional experience point/day in the chosen skill. This is a slow, steady progression; rescued specialists remain valuable.

## Needs and condition

### Food, water, and oxygen
Use the baseline rates from `resources.md`:

- **Food:** 1 RU/person/day.
- **Water:** 1 RU/person/day gross, or 0.8 with Galley and Hygiene; 80% of used water is recovered by operating Life Support.
- **Oxygen:** 0.8 RU/person/day gross; 70% recovery gives 0.24 RU/person/day net replacement when Life Support operates within capacity.
- If any essential need is unmet, give a visible warning immediately. After 12 hours of shortage, health begins falling by 2 points per day; after 3 consecutive days, the loss rises to 10 points/day. Restore supply to stop decline. At health 0, the crew member dies.

### Rest and fatigue

- A standard day contains **8 work hours, 8 rest hours, and 8 personal hours**.
- Fatigue runs from 0 (rested) to 100 (exhausted). Start each day at 20; each scheduled work-hour adds 5 fatigue; each rest-hour removes 6 fatigue; personal time removes 2 fatigue/hour.
- At fatigue 50+, work rate is reduced by 10%; at 75+, reduced by 30%; at 90+, the person refuses non-emergency work. A full 8-hour rest period reduces fatigue by 48 points.
- Overtime is allowed by schedule, but each extra work-hour adds 8 fatigue and has a 2% base daily chance of a work incident, increasing by 1 percentage point for every 10 fatigue above 50.

### Fitness

- Each crew member has **fitness** 0–1, starting at 1. It falls steadily in microgravity (10% per game day, also while away on a mission) and is restored by using an **exercise machine** rack (+25% per hour; the crew member steps off when fully fit). About half an hour of exercise a day holds it.
- Below 50% fitness, every work multiplier of theirs (work speed, bench output, missions) falls linearly to 50% at 0 fitness. Crossing 50% triggers the *exercise machine* objective (`objectives.md` #19).

### Health, injury, and illness

- **Two injury tiers.** *Minor injuries* (random; higher chance on missions) lower the crew member's output until treated at a **medical rack**. *Serious injuries* (rarer; also higher on missions) leave the crew member unable to work, and their health falls until treated in a **Medical Bay** with **another crew member** attending as caregiver. The caregiver does no other work meanwhile; Medicine skill speeds recovery, but anyone can do it. A serious injury left untreated for too long is fatal, with a visible health decline, not an instant death. Crew injured for the first time trigger the *medical rack* objective; the first serious injury triggers the *Medical Bay* objective.

- Health is 0–100. Below 50, work rate is reduced by 25%; below 25, the crew member is incapacitated and needs medical care.
- Injury or illness applies a named status with a duration and effect (e.g., sprain: −50% work rate for 3 days; infection: isolation required, health loss if untreated).
- Medical Bay capacity is 2 patients/day and halves recovery time for treated cases, as specified in `modules.md`.
- A serious medical incident should not instantly kill a healthy crew member; use warning stages and time for treatment unless the initiating event is explicitly catastrophic.

### Morale and comfort

- Morale is 0–100, starts at 70, and changes once per day based on housing, crowding, food quality, safety, and personal-time facilities.
- Below 40, work rate is reduced by 10%; below 20, reduced by 25% and the person may refuse optional overtime.
- Each occupant needs an assigned berth. Housing every occupant above capacity causes −5 morale/day. A successful rescue without a free berth causes −10 morale/day for all residents until capacity is restored.
- Greenhouse personal-time access grants +2 morale/day to up to 8 assigned crew, as specified in `modules.md`; cap morale at 100.
- Morale is individual condition, not a relationship score. No crew member has a social compatibility value.

### Radiation and safety

- Track accumulated radiation in a dose meter (0–100). At 25, apply −5 health; at 50, −15 health and −10% work rate; at 75, −30 health and require medical monitoring; at 100, the crew member dies.
- Dose decays by 1 point per 30 safe days. Radiation Shelter reduces event dose by 90% for sheltered crew.
- A crew member assigned to a hazardous salvage operation receives an estimated risk before dispatch. Base incident chance is 10%; Operations skill 5 lowers it by 5 percentage points; Salvage Control lowers it by 10 points. Minimum incident chance is 1%.

## Schedules, shifts, and assignments

- Schedules use three blocks per day: **Work (8h), Rest (8h), Personal (8h)**. Players choose when each block occurs; crew on different shifts can keep critical modules staffed around the clock.
- Each module lists staffing per 8-hour shift. One worker assigned to a module covers one shift; 24-hour operation generally requires three shift assignments unless automated or the module explicitly uses a daily batch job.
- The UI shows required vs. assigned staffing and the projected output penalty. If a staffed module lacks its full shift crew, output scales linearly with staffed fraction; below 50% of required staffing, it operates at half of that scaled rate.
- A person cannot work two modules in the same time block. Assignment conflicts are highlighted before confirming the schedule.
- Emergency priorities can override a schedule for a limited period. Affected crew gain fatigue and morale penalties, shown in advance.
- Personal time is not a relationship or freeform activity simulation; it is recovery time. Optional facilities can provide explicit morale effects.

## Rescuing survivors

Procedural discoveries may reveal survivors in escape pods, derelicts, shelters, or other stations. A rescue is a strategic operation, not a direct-control mission.

### Discovery and assessment

- Each suitable discovery has a **20% base chance** to contain one or more living survivors; special location types can raise or lower this chance.
- The player receives an estimated count (±1 person), condition, and rescue risk. Observatory and sensor bonuses improve discovery timing and estimates, not guaranteed survivor odds.
- An operation takes **1–5 days**, depending on distance. The player commits cargo capacity and assigned crew/escort assets before dispatch.

### Rescue capacity and outcome

- Each rescued person requires one free berth, life-support capacity for 1 person, and **5 RU cargo capacity** for the transfer operation.
- Rescue operations have a **10% base chance** of an incident. Operations skill and escort effects reduce this chance; incidents can damage cargo, delay return by 1–3 days, or injure a survivor.
- Rescued crew may arrive with health 25–90, fatigue 20–80, and a randomly assigned skill profile. Each survivor gets at least one skill at rating 2 or higher, and has a 25% chance to have a specialty matching a detected station need.
- A newly rescued survivor requires **1 day of medical screening** before full work assignment. Injured survivors take longer according to their condition.
- The player may decline a rescue if capacity or supplies are insufficient. If accepted, the station must meet their food, water, oxygen, berth, and medical needs on arrival.
- Survivors are not guaranteed to be friendly, but initial scope treats successful survivors as recruitable. Hostile encounters belong to pirate/event systems, not a hidden betrayal mechanic.

## Death, incapacitation, and resilience

- Death is possible through prolonged unmet needs, severe radiation, or explicitly catastrophic incidents; communicate danger and provide time to respond whenever reasonable.
- An incapacitated crew member consumes supplies but cannot work; treatment or recovery restores capacity.
- Never gate basic life support behind a single specialty or living person. Starter systems should continue in an emergency at reduced efficiency, and recipes should have alternate/manual options where practical.
- On losing a specialist, the player can cross-train another crew member, rescue someone with the needed skill, trade for assistance, or accept lower efficiency until automation/research helps.

## UI requirements

- Crew roster: name, role, six skills, health, fatigue, morale, radiation, current assignment, and next schedule block.
- Staffing view: modules by shift, required/assigned workers, projected output, and conflict warnings.
- Rescue preview: estimated survivors, arrival window, risk range, required berths, and projected additional daily food/water/oxygen needs.
- Alerts identify the cause and deadline: e.g. “Water reserves last 2.4 days at current staffing,” not just “crew in danger.”
- Show the exact effect of assigning or rescheduling a person before applying it.
- Robots: a ROBOTS block in the CREW panel (id, kind, condition, job, dock), robot rows in the assign popup after the people (only those that can do the order), and robot ids in the TASKS panel and the module panel.

## Open design questions

- Should crew death be permanent in standard play, or should an optional relaxed mode prevent death while retaining penalties?
- Are 3 starting crew and the resource rates in `resources.md` a suitable opening balance?
- Should fatigue be a numeric meter, or should the game display simpler rested/tired/exhausted states backed by these values?
- Should crew have fixed backgrounds/specialties, or be generated entirely by procedural discoveries?
- Should a failed EVA run or unmanned mission always lose the robot, or only sometimes (a damaged robot recovered later)?
- Should a later tier let robots build robots, and should the Long-range robot be allowed on survivor missions once it has a medical module?
- Are the work rates (Service ×0.8, Builder ×1.0) and the 80 / 135 / 220 kg costs the right balance against another crew member?
