import os

os.chdir('/opt/homeserver2027/stacks/toolbox-network')

# Add port to docker-compose.yml
with open('docker-compose.yml', 'r') as f:
    dc = f.read()

if '8447:8447' not in dc:
    dc = dc.replace('- "443:443"', '- "443:443"\n      - "8447:8447"')
    with open('docker-compose.yml', 'w') as f:
        f.write(dc)

# Add portal block to Caddyfile
with open('Caddyfile', 'r') as f:
    cf = f.read()

if ':8447' not in cf:
    cf += '\n:8447 {\n  root * /srv/portal/franz\n  file_server\n}\n'
    with open('Caddyfile', 'w') as f:
        f.write(cf)

os.system('docker-compose up -d')
