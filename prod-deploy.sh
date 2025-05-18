#!/bin/bash

docker stop edu-track-prod || true
docker rm edu-track-prod || true


docker rmi edu-track-prod:latest

docker compose -p edu-track-prod -f "./docker-compose/docker-compose-dev.yml" down
docker compose -p edu-track-prod -f "./docker-compose/docker-compose-dev.yml" up -d --build

exit
