import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    task_id = 155
    description = """
    <h1>RAM-Budget optimieren (Proxmox)</h1>
    <p>Der Proxmox-Host (Anker) hat 16 GB physikalischen RAM. Aktuell sind jedoch VMs und Container mit insgesamt ca. 20 GB RAM zugewiesen (Overprovisioning!).</p>
    <p>Das führt dazu, dass der Server Swap nutzt (aktuell ca. 1.7 GB Swap verwendet).</p>
    
    <h3>Aktuelle Zuweisung (Laufend):</h3>
    <ul>
        <li><b>VM 210 (haos):</b> 2048 MB</li>
        <li><b>VM 220 (odoo):</b> 2048 MB</li>
        <li><b>VM 240 (PBS-FraWo):</b> 2048 MB</li>
        <li><b>VM 300 (nextcloud):</b> 3072 MB</li>
        <li><b>VM 330 (paperless):</b> 3072 MB</li>
        <li><b>CT 100 (toolbox):</b> 2048 MB</li>
        <li><b>CT 110 (storage):</b> 2048 MB</li>
        <li><b>CT 120 (vaultwarden):</b> 2048 MB</li>
        <li><b>CT 130 (radio):</b> 2048 MB</li>
    </ul>
    
    <h3>Vorschlag zur Optimierung:</h3>
    <ol>
        <li>Reduzierung von <b>haos</b> auf 1.5 GB (spart 512 MB).</li>
        <li>Reduzierung von <b>toolbox</b> auf 1 GB (spart 1024 MB).</li>
        <li>Reduzierung von <b>vaultwarden</b> auf 1 GB (spart 1024 MB).</li>
    </ol>
    <p>Damit sparen wir ca. 2.5 GB RAM und entlasten den Host!</p>
    """
    
    result = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [[task_id], {'description': description}])
    print(f"Enriched task {task_id}: {result}")

if __name__ == "__main__":
    main()
