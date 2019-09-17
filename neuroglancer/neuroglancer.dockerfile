FROM python:3.6.9-slim-buster

RUN mkdir -p /opt/repos

WORKDIR /opt/repos

RUN apt-get update && apt-get upgrade && \
    apt-get install bash git gcc 'g++' musl-dev -y

##setup required python software
RUN  pip install neuroglancer && \
     git clone https://github.com/seung-lab/igneous.git /opt/repos/igneous && \
     cd /opt/repos/igneous && pip install -r requirements.txt

COPY nglancer-launcher.py /opt/nglancer-launcher.py

CMD ["python","/opt/nglancer-launcher.py"]

### node work - not in use!
#FROM node:10.16.3-alpine

## get neuroglancer source
#RUN git clone https://github.com/seung-lab/neuroglancer.git /opt/neuroglancer

#WORKDIR /opt/neuroglancer

#RUN npm i && npm run build-python

## the run dev-server command won't work here, we are going to need a python
# script to handle this.
#CMD ["npm","run","dev-server"]
