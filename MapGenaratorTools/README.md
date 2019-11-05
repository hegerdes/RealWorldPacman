## Traces erstellen für NPC

# Konvertierung von .osm zu .osm.pbf

```
osmconvert[64|32] --out-pbf -o={FILENAME}.osm.pbf {FILENAME}.osm
```

# Docker Image erstellen

In docker/Dockerfile muss in Zeile 7 die korrekte .pbf als erstes argument
übergeben werden.

```
cd docker
docker build -t lab-osrm-server .
```

# Docker Container starten

```
docker run -p 5000:5000 [--name {CONTAINER NAME}] lab-osrm-server
```

# Trace erstellen

Unbedingt Bonnmotion Version 3.0.2 benutzen!

```
bm -f {OUTPUT} -I (mslaw.params | randstreet.params) (MSLAW | RandomStreet)
```
