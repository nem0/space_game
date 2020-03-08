#include "engine/engine.h"
#include "engine/plugin.h"
#include "engine/reflection.h"
#include "engine/resource_manager.h"
#include "engine/universe.h"
#include "gui/gui_scene.h"
#include "gui/gui_system.h"
#include "renderer/model.h"
#include "renderer/render_scene.h"

using namespace Lumix;

static const ComponentType MODEL_INSTANCE_TYPE = Reflection::getComponentType("model_instance");
static const ComponentType GUI_BUTTON_TYPE = Reflection::getComponentType("gui_button");

struct Extension {
	enum class Type {
		SOLAR_PANEL,
		AIR_RECYCLER
	};
	EntityPtr entity;
	Type type;
};

struct CrewMember {
};

struct Module {
	Module(IAllocator& allocator) : extensions(allocator) {}

	EntityRef entity;
	Array<Extension*> extensions;
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
	Path module;
	Path solar_panel;
};

struct Game : IPlugin {
	Game(Engine& engine) 
		: m_engine(engine) 
	{
		initAssets();
	}

	void initAssets() {
		m_assets.module = "models/module.fbx";
		m_assets.solar_panel = "models/solar_panel.fbx";
	}

	void createScenes(Universe& universe) override;
	void destroyScene(IScene* scene) override { LUMIX_DELETE(m_engine.getAllocator(), scene); }

	const char* getName() const override { return "game"; }

	Assets m_assets;
	Engine& m_engine;
};

struct GUI {
	EntityRef station_stats_panel;
	EntityRef actions_panel;
	EntityRef power_stat;
	EntityRef heat_stat;
	EntityRef air_stat;
	EntityRef food_stat;
	EntityRef water_stat;

	EntityRef station_stats_icon;
	EntityRef actions_icon;
};

struct GameScene : IScene {
	GameScene(Game& game, Universe& universe) 
		: m_game(game)
		, m_universe(universe)
		, m_station(game.m_engine.getAllocator())
		, m_allocator(game.m_engine.getAllocator())
	{}

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
		const EntityRef gui = (EntityRef)m_universe.findByName(INVALID_ENTITY, "gui");
		
		m_gui.station_stats_panel = (EntityRef)m_universe.findByName(gui, "ship_stats_panel");
		const EntityRef vals = (EntityRef)m_universe.findByName(m_gui.station_stats_panel, "values");
		m_gui.power_stat = findByName(vals, "power", "value");
		m_gui.heat_stat = findByName(vals, "heat", "value");
		m_gui.air_stat = findByName(vals, "air", "value");
		m_gui.food_stat = findByName(vals, "food", "value");
		m_gui.water_stat = findByName(vals, "water", "value");
		
		m_gui.actions_panel = (EntityRef)m_universe.findByName(gui, "actions_panel");


		const EntityRef icons = (EntityRef)m_universe.findByName(gui, "icons");
		m_gui.station_stats_icon = (EntityRef)m_universe.findByName(icons, "station");
		m_gui.actions_icon = (EntityRef)m_universe.findByName(icons, "actions");

		GUIScene* scene = (GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
		scene->buttonClicked().bind<&GameScene::onButtonClicked>(this);

		((GUISystem&)scene->getPlugin()).enableCursor(true);
	}

	void startGame() override {
		Module* m = addModule();
		addExtension(*m, Extension::Type::SOLAR_PANEL);
		addExtension(*m, Extension::Type::AIR_RECYCLER);
		m_station.crew.emplace();
		initGUI();
		m_is_game_started = true;
	}

	void stopGame() override {
		// TODO clean station
		m_is_game_started = false;
		GUIScene* scene = (GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
		scene->buttonClicked().unbind<&GameScene::onButtonClicked>(this);
	}

	void onButtonClicked(EntityRef button) {
		GUIScene& scene = getGUIScene();
		if (button == m_gui.station_stats_icon) {
			const bool enabled = scene.isRectEnabled(m_gui.station_stats_panel);
			scene.enableRect(m_gui.station_stats_panel, !enabled);
			scene.enableRect(m_gui.actions_panel, false);
		}
		if (button == m_gui.actions_icon) {
			const bool enabled = scene.isRectEnabled(m_gui.actions_panel);
			scene.enableRect(m_gui.actions_panel, !enabled);
			scene.enableRect(m_gui.station_stats_panel, false);
		}
	}

	GUIScene& getGUIScene() {
		return *(GUIScene*)m_universe.getScene(GUI_BUTTON_TYPE);
	}

	RenderScene& getRenderScene() {
		return *(RenderScene*)m_universe.getScene(MODEL_INSTANCE_TYPE);
	}

	Module* addModule() {
		Module* m = LUMIX_NEW(m_allocator, Module)(m_allocator);
		m->entity = m_universe.createEntity({0, 0, 0}, {0, 0, 0, 1});
		m_universe.createComponent(MODEL_INSTANCE_TYPE, m->entity);
		const Path& p = m_game.m_assets.module;
		getRenderScene().setModelInstancePath(m->entity, p);
		m_station.modules.push(m);
		return m;
	}

	void addExtension(Module& module, Extension::Type type) {
		Extension* e = LUMIX_NEW(m_allocator, Extension);
		e->entity = m_universe.createEntity({0, 0, 0}, {0, 0, 0, 1});
		m_universe.createComponent(MODEL_INSTANCE_TYPE, (EntityRef)e->entity);
		switch (type) {
			case Extension::Type::SOLAR_PANEL : getRenderScene().setModelInstancePath((EntityRef)e->entity, m_game.m_assets.solar_panel); break;
			case Extension::Type::AIR_RECYCLER : break;
			default: ASSERT(false); break;
		}
		e->type = type;
		module.extensions.push(e);
	}

	void computeStats(float time_delta) {
		Stats& stats = m_station.stats;
		stats.volume = 0;
		stats.production = {};
		stats.consumption = {};

		for (const Module* m : m_station.modules) {
			stats.volume += 100;
			stats.consumption.heat += 10; // IR emission from the module itself
			stats.production.heat += 5; // produced by necessary module electronics
			stats.consumption.power += 7; // consumed by necessary module electronics
			for (Extension* ext : m->extensions) {
				switch (ext->type) {
					case Extension::Type::AIR_RECYCLER:
						stats.production.air = 2000;
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
			stats.consumption.water = 2;
			stats.consumption.food = 2700;
		}
	}

	void updateGUI() {
		const Stats& stats = m_station.stats;
		GUIScene& scene = getGUIScene();
		StaticString<256> tmp;
		
		tmp << int(stats.production.power - stats.consumption.power) << " kW (" 
			<< int(stats.production.power) << " - " << int(stats.consumption.power) << ")";
		scene.setText(m_gui.power_stat, tmp);
	
		tmp = "";
		tmp << int(stats.production.heat - stats.consumption.heat) << " W (" 
			<< int(stats.production.heat) << " - " << int(stats.consumption.heat) << ")";
		scene.setText(m_gui.heat_stat, tmp);

		tmp = "";
		tmp << int(stats.production.air - stats.consumption.air) << " l/h (" 
			<< int(stats.production.air) << " - " << int(stats.consumption.air) << ")";
		scene.setText(m_gui.air_stat, tmp);

		tmp = "";
		tmp << int(stats.production.food - stats.consumption.food) << " kcal/day (" 
			<< int(stats.production.food) << " - " << int(stats.consumption.food) << ")";
		scene.setText(m_gui.food_stat, tmp);

		tmp = "";
		tmp << int(stats.production.water - stats.consumption.water) << " l/day (" 
			<< int(stats.production.water) << " - " << int(stats.consumption.water) << ")";
		scene.setText(m_gui.water_stat, tmp);
	}

	void update(float time_delta, bool paused) override {
		if (paused) return;
		if (!m_is_game_started) return;

		computeStats(time_delta);
		updateGUI();
	}

	bool m_is_game_started = false;
	IAllocator& m_allocator;
	Game& m_game;
	Universe& m_universe;
	SpaceStation m_station;
	GUI m_gui;
};

void Game::createScenes(Universe& universe) {
	GameScene* scene = LUMIX_NEW(m_engine.getAllocator(), GameScene)(*this, universe); 
	universe.addScene(scene);
}

LUMIX_PLUGIN_ENTRY(game_plugin) {
	return LUMIX_NEW(engine.getAllocator(), Game)(engine);
}

