# -*- coding: utf-8 -*-
with open('/tmp/fw2.py', 'rb') as f:
    content = f.read()

# Fix UTF-8 that was double-encoded (Mojibake): replace the byte sequences
fixes = [
    (b'f\xc3\xbcr', b'f&uuml;r'),
    (b'B\xc3\xbchne', b'B&uuml;hne'),
    (b'Pr\xc3\xa4zision', b'Pr&auml;zision'),
    (b'Professionalit\xc3\xa4t', b'Professionalit&auml;t'),
    (b'h\xc3\xb6chster', b'h&ouml;chster'),
    (b'\xc3\x9cbergabe', b'&Uuml;bergabe'),
    (b'k\xc3\xbcnstlich', b'k&uuml;nstlich'),
    (b'pr\xc3\xa4zise', b'pr&auml;zise'),
    (b'au\xc3\x9ferhalb', b'au&szlig;erhalb'),
    (b'Stra\xc3\x9fe', b'Stra&szlig;e'),
    (b'Wei\xc3\x9fensberg', b'Wei&szlig;ensberg'),
    (b'Ei\xc3\x9fen', b'Ei&szlig;en'),
    (b'Sch\xc3\xa4tzung', b'Sch&auml;tzung'),
    (b'e\xc3\xa4', b'e&auml;'),
    (b'n\xc3\xa4', b'n&auml;'),
    (b'rk\xc3\xa4', b'rk&auml;'),
    (b'pr\xc3\xa4', b'pr&auml;'),
    (b'Pr\xc3\xa4', b'Pr&auml;'),
    (b'K\xc3\xbc', b'K&uuml;'),
    (b'R\xc3\xbc', b'R&uuml;'),
    (b'n\xc3\xbc', b'n&uuml;'),
    (b'd\xc3\xbc', b'd&uuml;'),
    (b'f\xc3\xbc', b'f&uuml;'),
    (b't\xc3\xbc', b't&uuml;'),
    (b'r\xc3\xbc', b'r&uuml;'),
    (b'M\xc3\xbc', b'M&uuml;'),
    (b's\xc3\xb6', b's&ouml;'),
    (b'n\xc3\xb6', b'n&ouml;'),
    (b'l\xc3\xb6', b'l&ouml;'),
    (b'h\xc3\xb6', b'h&ouml;'),
    (b'g\xc3\xb6', b'g&ouml;'),
    (b'r\xc3\xb6', b'r&ouml;'),
    (b'k\xc3\xb6', b'k&ouml;'),
    (b'\xc3\x9f', b'&szlig;'),
    (b'W\xc3\xa4', b'W&auml;'),
]

for bad, good in fixes:
    content = content.replace(bad, good)

with open('/tmp/fw2_fixed.py', 'wb') as f:
    f.write(content)

print('patch done')
print('spot check:', content[content.find(b'fw-h1'):content.find(b'fw-h1')+120])