from odoo import models, fields

class MaintenanceEquipmentIT(models.Model):
    _inherit = 'maintenance.equipment'

    ip_address = fields.Char(string="LAN IP Address", help="Internal LAN IP (e.g. 10.1.0.112)")
    tailscale_ip = fields.Char(string="Tailscale IP", help="Tailscale VPN IP (e.g. 100.91.20.116)")
    vlan_id = fields.Selection([
        ('101', 'VLAN 101 - Server (10.1.0.0/24)'),
        ('102', 'VLAN 102 - DMZ'),
        ('103', 'VLAN 103 - DMZ Radio'),
        ('104', 'VLAN 104 - IoT (10.4.0.0/24)'),
        ('105', 'VLAN 105 - Guest (10.5.0.0/24)'),
        ('110', 'VLAN 110 - Stockenweiler'),
    ], string="VLAN Segment", default='101')

    pve_host = fields.Selection([
        ('stockenweiler-pve', 'stockenweiler-pve (HP ProDesk)'),
        ('proxmox-anker', 'proxmox-anker (Lenovo ThinkCentre)'),
        ('wolfstudiopc', 'wolfstudiopc (StudioPC Workstation)'),
        ('cloud', 'Cloud / Remote Provider'),
    ], string="Physical Host", default='stockenweiler-pve')

    vm_ct_id = fields.Char(string="CT / VM ID", help="Proxmox container or VM ID (e.g. CT140, VM210)")
    equipment_role = fields.Char(string="IT Function / Role", help="Primary function (e.g. Odoo Server, AzuraCast Master)")
    is_critical = fields.Boolean(string="Critical Infrastructure", default=False, help="Never turn off without maintenance window")
