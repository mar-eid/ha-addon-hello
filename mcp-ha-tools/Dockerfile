ARG BUILD_FROM
FROM $BUILD_FROM

# Alpine base: installer systempakker
# - python3 & pip
# - psycopg2 via apk (systempakke) for stabil DB-driver på musl/Alpine
RUN apk add --no-cache \
      python3 \
      py3-pip \
      py3-psycopg2

# Lag en virtualenv som også ser system-site-packages
# (slik at py3-psycopg2 fra apk er tilgjengelig i venv)
RUN python3 -m venv /opt/venv --system-site-packages \
 && . /opt/venv/bin/activate \
 && pip install --no-cache-dir \
      "modelcontextprotocol[server]" \
      starlette \
      uvicorn \
      httpx

# Gjør venv tilgjengelig i PATH for hele containeren
ENV PATH="/opt/venv/bin:${PATH}"

# Kopier kode og oppstartsskript
COPY run.sh /run.sh
COPY server.py /app/server.py
RUN chmod +x /run.sh

# (valgfritt, dokumentasjon) eksponer porten vi lytter på
EXPOSE 8080

# HA-addons forventer å starte /run.sh
CMD ["/run.sh"]
