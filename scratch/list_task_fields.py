import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    # Read fields
    fields = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'fields_get', [], {'attributes': ['type', 'string']})
    print(f"Fields of project.task:")
    for name, info in fields.items():
        if 'stage' in name or 'state' in name or 'close' in name:
            print(f"- {name}: {info['string']} ({info['type']})")

if __name__ == "__main__":
    main()
