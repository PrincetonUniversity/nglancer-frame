#! /bin/env bash

## a simple script to remove crufty containers, assert a named docker network,
# build all dockercomposeable containers, and retag the cloudvolume and neuroglancer latest containers


#make sure all containers are stopped (note this will not capture cloud volumes launched by the notebook!!!!)
docker-compose stop

#clear out junk
docker-compose rm -f

## remove named docker network that will be recreated at end of script
docker network rm
