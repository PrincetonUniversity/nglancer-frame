#! /bin/env python

## basic shim to load up neuroglancer in a browser:
import neuroglancer
import logging
from time import sleep
import progproxy as pp
import redis

logging.basicConfig(level=logging.DEBUG)
# we are currently using the seunglab hosted neuroglancer static resources
# ideally this would be self hosted for local development against nglancer
logging.info("configuring neuroglancer defaults")
neuroglancer.set_static_content_source(
    url="https://neuromancer-seung-import.appspot.com"
)
## neuroglancer setup segment:
## set the tornado server that is launched to talk on all ips and at port 8080
neuroglancer.set_server_bind_address("0.0.0.0", "8080")

neuroglancer.debug = True
neuroglancer.server.debug = True

logging.info("starting viewer subprocess")
# setup a viewer with pre-configured defaults and launch.
viewer = neuroglancer.Viewer()

logging.info("viewer token: {}".format(viewer.token))

logging.info("setting viewers default volume")
# load data from cloudvolume container:
with viewer.txn() as s:
    s.layers["segmentation"] = neuroglancer.SegmentationLayer(
        source="precomputed://http://localhost/testcv/"
    )
# this container does not act as a proxy for the CV container, as such
# we need to expose port 1337 to the local system in the docker compose file.

## need to retool this so it shows the correct link, the internal FQDN is not useful
logging.info("viewer at: {}".format(viewer))

logging.debug("creating proxy object")
proxy_h = pp.progproxy(target_hname="confproxy")
logging.debug("adding route to configurable proxy")

# pure brute force approach where we proxy the root and assemble a link from exported state information.
proxy_h.addroute(proxypath="viewers/viewer0/", proxytarget=f"http://nglancer:8080/")

logging.debug("neuroglancer viewer is now available")

## redis shared state segment
kv = redis.Redis(host="redis", decode_responses=True)  # container simply named redis

kv.hmset("viewer0", {"host": "nglancer", "port": "8080", "token": viewer.token})

logging.debug("redis key viewer0: {}".format(kv.hgetall("viewer0")))

while 1:
    sleep(0.1)
