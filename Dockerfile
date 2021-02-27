FROM python:3.9-slim-buster

WORKDIR /srv
COPY . .

RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends libhdf5-103 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists \
 && python3 -m venv _venv \
 && _venv/bin/pip install -r requirements.txt

VOLUME /srv/data

ENTRYPOINT ["/srv/_venv/bin/python", "-m", "wordgen.web"]
CMD ["--host", "0.0.0.0", "--port", "8080", "web_config.json"]
