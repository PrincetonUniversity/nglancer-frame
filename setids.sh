#! /bin/env bash

## retrieve uid and gid for user

export NB_UID=$(id -u $USER)
export NB_GID=$(id -g $USER)

echo "NB_UID set to $NB_UID"
echo "NB_GID set to $NB_GID"
