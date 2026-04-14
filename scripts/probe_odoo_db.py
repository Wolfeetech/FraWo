import xmlrpc.client
url = 'http://192.168.2.22:8069'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
try:
    print(common.list_databases())
except Exception as e:
    print(f"Error: {e}")
