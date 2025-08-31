from python:3.7-slim

run mkdir /app
workdir /app

copy . .

# Download free GeoIP database from DB-IP (optional, no registration required)
# This step is allowed to fail without breaking the build
run apt-get update \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/* \
  && (curl -L -o /usr/share/dbip-country-lite.mmdb.gz "https://download.db-ip.com/free/dbip-country-lite-$(date +'%Y-%m').mmdb.gz" \
      || curl -L -o /usr/share/dbip-country-lite.mmdb.gz "https://download.db-ip.com/free/dbip-country-lite-$(date -d '-1 month' +'%Y-%m').mmdb.gz") \
  && gunzip /usr/share/dbip-country-lite.mmdb.gz 2>/dev/null \
  || echo "GeoIP database download failed - continuing without it (country lookups will be disabled)"

run BUILD_DEPS='gcc' \
  && apt-get update \
  && apt-get install -y $BUILD_DEPS \
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
