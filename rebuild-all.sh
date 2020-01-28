#! /bin/bash

## a simple script to remove crufty containers, assert a named docker network,
# build all dockercomposeable containers, and retag the cloudvolume and neuroglancer latest containers

#make sure all containers are stopped (note this will not capture cloud volumes launched by the notebook!!!!)
docker-compose stop

#clear out junk and rebuild
docker-compose rm -f

docker-compose build

## cleanup network to make sure a good fresh one exists
docker network rm nglancer

docker network create --attachable nglancer


## build cloud volume latest tag
cd ./cloudvolume

docker build -f ./cloudvolume.dockerfile -t cloudv:latest .

## build neuroglancer latest tag
cd ../neuroglancer

docker build -f ./neuroglancer.dockerfile -t nglancer:latest .
