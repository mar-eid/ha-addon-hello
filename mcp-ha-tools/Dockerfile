ARG BUILD_FROM
FROM $BUILD_FROM

# System deps
RUN apk add --no-cache \
      python3 \
      py3-pip \
      py3-psycopg2

# Python venv with system-site-packages (so psycopg2 from apk is visible)
RUN python3 -m venv /opt/venv --system-site-packages \
 && . /opt/venv/bin/activate \
 && pip install --no-cache-dir \
      "modelcontextprotocol[server]" \
      starlette \
      uvicorn \
      httpx

ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

COPY server.py /app/server.py
COPY run.sh /run.sh

# Normalize line endings and make run.sh executable
RUN sed -i 's/\r$//' /run.sh && chmod +x /run.sh

EXPOSE 8080
CMD ["/run.sh"]
