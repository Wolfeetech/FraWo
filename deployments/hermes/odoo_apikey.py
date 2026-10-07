# Odoo-Shell-Skript (CT140): eigener API-Schluessel fuer Benutzer agent (UID 7) fuer den Hermes-Pilot, 90 Tage.
# Aufruf ueber odoo_schluessel_einrichten.sh. Der Schluessel wird nur in eine Datei (600) geschrieben, nie ausgegeben.
import datetime
import os

u = env['res.users'].sudo().browse(7)
print('Benutzer:', u.login)
k = env['res.users.apikeys'].with_user(u).sudo()._generate(
    None, 'Hermes-Pilot CT160 (#1965)', datetime.datetime.now() + datetime.timedelta(days=90))
fd = os.open('/tmp/hermes_odoo_key', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
os.write(fd, k.encode())
os.close(fd)
env.cr.commit()
print('Schluessel erzeugt, Laenge', len(k))
