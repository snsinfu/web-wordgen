FROM python:3.9-alpine

WORKDIR /srv
COPY . .

RUN apk add --no-cache hdf5 \
 && python3 -m venv _venv \
 && _venv/bin/pip install -r requirements.txt

VOLUME /srv/data

ENTRYPOINT ["/srv/_venv/bin/python", "-m", "wordgen.web"]
CMD ["--host", "0.0.0.0", "--port", "8080", "web_config.json"]
