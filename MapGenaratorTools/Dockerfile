FROM osrm/osrm-backend

EXPOSE 5000
RUN mkdir /data
WORKDIR /data

COPY YOUR_MAP.osm.pbf /data/map.osm.pbf
RUN osrm-extract -p /opt/car.lua /data/map.osm.pbf
RUN ls /data
RUN osrm-partition /data/map.osrm
RUN osrm-customize /data/map.osrm

CMD osrm-routed --algorithm mld /data/map.osrm
