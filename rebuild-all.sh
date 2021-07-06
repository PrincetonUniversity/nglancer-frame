#! /bin/bash

## a simple script to remove crufty containers, assert a named docker network,
# build all dockercomposeable containers, and retag the cloudvolume and neuroglancer latest containers

#clear out junk and rebuild
docker rm -f $(docker ps -aq)

docker-compose build

## cleanup network to make sure a good fresh one exists
docker network rm nglancer

docker network create --attachable nglancer

## build cloud volume latest tag
cd ./cloudvolume

docker build -f ./cloudvolume.dockerfile -t cloudv_test:latest .

## build neuroglancer latest tag
cd ../neuroglancer

docker build -f ./neuroglancer.dockerfile -t ngdemo:latest .

## build precomputed latest tag
cd ../precomputed

docker build -f ./precomputed.dockerfile -t precomputed_test:latest .

