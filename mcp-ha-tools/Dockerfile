ARG BUILD_FROM
FROM $BUILD_FROM

# Systempakker (Alpine) – python + pip + psycopg2 fra apk
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

# Gjør venv tilgjengelig i PATH
ENV PATH="/opt/venv/bin:${PATH}"

# Sett arbeidskatalog til /app (viktig for uvicorn --app-dir /app)
WORKDIR /app

# Kopier kode og oppstartsskript
COPY server.py /app/server.py
COPY run.sh /run.sh

# Normaliser linjeslutt på run.sh (hindrer HEREDOC/CRLF-problemer) og gjør den kjørbar
RUN sed -i 's/\r$//' /run.sh && chmod +x /run.sh

# (valgfritt) eksponer porten
EXPOSE 8080

# HA-addons starter /run.sh
CMD ["/run.sh"]
