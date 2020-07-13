# Dockerfile
FROM tiangolo/meinheld-gunicorn-flask:python3.8


COPY requirements.txt /tmp/
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /app/app
COPY ./project /app/app
COPY reference_*.csv /app/
COPY setup_db.py /app/

RUN cd /app && ./setup_db.py

ENV MODULE_NAME "app.__init__"


