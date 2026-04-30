import xmlrpc.client

URL = "http://100.82.26.53:8444"
DB = "FraWo_GbR"
USERS = ["wolf@frawo-tech.de", "admin"]
PASSWORD = "Wolf2024!Frawo"

def probe():
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    for user in USERS:
        print(f"Trying user: {user}...")
        try:
            uid = common.authenticate(DB, user, PASSWORD, {})
            if uid:
                print(f"Success! UID: {uid} for user: {user}")
                return uid, user
            else:
                print(f"Failed for user: {user}")
        except Exception as e:
            print(f"Error for user {user}: {e}")
    return None, None

if __name__ == "__main__":
    probe()
