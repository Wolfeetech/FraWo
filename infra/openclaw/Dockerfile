FROM node:22-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 curl ca-certificates openssh-client git \
    && update-ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | env HOME=/root sh \
    && /root/.local/bin/uv tool install mcp-server-odoo \
    && ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts 2>/dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

RUN npm install -g openclaw

COPY openclaw.json /app/openclaw.default.json
COPY entrypoint.sh /app/entrypoint.sh
COPY mcp_azuracast.py /app/mcp_azuracast.py
RUN chmod +x /app/entrypoint.sh

WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]
