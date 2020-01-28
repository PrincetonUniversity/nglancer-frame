#! /bin/env bash


## this is a small script to handle setting up the user `joyvan` to have access
# to the docker socket mounted in the notebook container


# capture docker sock gid

DOCKERGID=$(stat -c '%g' /var/run/docker.sock)

echo "Docker GID: $DOCKERGID"

## create docker group in container
groupadd docker --gid $DOCKERGID

## add default user jovyan to group

usermod -a -G docker jovyan
