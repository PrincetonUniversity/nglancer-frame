import docker
client = docker.DockerClient(base_url='unix://var/run/docker.sock')


environment = {
    'PYTHONPATH':'/opt/libraries',
    'CONFIGPROXY_AUTH_TOKEN':"'31507a9ddf3e41cf86b58ffede2db68326657437704461ae2c1a4018d55e18f0'"
}

# Set up the first cloudvolume container
volumes1 = {
    '/jukebox/LightSheetData/atlas/neuroglancer/atlas/princetonmouse':{
        'bind':'/mnt/data',
        'mode':'ro'
    },
    '/home/ahoag/Git/nglancer-frame/libraries':{
        'bind':'/opt/libraries'
    }
}

container1 = client.containers.run('cloudv_test',
                                  volumes=volumes1,
                                  environment=environment,
                                  network='nglancer',
                                  name='cloudv1',
                                  detach=True)
# Register the cloudvolume with the reverse proxy
proxy_h = pp.progproxy(target_hname='confproxy')
proxy_h.addroute(proxypath='cloudv1',proxytarget="http://cloudv1:1337")


# Set up the second cloudvolume container
volumes2 = {
    '/home/ahoag/ngdemo/demo_bucket/grin_lens/oostland_m27':{
        'bind':'/mnt/data',
        'mode':'ro'
    },
    '/home/ahoag/Git/nglancer-frame/libraries':{
        'bind':'/opt/libraries'
    }
}


container2 = client.containers.run('cloudv_test',
                                  volumes=volumes2,
                                  environment=environment,
                                  network='nglancer',
                                  name='cloudv2',
                                  detach=True)
# Register the cloudvolume with the reverse proxy
proxy_h.addroute(proxypath='cloudv2',proxytarget="http://cloudv2:1337")
