#FROM continuumio/anaconda3:2019.07
FROM python:3.6.9-slim-buster

#USER root

#SHELL ["/bin/bash","-c"]

RUN mkdir -p /opt/repos && mkdir -p /tmp/cloudvolume/test-skeletons

WORKDIR /opt/repos

RUN apt-get update && apt-get upgrade -y && \
    apt-get install bash git gcc musl-dev curl htop psmisc net-tools -y

#RUN git clone https://github.com/seung-lab/cloud-volume.git && cd cloud-volume && \
#    pip install -r requirements.txt && pip install . && pip install -e .[all_viewers]
RUN pip install cloud-volume && pip install cloud-volume[boss,test,all_viewers]

VOLUME ["/mnt/data"]

COPY volshim.py /opt/volshim.py

CMD ["python","/opt/volshim.py"]
