#include "engine/crc32.h"
#include "engine/engine.h"
#include "engine/input_system.h"
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

using namespace Lumix;

static const ComponentType MODEL_INSTANCE_TYPE = Reflection::getComponentType("model_instance");
static const ComponentType LUA_SCRIPT_TYPE = Reflection::getComponentType("lua_script");
static const ComponentType GUI_BUTTON_TYPE = Reflection::getComponentType("gui_button");

struct Extension {
	enum class Type {
		SOLAR_PANEL,
		AIR_RECYCLER,
		TOILET,
		SLEEPING_QUARTER,
		WATER_RECYCLER,
		HYDROPONICS,

		NONE
	};
	u32 id;
	EntityPtr entity;
	Type type;
	float build_progress = 0.f;
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
	} consumption;
	float volume = 0;
	float stored_power = 0;
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
		// TODO this does not work if the asset is not precompiled at this time, since asset compiler is not hooked at this point
		ResourceManagerHub& rm = m_engine.getResourceManager();
		m_assets.module_2 = rm.load<PrefabResource>(Path("prefabs/module_2.fab"));
		m_assets.module_3 = rm.load<PrefabResource>(Path("prefabs/module_3.fab"));
		m_assets.module_4 = rm.load<PrefabResource>(Path("prefabs/module_4.fab"));
		m_assets.solar_panel = rm.load<PrefabResource>(Path("prefabs/solar_panel.fab"));
	}

	~Game() {
		m_assets.module_2->getResourceManager().unload(*m_assets.module_2);
		m_assets.module_3->getResourceManager().unload(*m_assets.module_3);
		m_assets.module_4->getResourceManager().unload(*m_assets.module_4);
		m_assets.solar_panel->getResourceManager().unload(*m_assets.solar_panel);
	}

	void createScenes(Universe& universe) override;
	void destroyScene(IScene* scene) override { LUMIX_DELETE(m_engine.getAllocator(), scene); }

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
	{
		lua_State* L = m_game.m_engine.getState();
		LuaWrapper::createSystemClosure(L, "Game", this, "getStationStats", lua_getStationStats);
		LuaWrapper::createSystemClosure(L, "Game", this, "getModule", lua_getModule);
		LuaWrapper::createSystemClosure(L, "Game", this, "getCrew", lua_getCrew);
		LuaWrapper::createSystemClosure(L, "Game", this, "assignBuilder", lua_assignBuilder);
		LuaWrapper::createSystemClosure(L, "Game", this, "onGUIEvent", lua_onGUIEvent);
	}

	static const char* toString(Extension::Type type) {
		switch (type) {
			case Extension::Type::SOLAR_PANEL: return "solar_panel";
			case Extension::Type::AIR_RECYCLER: return "air_recycler";
			case Extension::Type::WATER_RECYCLER: return "water_recycler";
			case Extension::Type::TOILET: return "toilet";
			case Extension::Type::SLEEPING_QUARTER: return "sleeping_quarter";
			case Extension::Type::HYDROPONICS: return "hydroponics";
			default: ASSERT(false); return "unknown";
		}
	}

	static int lua_onGUIEvent(lua_State* L) {
		const char* event_name = LuaWrapper::checkArg<const char*>(L, 1);
		GameScene* game = getClosureScene(L);
		if (!game) return 0;

		game->onGUIEvent(crc32(event_name));
		return 0;
	}

	void onGUIEvent(u32 event_hash) {
		static const u32 build_module_2_event = crc32("build_module_2");
		static const u32 build_module_3_event = crc32("build_module_3");
		static const u32 build_module_4_event = crc32("build_module_4");
		static const u32 build_solar_panel_event = crc32("build_solar_panel");
		static const u32 build_water_recycler_event = crc32("build_water_recycler");
		static const u32 build_air_recycler_event = crc32("build_air_recycler");
		static const u32 build_toilet_event = crc32("build_toilet");
		static const u32 build_sleeping_quarter_event = crc32("build_sleeping_quarter");
		static const u32 build_hydroponics_event = crc32("build_hydroponics");
		if (event_hash == build_module_2_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.module_2, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.module_2;
			m_build_ext_type = Extension::Type::NONE;
			return;
		}
		if (event_hash == build_module_3_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.module_3, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.module_3;
			m_build_ext_type = Extension::Type::NONE;
			return;
		}
		if (event_hash == build_module_4_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.module_4, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.module_4;
			m_build_ext_type = Extension::Type::NONE;
			return;
		}
		if (event_hash == build_solar_panel_event) {
			ASSERT(!m_build_preview.isValid());
			EntityMap entity_map(m_allocator);
			const bool created = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.solar_panel, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
			m_build_preview = entity_map.m_map[0];
			m_build_prefab = m_game.m_assets.solar_panel;
			m_build_ext_type = Extension::Type::SOLAR_PANEL;
			return;
		}
		if (event_hash == build_water_recycler_event) {
			addExtension(*m_selected_module, Extension::Type::WATER_RECYCLER, INVALID_ENTITY);
			return;
		}
		if (event_hash == build_air_recycler_event) {
			addExtension(*m_selected_module, Extension::Type::AIR_RECYCLER, INVALID_ENTITY);
			return;
		}
		if (event_hash == build_toilet_event) {
			addExtension(*m_selected_module, Extension::Type::TOILET, INVALID_ENTITY);
			return;
		}
		if (event_hash == build_sleeping_quarter_event) {
			addExtension(*m_selected_module, Extension::Type::SLEEPING_QUARTER, INVALID_ENTITY);
			return;
		}
		if (event_hash == build_hydroponics_event) {
			addExtension(*m_selected_module, Extension::Type::HYDROPONICS, INVALID_ENTITY);
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
		LuaWrapper::setField(L, -1, "type", toString(ext.type));
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

		logError("Game") << "Invalid crewmember in assignBuilder";

		return 0;
	}

	static GameScene* getClosureScene(lua_State* L) {
		const int index = lua_upvalueindex(1);
		if (!LuaWrapper::isType<GameScene>(L, index)) {
			logError("Lua") << "Invalid Lua closure";
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
		return 1;
	}

	IPlugin& getPlugin() const override { return m_game; }
	struct Universe& getUniverse() override { return m_universe; }

	void serialize(OutputMemoryStream& serializer) override {}
	void deserialize(InputMemoryStream& serialize, const EntityMap& entity_map) override {}
	void clear() override {}
	
	EntityRef findByName(EntityRef parent, const char* first, const char* second) {
		const EntityRef tmp = (EntityRef)m_universe.findByName(parent, first);
		return (EntityRef)m_universe.findByName(tmp, second);
	}

	void initGUI() {
		GUIScene* scene = (GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
		scene->mousedButtonUnhandled().bind<&GameScene::onMouseButton>(this);

		((GUISystem&)scene->getPlugin()).enableCursor(true);
	}

	void startGame() override {
		m_angle = PI * 0.5f;
		m_ref_point = (EntityRef)m_universe.findByName(INVALID_ENTITY, "ref_point");
		m_camera = (EntityRef)m_universe.findByName(m_ref_point, "camera");
		
		Module* m = addModule(*m_game.m_assets.module_2);
		m_universe.setRotation(m->entity, Quat::vec3ToVec3(Vec3(0, 1, 0), Vec3(0, 0, 1)));
		m->build_progress = 1;
		
		const EntityPtr pin_e = m_universe.findByName(m->entity, "ext_0");
		addExtension(*m, Extension::Type::SOLAR_PANEL, pin_e)->build_progress = 0;
		addExtension(*m, Extension::Type::AIR_RECYCLER, INVALID_ENTITY)->build_progress = 1;
		addExtension(*m, Extension::Type::TOILET, INVALID_ENTITY)->build_progress = 1;
		addExtension(*m, Extension::Type::SLEEPING_QUARTER, INVALID_ENTITY)->build_progress = 1;
		CrewMember& c0 = m_station.crew.emplace();
		CrewMember& c1 = m_station.crew.emplace();
		c0.id = ++id_generator;
		c0.name = "Donald Trump";
		c1.id = ++id_generator;
		c1.name = "Alber Einstein";
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

	void selectModule(Module& m) {
		m_selected_module = &m;
		if (LuaScriptScene::IFunctionCall* call = getLuaScene().beginFunctionCall(m.entity, 0, "selected")) {
			getLuaScene().endFunctionCall();
		}
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
		res.rot.normalize();
		return res;
	}

	Transform getPinnedTransform(EntityRef hatch_a, EntityRef hatch_b, EntityRef module_b) const {
		 Transform hatch_a_tr = m_universe.getTransform(hatch_a);
		const Transform hatch_b_tr = m_universe.getTransform(hatch_b);
		const Transform module_b_tr = m_universe.getTransform(module_b);

		const Transform rel = hatch_b_tr.inverted() * module_b_tr;
		Transform res = hatch_a_tr * rel;
		res.rot.normalize();
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
			float t;
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
			m_build_preview = INVALID_ENTITY;
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
		m->id = ++id_generator;
		EntityMap entity_map(m_allocator);
		const bool created = m_game.m_engine.instantiatePrefab(m_universe, prefab, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
		m->entity = (EntityRef)entity_map.m_map[0];
		m_universe.setParent(m_ref_point, m->entity);
		m_universe.setLocalPosition(m->entity, {0, 0, 0});
		m_station.modules.push(m);
		return m;
	}

	Extension* addExtension(Module& module, Extension::Type type, EntityPtr pin_e) {
		Extension* ext = LUMIX_NEW(m_allocator, Extension);
		ext->id = ++id_generator;

		switch (type) {
			case Extension::Type::SOLAR_PANEL : {
				EntityMap entity_map(m_allocator);
				bool res = m_game.m_engine.instantiatePrefab(m_universe, *m_game.m_assets.solar_panel, {0, 0, 0}, Quat::IDENTITY, 1.f, Ref(entity_map));
				ASSERT(res);
				const EntityRef e = (EntityRef)entity_map.m_map[0];
				ext->entity = e;
				m_universe.setParent(pin_e, e);
				m_universe.setLocalTransform(e, Transform::IDENTITY);
				break;
			}
			case Extension::Type::WATER_RECYCLER : break;
			case Extension::Type::AIR_RECYCLER : break;
			case Extension::Type::TOILET : break;
			case Extension::Type::SLEEPING_QUARTER: break;
			case Extension::Type::HYDROPONICS: break;
			default: ASSERT(false); break;
		}
		ext->type = type;
		module.extensions.push(ext);
		return ext;
	}

	void computeStats(float time_delta) {
		Stats& stats = m_station.stats;
		stats.volume = 0;
		stats.production = {};
		stats.consumption = {};

		for (const Module* m : m_station.modules) {
			if (m->build_progress < 1) continue;
			stats.volume += 40; // usable volume in m3
			stats.consumption.heat += 10; // IR emission from the module itself
			stats.production.heat += 5; // produced by necessary module electronics
			stats.consumption.power += 7; // consumed by necessary module electronics
			
			for (Extension* ext : m->extensions) {
				if (ext->build_progress < 1) continue;
				switch (ext->type) {
					case Extension::Type::AIR_RECYCLER:
						stats.production.air = 2000;
						break;
					case Extension::Type::WATER_RECYCLER:
						stats.production.water = 10;
						break;
					case Extension::Type::HYDROPONICS:
						stats.production.food = 20'000;
						break;
					case Extension::Type::SOLAR_PANEL:
						stats.production.power += 120; // avg, max is 240
						break;
				}
			}
		}

		for (CrewMember& c : m_station.crew) {
			stats.production.heat += 100;
			stats.consumption.air += 450; 
			stats.consumption.water += 4.5;
			stats.consumption.food += 2700;
		}
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
						}
					}
					else {
						switch (e.data.button.key_id) {
							case 'W': is_forward = e.data.button.down; break;
							case 'S': is_backward = e.data.button.down; break;
							case 'A': is_left = e.data.button.down; break;
							case 'D': is_right = e.data.button.down; break;
							case (u32)OS::Keycode::SHIFT: is_fast = e.data.button.down; break;
						}
					}
					break;
				case InputSystem::Event::AXIS:
					if (is_rmb_down) {
						const Quat drot = Quat(up, -e.data.axis.x * 0.003f);
						const Quat drotx = Quat(side, -e.data.axis.y * 0.003f);
						m_universe.setRotation(m_camera, (drotx * drot * rot).normalized());
					}
					break;
			}
		}

		Vec3 move(0);
		if (is_forward) move += Vec3(0, 0, -1);
		if (is_backward) move += Vec3(0, 0, 1);
		if (is_left) move += Vec3(-1, 0, 0);
		if (is_right) move += Vec3(1, 0, 0);
		if (move.squaredLength() > 0.1f) {
			move = rot.rotate(move);
			DVec3 p = m_universe.getPosition(m_camera);
			p += move * time_delta * (is_fast ? 100.f : 10.f);
			m_universe.setPosition(m_camera, p);
		}
	}

	void update(float time_delta, bool paused) override {
		if (paused) return;
		if (!m_is_game_started) return;

		m_angle = fmodf(m_angle + time_delta * 0.2f, PI * 2);
		const float R = 6378e3 + 400e3;
		const DVec3 ref_point_pos = {cosf(m_angle) * R, 0, sinf(m_angle) * R};
		m_universe.setPosition(m_ref_point, ref_point_pos);
		m_universe.setRotation(m_ref_point, Quat({0, 1, 0}, -m_angle + PI * 0.5f));

		updateCamera(time_delta);

		for (CrewMember& c : m_station.crew) {
			if (c.state == CrewMember::BUILDING) {
				for (Module* m : m_station.modules) {
					if (m->id == c.subject) {
						m->build_progress += time_delta * 0.1f;
						if (m->build_progress >= 1) {
							m->build_progress  = 1;
							c.state = CrewMember::IDLE;
						}
						break;
					}
					for (Extension* ext : m->extensions) {
						if (ext->id == c.subject) {
							ext->build_progress += time_delta * 0.1f;
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

		computeStats(time_delta);
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
					const double d = (p - m_universe.getPosition(child)).squaredLength();
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
		}
	}

	bool m_is_game_started = false;
	IAllocator& m_allocator;
	Game& m_game;
	Universe& m_universe;
	SpaceStation m_station;
	EntityRef m_camera;
	EntityRef m_ref_point;
	float m_angle = 0;
	
	EntityPtr m_build_preview = INVALID_ENTITY;
	PrefabResource* m_build_prefab = nullptr;
	Extension::Type m_build_ext_type = Extension::Type::NONE;

	Module* m_selected_module = nullptr;
	u32 id_generator = 0;
};

void Game::createScenes(Universe& universe) {
	GameScene* scene = LUMIX_NEW(m_engine.getAllocator(), GameScene)(*this, universe); 
	universe.addScene(scene);
}

LUMIX_PLUGIN_ENTRY(game_plugin) {
	return LUMIX_NEW(engine.getAllocator(), Game)(engine);
}

