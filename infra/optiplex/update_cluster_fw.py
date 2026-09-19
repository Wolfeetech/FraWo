import re, subprocess

path = "/etc/pve/firewall/cluster.fw"
with open(path, "r") as f:
    lines = f.readlines()

new_lines = []
already_has_lan = any("10.0.0.0/24" in l and "11434" in l for l in lines)
already_has_srv = any("10.1.0.0/24" in l and "11434" in l for l in lines)

for line in lines:
    new_lines.append(line)
    if "Default-LAN: PVE-UI" in line and not already_has_lan:
        new_lines.append("IN ACCEPT -source 10.0.0.0/24 -p tcp -dport 11434 -log nolog   # Ollama API StudioPC & LAN\n")
        already_has_lan = True
    if "PBS-Backup-API" in line and not already_has_srv:
        new_lines.append("IN ACCEPT -source 10.1.0.0/24 -p tcp -dport 11434 -log nolog   # Ollama API CT110 & CT140\n")
        already_has_srv = True

with open(path, "w") as f:
    f.writelines(new_lines)

print("FILE_UPDATED_SUCCESSFULLY")
