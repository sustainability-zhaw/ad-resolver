FROM python:3.11.1-slim-bullseye

ENV AD_HOST=zhaw.ch
# ENV AD_USER=
# ENV AD_PASS=
# ENV DB_HOST=
ENV LOG_LEVEL=ERROR

COPY app/requirements.txt /requirements.txt

WORKDIR /app

RUN pip install -r /requirements.txt && \
    rm /requirements.txt && \
    groupadd -r app && \
    useradd --no-log-init -r -g app app && \
    chmod -R 775 /app

COPY app/src/ /app/

USER app

CMD [ "python", "main.py" ]
