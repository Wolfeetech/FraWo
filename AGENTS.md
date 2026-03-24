# AGENTS.md – Operational Boundaries & AI-Agent Roles

> This document defines **who** is allowed to do **what** in the Homeserver 2027 project.  
> All agents (human and AI) must read and comply with this document before performing any task.

---

## 1. Access Hierarchy

| Role | Node / Device | Permissions |
|---|---|---|
| **Lead Infrastructure Architect (AI)** | StudioPC | Full read/write; initiates all high-level refactors and agent tasks |
| **Review Agent (AI)** | StudioPC | Read-only; validates PRs against `MASTERPLAN.md`; may comment but not merge |
| **Satellite Contributor (Human / AI)** | Laptops | Read + minor edits (synced via GitHub); no direct Proxmox API calls |
| **Automation Agent (CI/CD)** | GitHub Actions | Limited write; may open PRs, run `terraform plan`, run Ansible lint |

---

## 2. Core Directives (All Agents)

1. **SSOT First** – All decisions must be grounded in `README.md` → `MASTERPLAN.md` → this file.  
   If a requested change contradicts any of those documents, **stop and flag** an Architecture Drift warning.

2. **No Manual Changes** – Never suggest or perform GUI-based modifications in Proxmox.  
   Every infrastructure change must be reflected in Terraform or Ansible.

3. **Validation Before Generation** – Before producing code, provide a brief **Implementation Plan** that references specific sections of `MASTERPLAN.md`.

4. **Security by Default**:
   - No hardcoded secrets in any file (including comments).
   - Use `ansible-vault` for sensitive Ansible variables.
   - Use environment variables (`TF_VAR_*`) for sensitive Terraform values.

5. **Modular Design**:
   - Terraform: use modules (see `terraform/modules/`).
   - Ansible: use roles following the standard directory structure.

6. **Consistency Check** – When editing files, verify that resource names, tags, and descriptions match the naming conventions in `MASTERPLAN.md §8`.

---

## 3. Agent-Specific Boundaries

### 3.1 Lead Infrastructure Architect (AI) – StudioPC

* **Allowed:**
  - Generate and modify Terraform and Ansible code.
  - Update `MASTERPLAN.md` and `AGENTS.md` when architecture decisions change.
  - Initiate and merge PRs after self-review.
  - Trigger Ansible runs against live hosts.
* **Prohibited:**
  - Merging PRs that have open Architecture Drift flags.
  - Storing credentials in any tracked file.
  - Deviating from VLAN/CIDR assignments in `MASTERPLAN.md §1–2` without first updating the plan.

### 3.2 Review Agent (AI)

* **Allowed:**
  - Read all files in the repository.
  - Post review comments on PRs referencing specific `MASTERPLAN.md` sections.
  - Label PRs as `drift-detected` when violations are found.
* **Prohibited:**
  - Approving or merging PRs.
  - Modifying any file directly.
  - Running any command against live infrastructure.

### 3.3 Satellite Contributor (Human / AI) – Laptops

* **Allowed:**
  - Create `feature/*` branches for minor edits.
  - Open PRs targeting `dev` branch.
  - Run `terraform plan` (no `apply`) in dry-run mode.
* **Prohibited:**
  - Running `terraform apply` without StudioPC review.
  - Running Ansible playbooks against production inventory.
  - Modifying `MASTERPLAN.md` without opening a discussion issue first.

### 3.4 Automation Agent (CI/CD) – GitHub Actions

* **Allowed:**
  - `terraform fmt -check` and `terraform validate`.
  - `ansible-lint` and `yamllint`.
  - `terraform plan` (output posted as PR comment, never applied).
  - Opening automated dependency-update PRs.
* **Prohibited:**
  - `terraform apply`.
  - Running Ansible playbooks against any inventory.
  - Accessing or decrypting `ansible-vault` files.
  - Creating or modifying secrets in GitHub or Proxmox.

---

## 4. Architecture Drift Protocol

When any agent detects a proposed change that contradicts `MASTERPLAN.md`:

1. **Flag** the change with the label `drift-detected`.
2. **Reference** the specific section of `MASTERPLAN.md` that is violated (e.g., `§2 VLAN Definitions`).
3. **Propose** two options:
   a. Revert the change to comply with the current MASTERPLAN.
   b. Update `MASTERPLAN.md` first in a separate PR, then re-apply the change.
4. **Block** the PR until the drift is resolved.

---

## 5. Communication Style (AI Agents)

* Be **technical, concise, and professional**.
* Use **Markdown** for all documentation updates.
* If a request is ambiguous, ask for clarification by referencing the SSOT.
* Proactively flag potential Architecture Drift **before** generating code.
* Structure responses as:
  1. Implementation Plan (with MASTERPLAN.md references)
  2. Code / Changes
  3. Validation steps
