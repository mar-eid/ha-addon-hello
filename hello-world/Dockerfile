FROM python:3.12-slim

# Install run‑time dependencies. Using slim base reduces image size.
RUN pip install --no-cache-dir "modelcontextprotocol[server]" starlette uvicorn httpx

# Copy the service code and helper script into the image
COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Expose port 8080 for the SSE server
EXPOSE 8080

# Run the add‑on. The script simply starts Uvicorn to serve the FastMCP SSE application.
CMD ["/run.sh"]