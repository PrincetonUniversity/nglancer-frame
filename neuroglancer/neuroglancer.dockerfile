FROM node:10.16.3-alpine

RUN git clone https://github.com/seung-lab/neuroglancer.git /opt/neuroglancer

WORKDIR /opt/neuroglancer

RUN npm i && npm run build-python
