# FraWo AI Toolkit & MCP Guide

This guide defines the professional usage of the **AI Toolkit for VS Code** and the **Model Context Protocol (MCP)** within the FraWo estate.

## 1. Environment Setup

### System Prerequisites
- **Hardware**: NVIDIA RTX 4060 (StudioPC) or DirectML-compatible GPU.
- **Extensions**: Ensure the **AI Toolkit for VS Code** (`ms-windows.ai-toolkit`) is installed (see Workspace Recommendations).
- **Python**: The `mcp[cli]` package must be installed in the environment used for business scripts.

### Model Provisioning
1. Open the AI Toolkit (Robot icon in the activity bar).
2. Browse for **Phi-3-mini-4k-instruct-onnx**.
3. Download the model to `C:\AI_MODELS\FraWo` (configured in `.vscode/settings.json`).
4. Select "Load Model" to start the local LLM server.

## 2. Model Context Protocol (MCP) Integration

The FraWo estate uses a custom MCP server to bridge AI with our Odoo instance.

### Canonical Server Info
- **Server Name**: `Odoo Professional MCP`
- **Script path**: `scripts/business/mcp_odoo_pro_server.py`
- **Configuration**: Shared via `mcp_config.json` and `.vscode/settings.json`.

### Available Tools
- `ensure_mission_lanes`: Synchronizes the 5 authoritative FraWo projects in Odoo.
- `activate_discount_feature`: Enables professional billing features.
- `reclaim_tasks`: Automatically categorizes tasks into mission lanes.

## 3. Workflow Best Practices

### Professional Preflight
Before performing major infrastructure shifts, use the local AI Toolkit with the Odoo MCP server to:
1. "Draft the mission lanes for the next rollout."
2. "Analyze open tasks in Odoo and propose a reclaim strategy."

### Satellite Node Usage
On Satellites (Surface), if local GPU performance is insufficient:
1. Connect via SSH to the **StudioPC**.
2. Run the AI Toolkit server on the StudioPC.
3. Access the remote endpoint from the Surface VS Code instance.

---
*Status: Active*
*Last Update: 2026-04-20*
