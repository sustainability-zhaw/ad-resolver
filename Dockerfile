FROM python:3.11.1-slim-bullseye

ENV AD_HOST=
ENV AD_USER=
ENV AD_PASS=
ENV DB_HOST=
ENV BATCH_SIZE=100
ENV BATCH_INTERVAL=180
ENV LOG_LEVEL=DEBUG

COPY app/requirements.txt /requirements.txt
COPY app/src/ /app/

RUN pip install -r requirements.txt && \
    rm requirements.txt && \
    groupadd -r app && \
    useradd --no-log-init -r -g app app && \
    chmod -R 775 /app

WORKDIR /app

USER app

CMD [ "python main.py" ]
