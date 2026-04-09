runtime_env = globals().get("env")

if runtime_env is None:
    print("Must run inside Odoo shell")
else:
    task_model = runtime_env["project.task"]
    
    t1 = task_model.create({
        "name": "[Lane C] Tailscale Route Approval (10.1.0.0/24)",
        "description": "<ul><li>[ ] In login.tailscale.com/admin/machines die Route 10.1.0.0/24 bei toolbox approven.</li><li>[ ] Route springt auf active</li><li>[ ] Nach Freigabe tailscale status verifizieren</li></ul>",
    })
    
    t2 = task_model.create({
        "name": "[Lane C] Tailscale Split DNS Update",
        "description": "<ul><li>[ ] Restricted Nameserver fuer hs27.internal auf 10.1.0.20 umstellen (login.tailscale.com/admin/dns).</li><li>[ ] Remote-Clients erreichen portal, ha, odoo via Domain.</li></ul>",
    })
    
    runtime_env.cr.commit()
    print(f"Tasks {t1.id} and {t2.id} created successfully!")
