#!/usr/bin/env bash
# Sobe o llama-server do fork em background (flags iguais ao scripts/start_llama_server.sh do
# Bonsai-demo, modo thinking) e depois o handler do RunPod, que faz proxy pra ele.
set -euo pipefail

ARGS=(
  -m "$MODEL_PATH"
  --host 127.0.0.1 --port "$LLAMA_PORT"
  -ngl "$LLAMA_NGL" -fa on
  -c "$LLAMA_CTX" -np "$LLAMA_PARALLEL"
  --jinja
  --temp 1.0 --top-p 0.95 --top-k 20
  --no-webui
)
# visao: ~0,9 GiB de VRAM a mais; so quando pedirem imagem
if [ "${LLAMA_MMPROJ:-0}" = "1" ] && [ -f "$MMPROJ_PATH" ]; then
  ARGS+=(--mmproj "$MMPROJ_PATH")
fi
# KV cache 4-bit (~3,5x menos memoria de contexto) - ver KV-CACHE.md do Bonsai-demo
if [ "${LLAMA_KV4:-0}" = "1" ]; then
  ARGS+=(--cache-type-k q4_0 --cache-type-v q4_0)
fi
# shellcheck disable=SC2206
ARGS+=(${LLAMA_EXTRA_ARGS:-})

echo "[start] llama-server ${ARGS[*]}"
/opt/llama/llama-server "${ARGS[@]}" &
echo $! > /tmp/llama-server.pid

exec python3 -u /handler.py
