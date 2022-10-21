pushd ..\LumixEngine\projects
genie.exe --dynamic-plugins --debug-args="-plugin C:\projects\space_game\tmp\vs2022\bin\Debug\game.dll" vs2022
popd
genie.exe vs2022
pause