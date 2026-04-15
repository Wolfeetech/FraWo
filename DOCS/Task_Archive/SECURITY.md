# Security Policy – Homeserver 2027 Ops Workspace

## Secret Handling

### Golden Rule

**Never commit plaintext secrets to this repository.**

All secrets belong in one of:
1. The Ansible Vault file (`ansible/inventory/group_vars/all/vault.yml`) – committed, always encrypted.
2. A local gitignored file (e.g. `.vault_pass`, `mail_runtime.local.yml`).
3. Environment variables (never written to disk).

### Files and Their Status

| File | Committed? | Contains |
|------|-----------|---------|
| `ansible/inventory/group_vars/all/vault.yml` | ✅ Yes (encrypted) | All service secrets |
| `.vault_pass` | ❌ No (gitignored) | Vault decryption password |
| `.vault_pass.example` | ✅ Yes (template) | Placeholder only |
| `ansible/inventory/group_vars/all/mail_runtime.local.yml` | ❌ No (gitignored) | Live SMTP password |
| `ansible/inventory/group_vars/all/mail_runtime.local.yml.example` | ✅ Yes (template) | Structure only |

### Local Setup (New Workstation)

1. Clone the repo.
2. Set up the vault password:
   ```bash
   cp .vault_pass.example .vault_pass
   # Edit .vault_pass and insert the real vault password
   chmod 600 .vault_pass
   ```
3. Verify Ansible can decrypt:
   ```bash
   ansible-vault view ansible/inventory/group_vars/all/vault.yml
   ```
4. For SMTP (if needed):
   ```bash
   cp ansible/inventory/group_vars/all/mail_runtime.local.yml.example \
      ansible/inventory/group_vars/all/mail_runtime.local.yml
   # Edit with real credentials
   ```

### Reporting a Secret Leak

If a secret was accidentally committed:

1. **Immediately rotate the secret** (change the password / revoke the token).
2. Remove it from the repo:
   ```bash
   git rm --cached <file>
   echo '<file>' >> .gitignore
   git commit -m "security: stop tracking <file>"
   ```
3. To purge from git history (requires `git-filter-repo` or BFG):
   ```bash
   git filter-repo --path <file> --invert-paths
   ```
   Then force-push and notify all collaborators.
4. Document the incident in `MEMORY.md` under `## Security Events`.

### Security Baseline

Run the daily security check:

```bash
make security-baseline-check
```

See [`SECURITY_BASELINE.md`](SECURITY_BASELINE.md) for the full posture and findings.

### What Is Not a Secret

The following are safe to commit:
- Ansible playbooks and roles
- Host inventory (`ansible/inventory/hosts.yml`) – contains hostnames/IPs but no passwords
- Terraform variable **definitions** (`variables.tf`) – but not `.tfvars` with real values
- This file and other markdown documentation
- Docker Compose templates without embedded credentials
