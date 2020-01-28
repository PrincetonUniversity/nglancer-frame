FROM jupyter/datascience-notebook:latest

RUN pip install redis neuroglancer docker

# set user to root so configuring uid/gid works as expected
USER root

#add a pre-notebook launch hook
COPY fix-docker-perms.sh /usr/local/bin/start-notebook.d/
