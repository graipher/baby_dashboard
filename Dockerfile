# Dockerfile
FROM tiangolo/meinheld-gunicorn-flask:python3.8


COPY requirements.txt /tmp/
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /app/app
COPY ./project /app/app

ENV MODULE_NAME "app.__init__"


