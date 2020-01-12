from python:3.7-slim

run mkdir /app
workdir /app

copy . .

run BUILD_DEPS='gcc' \
  && apt-get update \
  && apt-get install -y $BUILD_DEPS geoip-database \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir -r requirements.txt \
  && ./setup.py install \
  && rm -fr build \
  && apt-get purge -y --auto-remove $BUILD_DEPS

volume /app/volume

expose 27900/udp 28900

## trying to use non-root user:
# run chown -R nobody .
# user nobody
## unfortunately volume still belongs to root then and thus db.sqlite is read-only
