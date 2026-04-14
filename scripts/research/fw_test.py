import xmlrpc.client

url = 'http://localhost:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')

home = '''<t name=&quot;Home&quot; t-name=&quot;website.homepage&quot;></t>'''
print('uid:', uid)
print('done')
