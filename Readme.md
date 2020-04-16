# Multiplayer Map Pacman

![Python application](https://github.com/hegerdes/RealWorldPacman/workflows/Python%20application/badge.svg)

## What this is

This is a multiplayer version of Pacman playing in the real world. This is just like the thing google did for Pacmans annaveryers. But this is multiplayer!

![Alt Text](https://github.com/hegerdes/RealWorldPacman/blob/master/docs/examples/pac1.gif?raw=true)


You have to get an deliver packages.

## Install and Lunch

Download the repro and install the requirements.

You need the following libs to play:

* numpy
* osmium
* osmread
* pandas
* pygame
* pyproj
* PodSixNet
* IPy
* networkx
* configparser
* pygame-Menu
* requests
* networkx
* matplotlib

You can type `pip install -r requirments.txt`  to install all needed libs.
## Maps

There are some maps alrady generated. You also can genarate new maps. All you need is a OpenStreetMap (OSM) File and then zip it.

Default Maps:

* Osnabrück - small
* Osnabrück - big
* Tokyo

## Ghosts

The Gohst beave like real people. We used the Tool Bonnmotion to generate the movementmodels MSLAW and RandomStreet.

To generate own Ghost-traces you need to download Bonnotion 3.0.2 have a OSM.pbf File of your location and need a OpenStreetmapRoutingMachine (OSRM). The is a Dockerfile in MapGenaratorTools

## AI

There is to possibility controll pacman by a "AI" or to play against it. If you want ou use this you habe to connect to a OSRM. Default URL:localhost:5000

## RALANS

By default the packages are circles. Ther will be the option to use a real-world range based shape insted of the circles. This is EXPERIMENTAL. You need to have the Date for the area (by know only Osnabrück and Tokyo exists). It alsow slows down the game alot. Hopefully this will be fixed
