FROM python:3.9.15-slim-bullseye

ENV AD_HOST=
ENV AD_USER=
ENV AD_PASS=
ENV DB_HOST=
ENV BATCH_SIZE=
ENV LOG_LEVEL=

COPY requirements.txt /requirements.txt
COPY src/ /app/

RUN pip install -r requirements.txt && rm requirements.txt

WORKDIR /app
