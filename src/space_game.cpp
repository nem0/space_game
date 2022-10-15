#include "engine/engine.h"
#include "engine/input_system.h"
#include "engine/log.h"
#include "engine/lua_wrapper.h"
#include "engine/plugin.h"
#include "engine/prefab.h"
#include "engine/profiler.h"
#include "engine/reflection.h"
#include "engine/resource_manager.h"
#include "engine/universe.h"
#include "gui/gui_scene.h"
#include "gui/gui_system.h"
#include "lua_script/lua_script_system.h"
#include "renderer/model.h"
#include "renderer/render_scene.h"
#include <cstdio>

using namespace Lumix;

static const ComponentType MODEL_INSTANCE_TYPE = reflection::getComponentType("model_instance");
static const ComponentType LUA_SCRIPT_TYPE = reflection::getComponentType("lua_script");
static const ComponentType GUI_BUTTON_TYPE = reflection::getComponentType("gui_button");

struct Blueprint {
	char type[32] = "Not set";
	char label[64] = "Not set";
	PrefabResource* prefab = nullptr;
	char desc[2048];
	float power_cons = 0;
	float power_prod = 0;
	float heat_cons = 0;
	float heat_prod = 0;
	float water_cons = 0;
	float water_prod = 0;
	float food_cons = 0;
	float food_prod = 0;
	float air_cons = 0;
	float air_prod = 0;
	float volume = 0;
	float material_cost = 0;
	float build_time = 0;
} blueprint;
using BlueprintHandle = u32;


struct Extension {
	u32 id;
	EntityPtr entity;
	float build_progress = 0.f;
	BlueprintHandle blueprint = 0xffFFffFF;
};

struct CrewMember {
	u32 id;
	StaticString<128> name;
	enum State {
		IDLE,
		BUILDING
	} state = IDLE;
	u32 subject = 0xffFFffFF;
};

struct Module {
	Module(IAllocator& allocator) : extensions(allocator) {}

	void serialize(OutputMemoryStream& blob) {
		blob.write(id);
		blob.write(entity);
		blob.write(build_progress);
		blob.write(extensions.size());
		for (const Extension* e : extensions) {
			blob.write(*e);
		}
	}

	void deserialize(InputMemoryStream& blob, IAllocator& allocator) {
		blob.read(id);
		blob.read(entity);
		blob.read(build_progress);
		const i32 size = blob.read<i32>();
		extensions.resize(size);
		for (Extension*& e : extensions) {
			e = LUMIX_NEW(allocator, Extension);
			blob.read(*e);
		}
	}

	u32 id;
	EntityRef entity;
	Array<Extension*> extensions;
	float build_progress = 0.f;
};

struct Stats {
	struct {
		float air = 0;
		float power = 0;
		float heat = 0;
		float water = 0;
		float food = 0;
	} production;
	struct {
		float air = 0;
		float power = 0;
		float heat = 0;
		float water = 0;
		float food = 0;
		float fuel = 0;
	} consumption;
	
	struct {
		float food = 0;
		float water = 0;
		float fuel = 0;
		float materials = 0;
	} stored;
	struct {
		float food = 0;
		float water = 0;
		float fuel = 0;
		float materials = 0;
	} storage_space;
	float volume = 0;
	float efficiency = 1.f;
};

struct SpaceStation {
	SpaceStation(IAllocator& allocator) 
		: modules(allocator) 
		, crew(allocator) 
	{}
	Array<Module*> modules;
	Array<CrewMember> crew;
	Stats stats;
};

struct Assets {
	PrefabResource* module_2 = nullptr;
	PrefabResource* module_3 = nullptr;
	PrefabResource* module_4 = nullptr;
	PrefabResource* solar_panel = nullptr;
};

struct Game : IPlugin {
	Game(Engine& engine)
		: m_engine(engine)
	{
		ResourceManagerHub& rm = m_engine.getResourceManager();
		m_assets.module_2 = rm.load<PrefabResource>(Path("prefabs/module_2.fab"));
		//m_assets.module_3 = rm.load<PrefabResource>(Path("prefabs/module_3.fab"));
		//m_assets.module_4 = rm.load<PrefabResource>(Path("prefabs/module_4.fab"));
		m_assets.solar_panel = rm.load<PrefabResource>(Path("prefabs/solar_panel.fab"));
	}

	~Game() {
		m_assets.module_2->decRefCount();
		if (m_assets.module_3) m_assets.module_3->decRefCount();
		if (m_assets.module_4) m_assets.module_4->decRefCount();
		m_assets.solar_panel->decRefCount();
	}

	u32 getVersion() const override { return 0; }
	void serialize(OutputMemoryStream& stream) const override {}
	bool deserialize(u32 version, InputMemoryStream& stream) override { return version == 0; }

	void createScenes(Universe& universe) override;

	const char* getName() const override { return "game"; }

	Assets m_assets;
	Engine& m_engine;
};


struct GameScene : IScene {
	GameScene(Game& game, Universe& universe) 
		: m_game(game)
		, m_universe(universe)
		, m_station(game.m_engine.getAllocator())
		, m_allocator(game.m_engine.getAllocator())
		, m_blueprints(game.m_engine.getAllocator())
	{
		lua_State* L = m_game.m_engine.getState();
		LuaWrapper::createSystemClosure(L, "Game", this, "signal", lua_signal);
		LuaWrapper::createSystemClosure(L, "Game", this, "getStationStats", lua_getStationStats);
		LuaWrapper::createSystemClosure(L, "Game", this, "getModule", lua_getModule);
		LuaWrapper::createSystemClosure(L, "Game", this, "getBlueprints", lua_getBlueprints);
		LuaWrapper::createSystemClosure(L, "Game", this, "getCrew", lua_getCrew);
		LuaWrapper::createSystemClosure(L, "Game", this, "assignBuilder", lua_assignBuilder);
		LuaWrapper::createSystemClosure(L, "Game", this, "onGUIEvent", lua_onGUIEvent);

		#define EXT(_type, _label, _volume, _material_cost, _build_time) \
			Blueprint& _type = m_blueprints.emplace(); \
			copyString(_type.type, #_type); \
			copyString(_type.label, _label); \
			_type.volume = _volume; \
			_type.material_cost = _material_cost; \
			_type.build_time = _build_time; \

		EXT(air_recycler, "Air recycler", 5, 1000, 1);
		air_recycler.air_prod = 2000;
		air_recycler.power_cons = 25;
		copyString(air_recycler.desc, R"#(Basic air recycler. It removes carbon dioxide from air and adds oxygen.
It consumes 25 kJ/s of electricity.)#");

		EXT(water_recycler, "Water recycler", 5, 1000, 1);
		water_recycler.water_prod = 10;
		water_recycler.power_cons = 25;
		copyString(water_recycler.desc, R"#(Basic water recycler recycles all kinds of waste water, including urine.
It produces drinkable water and needs 25 kJ/s of electricity to do so.)#");

		EXT(solar_panel, "Solar panel", 0, 1500, 2);
		solar_panel.power_prod = 120; // avg, max is 240
		solar_panel.prefab = m_game.m_assets.solar_panel;

		EXT(toilet, "Toilet", 0, 500, 2);
		toilet.power_cons = 10;
		copyString(toilet.desc, R"#(It's used to dispose of urine and excrements.
The waste is stored, so it can be recycled later.
It consumes 5 kJ/s of electricity.)#");

		
		EXT(sleeping_quarter, "Sleeping quarter", 6, 30, 1);
		copyString(sleeping_quarter.desc, R"#(A place for one crewmember to sleep. 
While people can sleep even without sleeping quarter, 
it lower their health and morale considerably.)#");

		EXT(hydroponics, "Hydroponics", 45, 300, 3);
		hydroponics.food_prod = 10;
		hydroponics.power_cons = 250;
		hydroponics.water_cons = 2;
		copyString(hydroponics.desc, R"#(A method of growing plants without soil, 
by instead using mineral nutrient solutions in a water solvent.
It consumes 10 kJ/s of electricity and 5l/day of water.
It produces 20 000 kcal/day of food.)#");

		#undef EXT
	}

	static int lua_onGUIEvent(lua_State* L) {
		const char* event_name = LuaWrapper::checkArg<const char*>(L, 1);
		GameScene* game = getClosureScene(L);
		if (!game) return 0;

		game->onGUIEvent(event_name);
		return 0;
	}

	void onGUIEvent(const char* event_name) {
		const RuntimeHash event_hash(event_name);
		static const RuntimeHash time_0x_event("time_0x");
		static const RuntimeHash time_1x_event("time_1x");
		static const RuntimeHash time_2x_event("time_2x");
		static const RuntimeHash time_4x_event("time_4x");

		static const RuntimeHash build_module_2_event("build_module_2");
		static const RuntimeHash build_module_3_event("build_module_3");
		static const RuntimeHash build_module_4_event("build_module_4");
		static const RuntimeHash build_solar_panel_event("build_solar_panel");
		
		if (event_hash == time_0x_event) {
			m_time_multiplier = 0;
			return;
		}
		if (event_hash == time_1x_event) {
			m_time_multiplier = 1;
			return;
		}
		if (event_hash == time_2x_event) {
			m_time_multiplier = 2;
			return;
		}
		if (event_hash == time_4x_event) {
			m_time_multiplier = 4;
			return;
		}
		
		if (event_hash == build_module_2_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.module_2, {0, 0, 0}, Quat::IDENTITY, 1.f, entity_map);
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.module_2;
			return;
		}
		if (event_hash == build_module_3_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.module_3, {0, 0, 0}, Quat::IDENTITY, 1.f, entity_map);
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.module_3;
			return;
		}
		if (event_hash == build_module_4_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.module_4, {0, 0, 0}, Quat::IDENTITY, 1.f, entity_map);
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.module_4;
			return;
		}
		if (event_hash == build_solar_panel_event) {
			ASSERT(false);
			/*ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.solar_panel, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.solar_panel;
			m_build_ext_type = Extension::Type::SOLAR_PANEL;*/
			return;
		}
		if (startsWith(event_name, "build_")) {
			addExtension(*m_selected_module, event_name + stringLength("build_"), INVALID_ENTITY);
			return;
		}
		ASSERT(false);
	}

	i32 getBuilder(const Extension& ext) const {
		for (const CrewMember& c : m_station.crew) {
			if (c.subject == ext.id && c.state == CrewMember::BUILDING) return c.id;
		}
		return -1;
	}

	static void push(GameScene* game, lua_State* L, Extension& ext) {
		lua_newtable(L); // [ext]
		LuaWrapper::setField(L, -1, "id", ext.id);
		LuaWrapper::setField(L, -1, "entity", ext.entity.index);
		LuaWrapper::setField(L, -1, "blueprint", ext.blueprint);
		LuaWrapper::setField(L, -1, "builder", game->getBuilder(ext));
		LuaWrapper::setField(L, -1, "build_progress", ext.build_progress);
	}

	static int lua_assignBuilder(lua_State* L) {
		const u32 obj_id = LuaWrapper::checkArg<u32>(L, 1);
		const u32 crewmember_id = LuaWrapper::checkArg<u32>(L, 2);

		GameScene* game = getClosureScene(L);
		if (!game) return 0;

		for (CrewMember& c : game->m_station.crew) {
			if (c.id == crewmember_id) {
				c.state = CrewMember::BUILDING;
				c.subject = obj_id;
				return 0;
			}
		}

		logError("Invalid crewmember in assignBuilder");

		return 0;
	}

	static GameScene* getClosureScene(lua_State* L) {
		const int index = lua_upvalueindex(1);
		if (!LuaWrapper::isType<GameScene>(L, index)) {
			logError("Invalid Lua closure");
			ASSERT(false);
			return nullptr;
		}
		return LuaWrapper::checkArg<GameScene*>(L, index);
	}

	static int lua_getCrew(lua_State* L) {
		GameScene* game = getClosureScene(L);
		if (!game) return 0;

		LuaWrapper::DebugGuard guard(L, 1);
		lua_newtable(L); // [crew]
		for (const CrewMember& member : game->m_station.crew) {
			lua_newtable(L); // [crew, member]
			switch (member.state) {
				case CrewMember::BUILDING: LuaWrapper::setField(L, -1, "state", "building"); break;
				case CrewMember::IDLE: LuaWrapper::setField(L, -1, "state", "idle"); break;
			}
			LuaWrapper::setField(L, -1, "subject", member.subject);
			LuaWrapper::setField(L, -1, "id", member.id);
			LuaWrapper::setField(L, -1, "name", member.name.data);

			const int idx = 1 + int(&member - game->m_station.crew.begin());
			lua_rawseti(L, -2, idx); // [crew]
		}

		return 1;
	}

	static int lua_getModule(lua_State* L) {
		const EntityRef e = LuaWrapper::checkArg<EntityRef>(L, 1);
		GameScene* game = getClosureScene(L);
		if (!game) {
			ASSERT(false);
			return 0;
		}

		const int midx = game->m_station.modules.find([&](Module* m){ return m->entity == e; });
		if (midx < 0) {
			ASSERT(false);
			return 0;
		}

		LuaWrapper::DebugGuard guard(L, 1);
		Module* m = game->m_station.modules[midx];
		lua_newtable(L); // [module]
		LuaWrapper::setField(L, -1, "id", m->id);
		LuaWrapper::setField(L, -1, "entity", m->entity);
		LuaWrapper::setField(L, -1, "build_progress", m->build_progress);
		lua_newtable(L); // [module, exts]
		lua_setfield(L, -2, "extensions"); // [module]
		lua_getfield(L, -1, "extensions"); // [module, exts]

		for (Extension*& ext : m->extensions) {
			const int idx = 1 + int(&ext - m->extensions.begin());
			push(game, L, *ext); // [module, exts, ext]
			lua_rawseti(L, -2, idx); // [module, exts]
		}
		lua_pop(L, 1); // [module]

		return 1;
	}

	static int lua_getBlueprints(lua_State* L) {
		GameScene* game = getClosureScene(L);
		if (!game) return 0;

		lua_createtable(L, game->m_blueprints.size(), 0); // [bps]
		for (i32 i = 0; i < game->m_blueprints.size(); ++i) {
			const Blueprint& bp = game->m_blueprints[i];
			lua_newtable(L); // [bps, bp]

			#define EXP(T) LuaWrapper::setField(L, -1, #T, bp.T);
			EXP(type);
			EXP(label);
			EXP(prefab);
			EXP(desc);
			EXP(power_cons);
			EXP(power_prod);
			EXP(heat_cons);
			EXP(heat_prod);
			EXP(water_cons);
			EXP(water_prod);
			EXP(food_cons);
			EXP(food_prod);
			EXP(air_cons);
			EXP(air_prod);
			EXP(volume);
			EXP(material_cost);
			EXP(build_time);
			
			#undef EXP
			lua_rawseti(L, -2, i + 1);
		}
		return 1;
	}

	static int lua_signal(lua_State* L) {
		const char* signal = LuaWrapper::checkArg<const char*>(L, 1);
		GameScene* game = getClosureScene(L);
		if (!game) return 0;
		if (equalStrings(signal, "close_module_ui")) game->m_selected_module = nullptr;
		return 0;
	}
	static int lua_getStationStats(lua_State* L) {
		GameScene* game = getClosureScene(L);
		if (!game) return 0;

		lua_newtable(L);
		const Stats& stats = game->m_station.stats;
		LuaWrapper::setField(L, -1, "power_cons", stats.consumption.power);
		LuaWrapper::setField(L, -1, "power_prod", stats.production.power);
		LuaWrapper::setField(L, -1, "heat_cons", stats.consumption.heat);
		LuaWrapper::setField(L, -1, "heat_prod", stats.production.heat);
		LuaWrapper::setField(L, -1, "water_cons", stats.consumption.water);
		LuaWrapper::setField(L, -1, "water_prod", stats.production.water);
		LuaWrapper::setField(L, -1, "food_cons", stats.consumption.food);
		LuaWrapper::setField(L, -1, "food_prod", stats.production.food);
		LuaWrapper::setField(L, -1, "air_cons", stats.consumption.air);
		LuaWrapper::setField(L, -1, "air_prod", stats.production.air);
		LuaWrapper::setField(L, -1, "fuel_cons", stats.consumption.fuel);
		
		LuaWrapper::setField(L, -1, "water_stored", stats.stored.water);
		LuaWrapper::setField(L, -1, "food_stored", stats.stored.food);
		LuaWrapper::setField(L, -1, "fuel_stored", stats.stored.fuel);
		LuaWrapper::setField(L, -1, "materials_stored", stats.stored.materials);

		LuaWrapper::setField(L, -1, "water_space", stats.storage_space.water);
		LuaWrapper::setField(L, -1, "food_space", stats.storage_space.food);
		LuaWrapper::setField(L, -1, "fuel_space", stats.storage_space.fuel);
		LuaWrapper::setField(L, -1, "materials_space", stats.storage_space.materials);
		
		LuaWrapper::setField(L, -1, "efficiency", stats.efficiency);
		return 1;
	}

	IPlugin& getPlugin() const override { return m_game; }
	struct Universe& getUniverse() override { return m_universe; }

	void serialize(OutputMemoryStream& serializer) override {}
	void deserialize(InputMemoryStream& serialize, const EntityMap& entity_map, i32 version) override {}
	void clear() override {}
	
	EntityRef findByName(EntityRef parent, const char* first, const char* second) {
		const EntityRef tmp = (EntityRef)m_universe.findByName(parent, first);
		return (EntityRef)m_universe.findByName(tmp, second);
	}

	void initGUI() {
		GUIScene* scene = (GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
		scene->mousedButtonUnhandled().bind<&GameScene::onMouseButton>(this);

		((GUISystem&)scene->getPlugin()).enableCursor(true);
		
		const EntityPtr gui = m_universe.findByName(INVALID_ENTITY, "gui");
		scene->enableRect(*m_universe.findByName(gui, "moduleui"), false);
	}

	void startGame() override {
		m_time_multiplier = 1;
		m_angle = PI * 0.5f;
		m_ref_point = (EntityRef)m_universe.findByName(INVALID_ENTITY, "ref_point");
		m_camera = (EntityRef)m_universe.findByName(m_ref_point, "camera");
		m_hud = (EntityRef)m_universe.findByName(m_universe.findByName(INVALID_ENTITY, "gui"), "hud");
		
		Module* m = addModule(*m_game.m_assets.module_2);
		m_universe.setRotation(m->entity, Quat::vec3ToVec3(Vec3(0, 1, 0), Vec3(0, 0, 1)));
		m->build_progress = 1;
		
		const EntityPtr pin_e = m_universe.findByName(m->entity, "ext_0");
		addExtension(*m, "solar_panel", pin_e)->build_progress = 0;
		addExtension(*m, "air_recycler", INVALID_ENTITY)->build_progress = 1;
		addExtension(*m, "toilet", INVALID_ENTITY)->build_progress = 1;
		addExtension(*m, "sleeping_quarter", INVALID_ENTITY)->build_progress = 1;
		CrewMember& c0 = m_station.crew.emplace();
		CrewMember& c1 = m_station.crew.emplace();
		c0.id = ++m_id_generator;
		c0.name = "Donald Trump";
		c1.id = ++m_id_generator;
		c1.name = "Alber Einstein";

		m_station.stats.stored.water = 300;
		m_station.stats.stored.food = 450'000;
		m_station.stats.stored.fuel = 700;
		m_station.stats.stored.materials = 15300;

		initGUI();
		m_is_game_started = true;
	}

	void stopGame() override {
		// TODO clean station
		m_is_game_started = false;
		GUIScene* scene = (GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
		scene->mousedButtonUnhandled().unbind<&GameScene::onMouseButton>(this);
	}

	void destroyChildren(EntityRef e) {
		EntityPtr ch = m_universe.getFirstChild(e);
		while (ch.isValid()) {
			const EntityRef child = (EntityRef)ch;
			const EntityPtr next = m_universe.getNextSibling(child);
			destroyChildren(child);
			m_universe.destroyEntity(child);
			ch = next;
		}
	}

	EntityPtr getEntity(const char* parent, const char* child) const {
		const EntityPtr e = m_universe.findByName(INVALID_ENTITY, parent);
		if (!e.isValid()) return INVALID_ENTITY;

		return m_universe.findByName(*e, child);
	}

	void selectModule(Module& m) {
		m_selected_module = &m;
		getGUIScene().enableRect(*getEntity("gui", "moduleui"), true);
	}

	void selectModule(EntityRef e) {
		for (Module* m : m_station.modules) {
			if (m->entity == e) {
				selectModule(*m);
				return;
			}

			for (const Extension* ext : m->extensions) {
				if (ext->entity == e) {
					selectModule(*m);
					return;
				}
			}
		}
	}
	
	Transform getNeighbourTransform(EntityRef hatch_a, EntityRef hatch_b, EntityRef module_b) const {
		 Transform hatch_a_tr = m_universe.getTransform(hatch_a);
		const Transform hatch_b_tr = m_universe.getTransform(hatch_b);
		const Transform module_b_tr = m_universe.getTransform(module_b);

		hatch_a_tr.rot = hatch_a_tr.rot * Quat(Vec3(0, 1, 0), PI);

		const Transform rel = hatch_b_tr.inverted() * module_b_tr;
		Transform res = hatch_a_tr * rel;
		res.rot = normalize(res.rot);
		return res;
	}

	Transform getPinnedTransform(EntityRef hatch_a, EntityRef hatch_b, EntityRef module_b) const {
		 Transform hatch_a_tr = m_universe.getTransform(hatch_a);
		const Transform hatch_b_tr = m_universe.getTransform(hatch_b);
		const Transform module_b_tr = m_universe.getTransform(module_b);

		const Transform rel = hatch_b_tr.inverted() * module_b_tr;
		Transform res = hatch_a_tr * rel;
		res.rot = normalize(res.rot);
		return res;
	}

	void onMouseButton(bool down, int x, int y) {
		PROFILE_FUNCTION();
		const Viewport& vp = getRenderScene().getCameraViewport(m_camera);
		DVec3 origin;
		Vec3 dir;
		vp.getRay(Vec2((float)x, (float)y), origin, dir);
		const Transform ref_tr = m_universe.getTransform(m_ref_point);
		const Vec3 N = ref_tr.rot.rotate(Vec3(0, 0, 1));

		if (m_build_preview.isValid()) {
			/*float t;
			if (getRayPlaneIntersecion(origin.toFloat(), dir, ref_tr.pos.toFloat(), N, t)) {
				const DVec3 p = origin + dir * t;
				if (m_build_ext_type != Extension::Type::NONE) {
					const Pin pin = getClosestPin(p, 5, "ext_");
					if (pin.module) {
						Extension* ext = addExtension(*pin.module, m_build_ext_type, pin.pin);
						const Transform tr = getPinnedTransform((EntityRef)pin.pin, (EntityRef)m_build_preview, (EntityRef)ext->entity);
						m_universe.setTransform((EntityRef)ext->entity, tr);
					}
				}
				else {
					const Pin pin = getClosestPin(p, 5, "hatch_");
					if (pin.module) {
						Module* m = addModule(*m_build_prefab);
						const EntityRef hatch_b = (EntityRef)m_universe.findByName(m->entity, "hatch_0");
						const Transform tr = getNeighbourTransform((EntityRef)pin.pin, hatch_b, m->entity);
						m_universe.setTransform(m->entity, tr);
					}
				}
			}
			destroyChildren((EntityRef)m_build_preview);
			m_universe.destroyEntity((EntityRef)m_build_preview);
			m_build_preview = INVALID_ENTITY;*/
			ASSERT(false);
		}

		const RayCastModelHit hit = getRenderScene().castRay(origin, dir, INVALID_ENTITY);
		if (hit.is_hit) {
			selectModule((EntityRef)hit.entity);
		}
	}
	
	GUIScene& getGUIScene() {
		return *(GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
	}

	RenderScene& getRenderScene() {
		return *(RenderScene*)m_universe.getScene(MODEL_INSTANCE_TYPE);
	}

	LuaScriptScene& getLuaScene() {
		return *(LuaScriptScene*)m_universe.getScene(LUA_SCRIPT_TYPE);
	}

	Module* addModule(PrefabResource& prefab) {
		Module* m = LUMIX_NEW(m_allocator, Module)(m_allocator);
		m->id = ++m_id_generator;
		EntityMap entity_map(m_allocator);
		const bool created = m_game.m_engine.instantiatePrefab(m_universe, prefab, {0, 0, 0}, Quat::IDENTITY, 1.f, entity_map);
		m->entity = (EntityRef)entity_map.m_map[0];
		m_universe.setParent(m_ref_point, m->entity);
		m_universe.setLocalPosition(m->entity, {0, 0, 0});
		m_station.modules.push(m);
		return m;
	}

	Extension* addExtension(Module& module, const char* blueprint, EntityPtr pin_e) {
		const BlueprintHandle bp = m_blueprints.find([blueprint](const Blueprint& bp){ return equalStrings(bp.type, blueprint); });
		ASSERT(bp != -1);

		Extension* ext = LUMIX_NEW(m_allocator, Extension);
		ext->id = ++m_id_generator;

		if (m_blueprints[bp].prefab) {
			EntityMap entity_map(m_allocator);
			bool res = m_game.m_engine.instantiatePrefab(m_universe, *m_blueprints[bp].prefab, {0, 0, 0}, Quat::IDENTITY, 1.f, entity_map);
			ASSERT(res);
			const EntityRef e = (EntityRef)entity_map.m_map[0];
			ext->entity = e;
			m_universe.setParent(pin_e, e);
			m_universe.setLocalTransform(e, Transform::IDENTITY);
		}

		ext->blueprint = bp;
		module.extensions.push(ext);
		return ext;
	}

	void computeStats(float time_delta) {
		Stats& stats = m_station.stats;
		stats.volume = 0;
		stats.production = {};
		stats.consumption = {};
		stats.storage_space = {};
		stats.storage_space.materials = 15000;

		for (const Module* m : m_station.modules) {
			if (m->build_progress < 1) continue;
			stats.consumption.power += 7; // consumed by necessary module electronics
			for (Extension* ext : m->extensions) {
				if (ext->build_progress < 1) continue;

				const Blueprint& bp = m_blueprints[ext->blueprint];
				stats.production.power += bp.power_prod;
				stats.consumption.power += bp.power_cons;
			}
		}

		const float efficiency = clamp(stats.production.power / stats.consumption.power, 0.f, 1.f);
		stats.efficiency = efficiency;

		for (const Module* m : m_station.modules) {
			if (m->build_progress < 1) continue;
			stats.volume += 40; // usable volume in m3
			stats.consumption.heat += 10; // IR emission from the module itself
			stats.production.heat += 5 * efficiency; // produced by necessary module electronics
			stats.storage_space.food += 500000;
			stats.storage_space.water += 200;
			stats.storage_space.fuel += 1000;
			stats.storage_space.materials += 1000;
			stats.consumption.fuel += 0.1f;

			for (Extension* ext : m->extensions) {
				if (ext->build_progress < 1) continue;
				const Blueprint& bp = m_blueprints[ext->blueprint];
				
				stats.production.air += bp.air_prod * efficiency;
				stats.production.food += bp.food_prod * efficiency;
				stats.production.heat += bp.heat_prod * efficiency;
				stats.production.water += bp.water_prod * efficiency;

				stats.consumption.air += bp.air_cons * efficiency;
				stats.consumption.food += bp.food_cons* efficiency;
				stats.consumption.heat += bp.heat_cons* efficiency;
				stats.consumption.water += bp.water_cons* efficiency;
			}
		}

		for (CrewMember& c : m_station.crew) {
			stats.production.heat += 100;
			stats.consumption.air += 450; 
			stats.consumption.water += 4.5;
			stats.consumption.food += 2700;
		}


		stats.stored.fuel -= time_delta * stats.consumption.fuel;
		stats.stored.food += time_delta * (stats.production.food - stats.consumption.food);
		stats.stored.water += time_delta * (stats.production.water - stats.consumption.water);
		stats.stored.food = clamp(stats.stored.food, 0.f, stats.storage_space.food);
		stats.stored.water = clamp(0.f, stats.stored.water, stats.storage_space.water);
		stats.stored.fuel = clamp(0.f, stats.stored.fuel, stats.storage_space.fuel);
		stats.stored.materials = clamp(0.f, stats.stored.materials, stats.storage_space.materials);
	}

	Module* getModule(EntityRef e) {
		for (Module* m : m_station.modules) {
			if (m->entity == e) return m;
		}
		return nullptr;
	}

	void updateCamera(float time_delta) {
		static bool is_rmb_down = false;
		static bool is_forward = false;
		static bool is_backward = false;
		static bool is_left = false;
		static bool is_right = false;
		static bool is_fast = false;
		static bool is_q = false;
		static bool is_e = false;

		Quat rot = m_universe.getRotation(m_camera);
		const Vec3 up = rot.rotate(Vec3(0, 1, 0));
		const Vec3 side = rot.rotate(Vec3(1, 0, 0));

		const InputSystem& input = m_game.m_engine.getInputSystem();
		const i32 count = input.getEventsCount();
		const InputSystem::Event* events = input.getEvents();
		for (i32 i = 0; i < count; ++i) {
			const InputSystem::Event& e = events[i];
			switch (e.type) {
				case InputSystem::Event::BUTTON:
					if (e.device->type == InputSystem::Device::MOUSE) {
						if (e.data.button.key_id == 1) {
							is_rmb_down = e.data.button.down;
							((GUISystem&)getGUIScene().getPlugin()).enableCursor(!is_rmb_down);

						}
					}
					else {
						switch (e.data.button.key_id) {
							case 'W': is_forward = e.data.button.down; break;
							case 'S': is_backward = e.data.button.down; break;
							case 'A': is_left = e.data.button.down; break;
							case 'D': is_right = e.data.button.down; break;
							case 'Q': is_q = e.data.button.down; break;
							case 'E': is_e = e.data.button.down; break;
							case (u32)os::Keycode::SHIFT: is_fast = e.data.button.down; break;
						}
					}
					break;
				case InputSystem::Event::AXIS:
					if (is_rmb_down) {
						const Quat drot = Quat(up, -e.data.axis.x * 0.006f);
						const Quat drotx = Quat(side, -e.data.axis.y * 0.006f);
						rot = normalize(drotx * drot * rot);
						m_universe.setRotation(m_camera, rot);
					}
					break;
			}
		}

		Vec3 move(0);
		if (is_forward) move += Vec3(0, 0, -1);
		if (is_backward) move += Vec3(0, 0, 1);
		if (is_left) move += Vec3(-1, 0, 0);
		if (is_right) move += Vec3(1, 0, 0);
		if (squaredLength(move) > 0.1f) {
			move = rot.rotate(move);
			DVec3 p = m_universe.getPosition(m_camera);
			p += move * time_delta * (is_fast ? 100.f : 30.f);
			m_universe.setPosition(m_camera, p);
		}
		if (is_q || is_e) {
			const Quat drot = Quat(cross(up, side), is_e ? time_delta : -time_delta);
			m_universe.setRotation(m_camera, normalize(drot * rot));
		}
	}
	
	void beforeReload(OutputMemoryStream& blob) override {
		blob.write(m_is_game_started);
		blob.write(m_time_multiplier);
		blob.write(m_angle);
		blob.write(m_ref_point);
		blob.write(m_camera);
		blob.write(m_hud);
		blob.write(m_station.stats);
		blob.writeArray(m_station.crew);
		blob.write(m_station.modules.size());
		for (Module* m : m_station.modules) {
			m->serialize(blob);
		}
		
		GUIScene* gui_scene = (GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
		gui_scene->mousedButtonUnhandled().unbind<&GameScene::onMouseButton>(this);
	}
	
	void afterReload(InputMemoryStream& blob) override {
		blob.read(m_is_game_started);
		blob.read(m_time_multiplier);
		blob.read(m_angle);
		blob.read(m_ref_point);
		blob.read(m_camera);
		blob.read(m_hud);
		blob.read(m_station.stats);
		blob.readArray(&m_station.crew);
		const i32 size = blob.read<i32>();
		m_station.modules.resize(size);
		for (Module*& m : m_station.modules) {
			m = LUMIX_NEW(m_allocator, Module)(m_allocator);
			m->deserialize(blob, m_allocator);
		}
		
		initGUI();
	}

	void setText(EntityRef parent, const char* child, const char* format, u32 value) {
		char buf[64];
		sprintf_s(buf, format, value);
		const EntityPtr e = m_universe.findByName(parent, child);
		ASSERT(e.isValid());
		getGUIScene().setText(*e, buf);
	}

	void updateHUD() {
		setText(m_hud, "air", "%d l/h", u32(m_station.stats.production.air + m_station.stats.consumption.air));
		setText(m_hud, "water", "%d l/day", u32(m_station.stats.production.water + m_station.stats.consumption.water));
		setText(m_hud, "food", "%d kcal/day", u32(m_station.stats.production.food + m_station.stats.consumption.food));
		setText(m_hud, "power", "%d kW", u32(m_station.stats.production.power + m_station.stats.consumption.power));
		setText(m_hud, "heat", "%d kJ/s", u32(m_station.stats.production.heat + m_station.stats.consumption.heat));
	}

	void update(float time_delta, bool paused) override {
		// TODO
		// game speed
		// searching for resource & crew
		// crew
		// research
		if (paused) return;
		if (!m_is_game_started) return;

		m_angle = fmodf(m_angle + m_time_multiplier * time_delta * 0.2f, PI * 2);
		const float R = 6378e3 + 400e3;
		const DVec3 ref_point_pos = {cosf(m_angle) * R, 0, sinf(m_angle) * R};
		m_universe.setPosition(m_ref_point, ref_point_pos);
		m_universe.setRotation(m_ref_point, Quat({0, 1, 0}, -m_angle + PI * 0.5f));

		updateCamera(time_delta);
		updateHUD();

		for (CrewMember& c : m_station.crew) {
			if (c.state == CrewMember::BUILDING) {
				for (Module* m : m_station.modules) {
					if (m->id == c.subject) {
						m->build_progress += time_delta * 0.01f * m_time_multiplier;
						if (m->build_progress >= 1) {
							m->build_progress  = 1;
							c.state = CrewMember::IDLE;
						}
						break;
					}
					for (Extension* ext : m->extensions) {
						if (ext->id == c.subject) {
							ext->build_progress += time_delta * 0.05f * m_time_multiplier;
							if (ext->build_progress >= 1) {
								ext->build_progress  = 1;
								c.state = CrewMember::IDLE;
								c.subject = -1;
							}
							break;
						}
					}
				}
			}
		}

		computeStats(time_delta * m_time_multiplier);
		updateBuildPreview();
	}

	struct Pin {
		Module* module;
		EntityPtr pin;
	}; 

	Pin getClosestPin(const DVec3& p, float max_dist, const char* prefix) {
		EntityPtr closest_pin = INVALID_ENTITY;
		Module* closest_module = nullptr;
		float pin_dist = FLT_MAX;
		for (Module* m : m_station.modules) {
			if (m->build_progress < 1) continue;
			for (EntityPtr ch = m_universe.getFirstChild(m->entity); ch.isValid(); ch = m_universe.getNextSibling((EntityRef)ch)) {
				EntityRef child = (EntityRef)ch;
				const char* name = m_universe.getEntityName(child);
				if (startsWith(name, prefix)) {
					const double d = squaredLength(p - m_universe.getPosition(child));
					if (d < pin_dist) {
						pin_dist = (float)d;
						closest_pin = child;
						closest_module = m;
					}
				}
			}
		}
		if (pin_dist < max_dist * max_dist) {
			return { closest_module, closest_pin };
		}
		return {};
	}

	void updateBuildPreview() {
		if (!m_build_preview.isValid()) return;

		ASSERT(false);/*
		const IVec2 mp = getGUIScene().getCursorPosition();

		const Viewport& vp = getRenderScene().getCameraViewport(m_camera);
		DVec3 origin;
		Vec3 dir;
		vp.getRay(Vec2((float)mp.x, (float)mp.y), origin, dir);
		const Transform ref_tr = m_universe.getTransform(m_ref_point);
		const Vec3 N = ref_tr.rot.rotate(Vec3(0, 0, 1));

		float t;

		if (getRayPlaneIntersecion(origin.toFloat(), dir, ref_tr.pos.toFloat(), N, t)) {
			const DVec3 p = origin + dir * t;
			const bool is_ext = m_build_ext_type != Extension::Type::NONE;
			const Pin pin = getClosestPin(p, 5, is_ext ? "ext_" : "hatch_");
			if (pin.module) {
				if (is_ext) {
					const Transform tr = getPinnedTransform((EntityRef)pin.pin, (EntityRef)m_build_preview, (EntityRef)m_build_preview);
					m_universe.setTransform((EntityRef)m_build_preview, tr);
					return;
				}
				
				const EntityRef hatch_b = (EntityRef)m_universe.findByName((EntityRef)m_build_preview, "hatch_0");				
				const Transform tr = getNeighbourTransform((EntityRef)pin.pin, hatch_b, (EntityRef)m_build_preview);
				m_universe.setTransform((EntityRef)m_build_preview, tr);
				return;
			}

			m_universe.setPosition((EntityRef)m_build_preview, p);
		}*/
	}

	bool m_is_game_started = false;
	u32 m_time_multiplier = 0;
	IAllocator& m_allocator;
	Game& m_game;
	Universe& m_universe;
	SpaceStation m_station;
	EntityRef m_camera;
	EntityRef m_hud;
	EntityRef m_ref_point;
	float m_angle = 0;
	
	EntityPtr m_build_preview = INVALID_ENTITY;
	PrefabResource* m_build_prefab = nullptr;
	//Extension::Type m_build_ext_type = Extension::Type::NONE;

	Module* m_selected_module = nullptr;
	u32 m_id_generator = 0;
	Array<Blueprint> m_blueprints;
};

void Game::createScenes(Universe& universe) {
	IAllocator& allocator = m_engine.getAllocator();
	UniquePtr<GameScene> scene = UniquePtr<GameScene>::create(allocator, *this, universe);
	universe.addScene(scene.move());
}

LUMIX_PLUGIN_ENTRY(game_plugin) {
	return LUMIX_NEW(engine.getAllocator(), Game)(engine);
}

