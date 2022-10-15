function copyPDA(config)
	configuration { config }
		prebuildcommands {
			[[if EXIST "$(SolutionDir)bin\]]..config..[[\game.pda" ( move /Y "$(SolutionDir)bin\]]..config..[[\game.pda" "$(SolutionDir)bin\]]..config..[[\game.pdb" )]],
		}
			
		postbuildcommands {
			[[move /Y "$(SolutionDir)bin\]]..config..[[\game.pdb" "$(SolutionDir)bin\]]..config..[[\game.pda"]],
		}
	configuration {}
end

dofile("../lumixengine/projects/plugin.lua")

bootstrapPlugin("game")
	files { 
		"src/**.cpp",
		"src/**.h",
		"genie.lua"
	}

	includedirs { "src", }
	defines { "BUILDING_GAME" }
	useLua()
	defaultConfigurations()

	copyPDA("Debug")
	copyPDA("RelWithDebInfo")