#!/bin/env python

from flask import Flask
import redis
import docker
import progproxy as pp
import logging
import time
import secrets
import os
import json
from datetime import datetime, timedelta
import subprocess, requests

hosturl = os.environ['HOSTURL']

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


@app.route("/")
@app.route("/index")
def base():
    ## we want to refresh this each time we refresh the page incase it's
    ## not ready on first startup.
    kv = redis.Redis(host="redis", decode_responses=True)
    task = subprocess.Popen("ip route | awk 'NR==1 {print $3}'",shell=True,stdout=subprocess.PIPE)
    data = task.stdout.read()
    localhost_addr = data.decode('utf-8').strip('\n')
    logging.debug("Got localhost address inside container:")
    logging.debug(localhost_addr)
    # response = requests.get(f'http://nglancerstatic:8080')
    response = requests.get(f'http://{localhost_addr}:8080')
    logging.debug("Response from neuroglancer container is:")
    logging.debug(response)
    logging.debug(response.text)
    # viewer0 = kv.hgetall("viewer0")
    # notebookurl = "http://localhost/notebook"
    hosturl = os.environ['HOSTURL']
    notebookurl = f"http://localhost/notebook"
    # neuroglancerurl = f"http://localhost/nglancer/viewer0/v/{viewer0['token']}/"

    ## this just bruteforce dumps html into a return output instead of a polished
    # template but should be fine as a demo.
    return f"""
<html>
    <head>
        <title>Home Page - Neuroglancer</title>
    </head>
    <body>
        <h1>neuroglancercv</h1>
        <h2>Links: </h2>

        <a href={notebookurl} target="_blank"> Notebook </a>
    </body>
</html>"""


@app.route("/ngdemo")
def ngdemo():
    """ A route for a minimal working example of launching a cloudvolume container
    and neuroglancer container with a layer for that cloudvolume.
    This route will provide a link for the neuroglancer viewer hosting that cloudvolume """
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    # Redis setup for this session
    kv = redis.Redis(host="redis", decode_responses=True)

    session_name = secrets.token_hex(6)
    # session_name = 'my_ng_session'
    viewer_id = "viewer1" # for storing the viewer info in redis
    # kv.hmset(session_name,{"viewer_id":viewer_id})
    kv.hmset(session_name,{"cv_count":0}) # initialize the number of cloudvolumes in this ng session

    # Set up environment to be shared by all cloudvolumes
    cv_environment = {
        'PYTHONPATH':'/opt/libraries',
        'CONFIGPROXY_AUTH_TOKEN':"'31507a9ddf3e41cf86b58ffede2db68326657437704461ae2c1a4018d55e18f0'",
        'SESSION_NAME':session_name
    }

    # Set up first cloudvolume
    cv1_container_name = '{}_cv1_container'.format(session_name)
    cv1_name = "testvol1"
    layer1_type = "segmentation"
    # cv1_localhost_path = '/jukebox/LightSheetData/lightserv_testing/neuroglancer/oostland_m27' 
    cv1_localhost_path = '/home/ahoag/ngdemo/demo_bucket/atlas/princetonmouse'
    
    cv1_mounts = {
        cv1_localhost_path:{
            'bind':'/mnt/data',
            'mode':'ro'
            },
    }
    cv1_container = client.containers.run('cloudv_test',
                                  volumes=cv1_mounts,
                                  environment=cv_environment,
                                  network='nglancer',
                                  name=cv1_container_name,
                                  detach=True)
    # Enter the cv information into redis so I can get it in the neuroglancer container
    kv.hmset(session_name, {"cv1_container_name": cv1_container_name,
        "cv1_name": cv1_name, "layer1_type":layer1_type})
    # increment the number of cloudvolumes so it is up to date
    kv.hincrby(session_name,'cv_count',1)
    
    # register with the confproxy so that it can be seen from outside the nglancer network
    proxy_h = pp.progproxy(target_hname='confproxy')
    proxypath_1 = os.path.join('cloudvols',session_name,cv1_name)
    proxy_h.addroute(proxypath=proxypath_1,proxytarget=f"http://{cv1_container_name}:1337")

    # Set up the second cloudvolume
    # cv2_container_name = '{}_cv2_container'.format(session_name)
    # cv2_name = "testvol2"
    # layer2_type = "segmentation"
    # cv2_localhost_path = '/jukebox/LightSheetData/lightserv_testing/neuroglancer/princetonmouse' 
    
    # cv2_mounts = {
    #     cv2_localhost_path:{
    #         'bind':'/mnt/data',
    #         'mode':'ro'
    #         },
    # }
    # cv2_container = client.containers.run('cloudv_test',
    #                               volumes=cv2_mounts,
    #                               environment=cv_environment,
    #                               network='nglancer',
    #                               name=cv2_container_name,
    #                               detach=True)
    # # Enter the cv information into redis so I can get it in the neuroglancer container
    # kv.hmset(session_name, {"cv2_container_name": cv2_container_name,
    #     "cv2_name": cv2_name, "layer2_type":layer2_type})
    # # increment the number of cloudvolumes so it is up to date
    # kv.hincrby(session_name,'cv_count',1)
    
    # # register with the confproxy so that it can be seen from outside the nglancer network
    # proxy_h = pp.progproxy(target_hname='confproxy')
    # proxypath_2 = os.path.join('cloudvols',session_name,cv2_name)
    # proxy_h.addroute(proxypath=proxypath_2,proxytarget=f"http://{cv2_container_name}:1337")

    # Run the ng container which adds the viewer info to redis
    ng_container_name = '{}_ng_container'.format(session_name)
    ng_environment = {
        'HOSTURL':hosturl,
        'PYTHONPATH':'/opt/libraries',
        'CONFIGPROXY_AUTH_TOKEN':"'31507a9ddf3e41cf86b58ffede2db68326657437704461ae2c1a4018d55e18f0'",
        'SESSION_NAME':session_name
    }
    ng_container = client.containers.run('ngdemo',
                                  environment=ng_environment,
                                  network='nglancer',
                                  name=ng_container_name,
                                  detach=True) 
    # Add the ng container name to redis session key level
    kv.hmset(session_name, {"ng_container_name": ng_container_name})
    # Add ng viewer url to config proxy so it can be seen from outside of the nglancer network eventually
    proxy_h.addroute(proxypath=f'viewers/{session_name}', proxytarget=f"http://{ng_container_name}:8081/")

    # Spin until the neuroglancer viewer token from redis becomes available (may be waiting on the neuroglancer container to finish writing to redis)
    # time.sleep(1.5      )
    while True:
        session_dict = kv.hgetall(session_name)
        if 'viewer' in session_dict.keys():
            break
        else:
            logging.debug("Still spinning; waiting for redis entry for neuoglancer viewer")
            time.sleep(0.25)
    viewer_json_str = kv.hgetall(session_name)['viewer']
    viewer_dict = json.loads(viewer_json_str)
    logging.debug(f"Redis contents for viewer")
    logging.debug(viewer_dict)
    
    neuroglancerurl = f"http://{hosturl}/nglancer/{session_name}/v/{viewer_dict['token']}/" # localhost/nglancer is reverse proxied to 8081 inside the ng container
    return f"""
<html>
    <head>
        <title>Containerized neuroglancer links</title>
    </head>
    <body>
        <h1>neuroglancercv</h1>
        <h2>Links: </h2>

        <a href={neuroglancerurl} target="_blank"> Neuroglancer </a>
    </body>
</html>"""


@app.route("/ng_viewer_checker") 
def ng_viewer_checker():
    """ Checks the activity timestamp for all open viewers.
    If it has been more than 6 hours since last activity,
    then shuts down the viewer and its cloudvolumes and removes them from
    the proxy table. """
    logging.basicConfig(level=logging.DEBUG)
    kv = redis.Redis(host="redis", decode_responses=True)
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    proxy_h = pp.progproxy(target_hname='confproxy')
    
    """ First get the entire proxy route table.
    We will need it to know the cloudvolume proxy paths 
    so we can take them down once we figure out the 
    expired neuroglancer viewers """
    response_all = proxy_h.getroutes()
    proxy_dict_all = json.loads(response_all.text)
    
    """ Make the timestamp against which we will 
    compare the neuroglancer viewer timestamps """
    timeout_timestamp_iso = (datetime.utcnow() - timedelta(seconds=5)).isoformat()

    response_expired = proxy_h.getroutes(inactive_since=timeout_timestamp_iso)
    proxy_dict_expired = json.loads(response_expired.text)
    proxy_viewer_dict_expired = {key:proxy_dict_expired[key] for key in proxy_dict_expired.keys() if 'viewer' in key}

    """ Now figure out the session names of each of the expired viewers """   
    expired_session_names = [key.split('/')[-1] for key in proxy_viewer_dict_expired.keys()]
    logging.debug("expired session names:")
    logging.debug(expired_session_names)
    
    """ Now delete the proxy routes for the expired viewers
    and the cloudvolumes attached to them, which we 
    can identify because we know the session name """
    for session_name in expired_session_names:
        expired_proxypaths = [key for key in proxy_dict_all.keys() if session_name in key]
        for proxypath in expired_proxypaths:
            proxy_h.deleteroute(proxypath)
        """ Now take down the cloudvolume containers """
        session_dict = kv.hgetall(session_name)
        # Cloudvolume containers
        cv_count = int(session_dict['cv_count'])
        for i in range(cv_count):
            cv_container_name = session_dict['cv%i_container_name' % (i+1)]
            cv_container = client.containers.get(cv_container_name)
            logging.debug(f"Killing cloudvolume container: {cv_container_name}")
            cv_container.kill()           
        # Neuroglancer container
        ng_container_name = session_dict['ng_container_name']
        ng_container = client.containers.get(ng_container_name)
        logging.debug(f"Killing neuroglancer container: {ng_container_name}")
        ng_container.kill()           
    final_timeout_timestamp_iso = (datetime.utcnow() - timedelta(seconds=5)).isoformat()
    final_response = proxy_h.getroutes(inactive_since=final_timeout_timestamp_iso)
    return final_response.text

@app.route("/precomputed_test") 
def precomputed_test():
    """ Route for testing out making precomputed datasets 
    (so that cloudvolume can host them) from TIF stacks """
    logging.basicConfig(level=logging.DEBUG)

    # kv = redis.Redis(host="redis", decode_responses=True)
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    # proxy_h = pp.progproxy(target_hname='confproxy')
     # Set up environment to be shared by all cloudvolumes
    session_name = secrets.token_hex(6)
    environment = {
        'PYTHONPATH':'/opt/libraries',
        'CONFIGPROXY_AUTH_TOKEN':"'31507a9ddf3e41cf86b58ffede2db68326657437704461ae2c1a4018d55e18f0'",
        'SESSION_NAME':session_name
    }

    atlas_file = '/home/ahoag/mounts/LightSheetData/atlas/annotation_sagittal_atlas_20um_iso.tif'

    volumes = {
        '/home/ahoag/ngdemo/docker':{
            'bind':'/mnt/data',
            'mode':'rw'
            },
        atlas_file:{
            'bind':'/mnt/data/annotation_sagittal_atlas_20um_iso.tif',
            'mode':'ro'
            }
    }

    # container = client.containers.run('precomputed_test',
    #                               volumes=cv1_mounts,
    #                               environment=cv_environment,
    #                               network='nglancer',
    #                               name=cv1_container_name,
    #                               detach=True)

    container = client.containers.run('precomputed_test',
                              environment=environment,
                              network='nglancer',
                              name='precomp1',
                              volumes=volumes,
                              detach=False
                              )
    return "Test performed"
if __name__ == "__main__":
    app.run(host="0.0.0.0")
