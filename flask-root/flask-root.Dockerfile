FROM python:3.7-alpine

RUN pip install flask redis

VOLUME /opt/app

WORKDIR /opt/app

CMD ["python", "./app.py"]
