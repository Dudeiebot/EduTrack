#!/bin/bash

docker stop edu-track-dev || true
docker rm edu-track-dev || true


docker rmi edu-track-dev:latest

docker compose -p edu-track-dev -f "./docker-compose/docker-compose-dev.yml" down
docker compose -p edu-track-dev -f "./docker-compose/docker-compose-dev.yml" up -d --build

exit
