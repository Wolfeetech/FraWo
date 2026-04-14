import os

os.chdir('/opt/homeserver2027/stacks/toolbox-network')

with open('Caddyfile', 'r') as f:
    cf = f.read()

cf = cf.replace('root * /srv/portal/franz', 'root * /srv/portal')

with open('Caddyfile', 'w') as f:
    f.write(cf)

os.system('docker-compose exec -T caddy caddy reload -c /etc/caddy/Caddyfile')
