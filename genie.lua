project "game_plugin"
	libType()
	files { 
		"src/**.c",
		"src/**.cpp",
		"src/**.h",
		"genie.lua"
	}
	defines { "BUILDING_SPACE_GAME" }
	links { "engine" }
	useLua()
	defaultConfigurations()

linkPlugin("game_plugin")