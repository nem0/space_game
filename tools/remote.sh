#!/bin/bash
# Helpers for driving a running Lumix Studio through its remote plugin (LumixEngine/plugins/remote, http://127.0.0.1:17123/mcp).
#   source tools/remote.sh; mcp start_game '{}'; shot name   (writes screenshots/name.png, scaled to 1600 px wide, via Blender)
mcp() { curl -s -m 60 -X POST http://127.0.0.1:17123/mcp -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":$2}}"; echo; }
key() { mcp send_input "{\"type\":\"key\",\"key\":\"$1\"}" > /dev/null; }
click() { mcp send_input "{\"type\":\"mouse_button\",\"button\":\"left\",\"x\":$1,\"y\":$2}" > /dev/null; }
restart() { mcp stop_game '{}' > /dev/null; sleep 3; mcp start_game '{}' > /dev/null; sleep 6; }
shot() {
	rm -f "screenshots/$1.tga"
	mcp make_game_screenshot "{\"path\":\"screenshots/$1.tga\"}" > /dev/null
	for i in $(seq 1 40); do [ -s "screenshots/$1.tga" ] && sleep 1 && break; sleep 0.5; done
	"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --python tools/tga2png.py -- "$PWD/screenshots/$1.tga" "$PWD/screenshots/$1.png" > /dev/null 2>&1
	rm -f "screenshots/$1.tga"
}
