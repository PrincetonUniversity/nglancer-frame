#! /bin/env python

from cloudvolume import CloudVolume
import types
import logging
import os
import numpy as np
import types
from time import sleep

def start_server():



    ## add some error checking
    if not os.path.isfile('/mnt/data/info'):
        logging.info('no valid volume found, using test data')
        vol=testdat()
    else:
        logging.info('using mounted dataset')
        vol = CloudVolume('file:///mnt/data')

    #logging.info('patching viewer to allow connections on all IPs')
    #funcType = types.MethodType
    #vol.viewer = funcType(localviewer, vol)

    logging.info('starting cloudvolume service')
    vol.viewer()
    while (1):
        sleep(0.1)



## replacement version of the 'view' function for the object `CloudVolumePrecomputed`
def localviewer(self, port=1337):
    import cloudvolume.server
    logging.info('using replacement viewer function')
    cloudvolume.server.view(self.cloudpath,hostname="0.0.0.0", port=port)

def testdat():
    """
    This is simply the test skeleton data from the cloud volume testing
    """
    info = CloudVolume.create_new_info(
    num_channels=1, # Increase this number when we add more tests for RGB
    layer_type='segmentation',
    data_type='uint16',
    encoding='raw',
    resolution=[1,1,1],
    voxel_offset=(0,0,0),
    skeletons=True,
    volume_size=(100, 100, 100),
    chunk_size=(64, 64, 64),
    )
    # Skeleton of my initials
    # z=0: W ; z=1 S
    vertices = np.array([
    [ 0, 1, 0 ],
    [ 1, 0, 0 ],
    [ 1, 1, 0 ],

    [ 2, 0, 0 ],
    [ 2, 1, 0 ],
    [ 0, 0, 1 ],

    [ 1, 0, 1 ],
    [ 1, 1, 1 ],
    [ 0, 1, 1 ],

    [ 0, 2, 1 ],
    [ 1, 2, 1 ],
    ], np.float32)

    edges = np.array([
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 8],
    [8, 9],
    [9, 10],
    [10, 11],
    ], dtype=np.uint32)

    radii = np.array([
    1.0,
    2.5,
    3.0,
    4.1,
    1.2,
    5.6,
    2000.123123,
    15.33332221,
    8128.124,
    -1,
    1824.03
    ], dtype=np.float32)

    vertex_types = np.array([
    1,
    2,
    3,
    5,
    8,
    2,
    0,
    5,
    9,
    11,
    22,
    ], dtype=np.uint8)
    logging.info('creating temporary volume')
    vol = CloudVolume('file:///tmp/cloudvolume/test-skeletons', info=info)
    logging.info('uploading fake data to tmp folder')
    vol.skeleton.upload_raw(
    segid=1, vertices=vertices, edges=edges,
    radii=radii, vertex_types=vertex_types
    )
    return vol

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    start_server()
