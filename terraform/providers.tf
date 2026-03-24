# ---------------------------------------------------------------------------
# providers.tf – bpg/proxmox provider configuration
# ---------------------------------------------------------------------------
# Credentials are supplied exclusively via environment variables:
#   PROXMOX_VE_ENDPOINT  – e.g. https://pve-01.lan:8006
#   PROXMOX_VE_API_TOKEN – e.g. terraform@pve!provider=<uuid>:<secret>
#   PROXMOX_VE_INSECURE  – set to "true" only when using self-signed certs
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.53"
    }
  }
}

provider "proxmox" {
  # Endpoint and API token are read from environment variables:
  # PROXMOX_VE_ENDPOINT and PROXMOX_VE_API_TOKEN
  # No credentials are set here to prevent accidental secret exposure.
}
