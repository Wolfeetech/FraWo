import xmlrpc.client
import sys

URL = "http://100.99.206.128:8444"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
try:
    dbs = common.list()
    print(f"Databases found: {dbs}")
except Exception as e:
    print(f"Error listing databases: {e}")
    sys.exit(1)
