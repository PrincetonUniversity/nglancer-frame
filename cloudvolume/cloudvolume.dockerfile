FROM python:3.6.9-alpine

RUN pip install cloud-volume cloud-volume[boss,test,all_viewers]

VOLUME ["/mnt/data"]

COPY volshim.py /opt/volshim.py

CMD ["python","/opt/volshim.py"]
