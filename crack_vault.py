import subprocess
import os

VAULT_FILE = r"C:\WORKSPACE\FraWo\ansible\inventory\group_vars\all\vault.yml"
PASSWORDS = [
    "Hs27Storage2026!",
    "FraWo2026!",
    "FraWo2027!",
    "Hs27!2026",
    "Hs27!2027",
    "frawo",
    "wolf",
    "Hs27Ops2027!",
    "Hs27Ops2026!"
]

def try_passwords():
    for pw in PASSWORDS:
        print(f"Trying: {pw}")
        try:
            # Use ansible-vault to check the password
            with open("temp_pass", "w") as f:
                f.write(pw)
            
            result = subprocess.run(
                ["ansible-vault", "view", VAULT_FILE, "--vault-password-file", "temp_pass"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"SUCCESS! Password is: {pw}")
                return pw
            else:
                print(f"Failed: {result.stderr.strip()}")
        finally:
            if os.path.exists("temp_pass"):
                os.remove("temp_pass")
    return None

if __name__ == "__main__":
    try_passwords()
