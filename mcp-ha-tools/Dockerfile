ARG BUILD_FROM
FROM $BUILD_FROM

# Install system deps (Alpine base)
RUN apk add --no-cache python3 py3-pip py3-psycopg2 \
    && python3 -m pip install --no-cache-dir \
       "modelcontextprotocol[server]" \
       starlette uvicorn httpx

# Copy code
COPY run.sh /run.sh
COPY server.py /app/server.py
RUN chmod +x /run.sh

# Expose SSE port (host_network true, but useful for docs)
EXPOSE 8080

# HA images expect /run.sh as entrypoint
CMD ["/run.sh"]
