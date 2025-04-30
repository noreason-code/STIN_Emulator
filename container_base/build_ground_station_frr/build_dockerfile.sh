#!/bin/bash -er
docker build -t ground_station_frr:latest .
echo "y" | docker image prune
echo "y" | docker builder prune