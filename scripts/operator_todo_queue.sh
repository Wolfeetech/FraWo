#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TODO_PATH="${ROOT_DIR}/DOCS/Task_Archive/OPERATOR_TODO_QUEUE.md"

echo "operator_todo_queue=$(realpath "${TODO_PATH}")"
echo
sed -n '/^### Blocked$/,/^### Next$/p' "${TODO_PATH}" | sed '$d'
echo
sed -n '/^### Next$/,/^### Doing$/p' "${TODO_PATH}" | sed '$d'
echo
sed -n '/^### Doing$/,/^### Done$/p' "${TODO_PATH}" | sed '$d'
