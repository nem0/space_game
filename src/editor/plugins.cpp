#include "editor/studio_app.h"

using namespace Lumix;

struct Module {

};

struct SpaceStation {
    Array<Module*> modules;
};


LUMIX_STUDIO_ENTRY(game_plugin) { return nullptr; }