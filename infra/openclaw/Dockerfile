FROM node:22-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 curl ca-certificates \
    && update-ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | env HOME=/root sh \
    && /root/.local/bin/uv tool install mcp-server-odoo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

RUN npm install -g openclaw

COPY openclaw.json /app/openclaw.default.json
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]
