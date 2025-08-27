ARG BUILD_FROM
FROM $BUILD_FROM

# Alpine base i HA: installer systempakker
# - python3 & pip
# - psycopg2 via apk (stabil mot musl/Alpine)
RUN apk add --no-cache \
      python3 \
      py3-pip \
      py3-psycopg2

# Lag venv som kan se system-site-packages (for py3-psycopg2)
RUN python3 -m venv /opt/venv --system-site-packages \
 && . /opt/venv/bin/activate \
 && pip install --no-cache-dir \
      "modelcontextprotocol[server]" \
      starlette \
      uvicorn \
      httpx

# Gjør venv synlig i PATH
ENV PATH="/opt/venv/bin:${PATH}"

# Kopier kode og oppstartsskript
COPY run.sh /run.sh
COPY server.py /app/server.py
RUN chmod +x /run.sh

# (valgfritt – for dokumentasjon)
EXPOSE 8080

# HA-addons starter /run.sh
CMD ["/run.sh"]
