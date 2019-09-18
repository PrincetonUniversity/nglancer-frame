# Neuroglancer Frame
This is a small `docker` + `docker-compose` based solution for running the [neuroglancer volumetric viewer](https://github.com/seung-lab/neuroglancer) against precomputed file sets off local filesystems. Local here is relative and will also allow usage of mounted cifs and nfs filesystems. The data is served up using the [cloud-volume tool](https://github.com/seung-lab/cloud-volume) developed by the seung lab.

## Requirements
* Docker: A modern version of [docker appropriate to the OS](https://docs.docker.com/install/#supported-platforms) needs to be installed.
* docker-compose: A recent version of [docker-compose](https://docs.docker.com/compose/install/#install-compose) must be installed as the compose file included with this package uses a relatively new format version to allow for the `.env` file support to work.

## Usage
First the images will need to be built with: `docker-compose build`; initially this will take a bit of time but should not need to be done again unless pulling new updates from this repo. After that simply set the variable `CVDATA` to the root of a dataset, this must be a full path to the folder, and launch the containers with `docker-compose up`. This will start a server running on port `8080` on your local machine that will present the selected dataset inside neuroglancer.

On a linux desktop this would look like:
```
docker-compose build
export CVDATA=/mnt/dataset # change path to correct location
docker-compose up
```

This will result in output similar to:
```
nglancer_1  | INFO:root:configuring neuroglancer defaults
nglancer_1  | INFO:root:starting viewer subprocess
nglancer_1  | INFO:root:setting viewers default volume
nglancer_1  | INFO:root:viewer at: http://2d1e96afebd8:8080/v/3fd6db165c87e94c073947c6abacbf4cc13bf12d/
cv_1        | INFO:root:using mounted dataset
cv_1        | DEBUG:python_jsonschema_objects.classbuilder:Setting value for 'description' to Segmentation volume for the 3D labeled allen atlas
```

The 'viewer at' value above unfortunately isn't 100% accurate at this time. If you copy the URL from the `:` past to the end this will work as a valid url for localhost as follows: `http://localhost:8080/v/3fd6db165c87e94c073947c6abacbf4cc13bf12d/`.  This changes with each execution of the container so you'll have to recopy this each time you launch the viewer.



## Todo
* Currently the URL generation is incorrect because of how neuroglancer's python tooling detects the hostname / fqdn inside a container. Correcting this output is currently in progress.
* Jupyter notebook sidecar that can control the neuroglancer instance over a websocket connection.
 * Fundamentally this seems like it *should* work but the 160 byte control code has to be overcome.

## Stretch Work
* wrap all sub containers in apache, nginx, or similar reverse proxy system to allow for a single url set for neuroglancer, the notebook, and hide the back end services so the end user doesn't need to know anything about ports / port mapping / etc.
