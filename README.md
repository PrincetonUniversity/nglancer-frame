# Neuroglancer Frame
This is a small `docker` + `docker-compose` based solution for running the [neuroglancer volumetric viewer](https://github.com/seung-lab/neuroglancer) against precomputed file sets off local filesystems. Local here is relative and will also allow usage of mounted cifs and nfs filesystems. The data is served up using the [cloud-volume tool](https://github.com/seung-lab/cloud-volume) developed by the seung lab.

## Requirements
* Docker: A modern version of [docker appropriate to the OS](https://docs.docker.com/install/#supported-platforms) needs to be installed.
* docker-compose: A recent version of [docker-compose](https://docs.docker.com/compose/install/#install-compose) must be installed as the compose file included with this package uses a relatively new format version to allow for the `.env` file support to work.

## Usage
First the images will need to be built with: `./rebuild-all.sh`; initially this will take a bit of time but should not need to be done again unless pulling new updates from this repo. After that simply set the variable `CVDATA` to the root of a dataset, this must be a full path to the folder.  The last setup step required is to source the file `setids.sh` to set some required environment variables and launch the containers with `docker-compose up`. A series of containers will be launched to handle a variety of different subtasks including an extremely basic website.

On a linux desktop this would look like:
```
./rebuild-all.sh
export CVDATA=/mnt/dataset # change path to correct location for mounted volume
source ./setids.sh
docker-compose up
```
Once this is done open a browser and navigate to `http://localhost` and you'll find a website with links to both an iPython notebook and the neuroglancer web interface.

## Structure
A single docker-compose file is able to build and launch all the constituent parts, bringing up a number of subordinate tasks and an apache server acting as a reverse proxy to act as a front end.
### apacheproxy
This creates a simple vhost that populates several sub tree urls to different backend services.
```
/ <- this points to the flask-root application
/testcv <- this points to the default cloudvolume launched as a service.
/vols <- this points to the runtime configurable proxy used to setup additional volumes, neuroglancer instances, or other services
/nglancer <- this points to the base location of the stock neuroglancer instance, while it can't be used directly due to neuroglancer design decisions it's useful for URL construction.
/notebook <- this points to an iPython notebook server mounting the ./data folder in this project
```
### confproxy
This launches the http-conf-proxy developed by the jupyterhub team (details found here: https://github.com/jupyterhub/configurable-http-proxy) to use for routing requests to different backend cloudvolumes.

### testcv
This launches a shim that mounts a the volume located at the envvar `CVDATA`, inspects it, and serves it out as using the seunglab's 'cloud volume' tool (https://github.com/seung-lab/cloud-volume). If an invalid volume is found at the mounted location it generates a random cube of data for testing against instead.

### nglancer
This launches a small python shim to spin up the neuroglancer service and spin lock to keep it alive while the services are running.  The default neuroglancer instance will be configured out of the box to view the cloudvolume launched by the `testcv` service.  It also registers relevant meta-data into the redis database for use by other services to allow them to construct urls to the working instance.

TODO: eliminate the spinlock and have it startup a properly forked service.

### notebook
This launches a standard datascience notebook server mounting the `./data` folder in this project to allow for a local python scratchpad system. The redis toolkit is installed here to allow direct access to the key value store.

### redis
This simply spins up an all in memory redis database to use as a key-value exchange server between several of the other services above.

### flask-root
This is a simple one file flask app that apache send you to by default if you go to the localhost root. It generates a valid link for the neuroglancer instance and provides a direct link to the notebook server to help people get started.

## Stretch Work
* Jupyter notebook sidecar that can control the neuroglancer instance over a websocket connection.
 * Fundamentally this seems like it *should* work but the 160 byte control code has to be overcome.
