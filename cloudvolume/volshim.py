#! /bin/env python

from cloudvolume import CloudVolume
import types
import logging

## replacement version of the 'view' function for the object `CloudVolumePrecomputed`
def viewer(self, port=1337):
    import cloudvolume.server
    logging.info('using replacement viewer function')
    cloudvolume.server.view(self.cloudpath,host="*.*.*.*", port=port)


vol = CloudVolume('file://mnt/data')
logging.info('starting cloudvolume service')



vol.viewer()
