# -*- coding: utf-8 -*-
import xmlrpc.client

url = "http://10.1.0.22:8069"
db = "FraWo_GbR"
username = "wolf@frawo-tech.de"
password = "Wolf2024!Frawo"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

websites = models.execute_kw(db, uid, password, 'website', 'search_read', [[]], {'fields': ['id', 'name', 'domain']})
print(f"Websites: {websites}")
