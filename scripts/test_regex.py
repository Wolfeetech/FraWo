import re

PROJECTS = {
    "Lane A": 2, "Lane B": 3, "Lane C": 4, "Lane D": 5, "Lane E": 9,
    "FraWo_GbR": 12, "Villa Bienert": 10, "Anker_Lounge": 11, "Masterplan": 1
}

PROJECT_RULES = [
    (PROJECTS["FraWo_GbR"], ["gbr", "gründung", "steuer", "finanzamt", "konto", "notar", "rechnung", "vertrag", "agb", "impressum", "business", "quonto", "qonto", "gesellschafter"]),
    (PROJECTS["Villa Bienert"], ["villa", "bienert", "einbau", "werkstatt", "holz", "strom", "bohren", "schreinerei", "schrank", "toilette"]),
    (PROJECTS["Anker_Lounge"], ["studio", "anker", "lounge", "dj", "pult", "controller", "led", "growbox"]),
    (PROJECTS["Lane A"], ["openclaw", "agent", "llm", "ai", "aiops", "caretaker", "heritage", "history", "python", "script"]),
    (PROJECTS["Lane B"], ["website", "public edge", "domain", "ssl", "cloudflare", "html", "css", "deploy", "caddy", "frontend", "homepage"]),
    (PROJECTS["Lane C"], ["security", "backup", "pbs", "proxmox backup", "vlan", "firewall", "passwort", "vaultwarden", "dns", "adguard"]),
    (PROJECTS["Lane D"], ["stockenweiler", "home assistant", "haos", "eltern", "smart home"]),
    (PROJECTS["Lane E"], ["radio", "azuracast", "musik", "stream", "funk", "sendung", "media", "jellyfin", "mp3", "obs", "video"])
]

def has_keyword(text: str, keywords: list[str]) -> bool:
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            return True
    return False

def get_project_by_keywords(text: str) -> int:
    text = text.lower()
    for pid, keywords in PROJECT_RULES:
        if has_keyword(text, keywords):
            return pid
    return PROJECTS["Masterplan"]

print(get_project_by_keywords("[Lane D] Stockenweiler Integration (ACTIVE)"))
print(get_project_by_keywords("[Lane A] OpenClaw Agent & Control (ACTIVE)"))
print(get_project_by_keywords("[Website Legal] Datenschutzerklärung erstellen"))
