#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "operator_todo_queue=$(realpath "${ROOT_DIR}/OPERATOR_TODO_QUEUE.md")"
echo
sed -n '/^## Now$/,/^## Soon$/p' "${ROOT_DIR}/OPERATOR_TODO_QUEUE.md" | sed '$d'
echo
sed -n '/^## Soon$/,/^## Later$/p' "${ROOT_DIR}/OPERATOR_TODO_QUEUE.md" | sed '$d'
echo
sed -n '/^## Later$/,/^## Canonical Detail Sources$/p' "${ROOT_DIR}/OPERATOR_TODO_QUEUE.md" | sed '$d'
