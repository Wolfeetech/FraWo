import xmlrpc.client

URL = "http://100.82.26.53:8444"

def list_dbs():
    print(f"Listing DBs at {URL}...")
    try:
        db_service = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/db')
        dbs = db_service.list()
        print(f"Databases: {dbs}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_dbs()
