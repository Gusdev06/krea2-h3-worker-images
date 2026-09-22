"""Handler RunPod Serverless: proxy fino sobre o llama-server (OpenAI-compatível).

Dois jeitos de chamar:
  1. /run, /runsync: {"input": {"messages": [...], "max_tokens": 512, "thinking": false, ...}}
  2. URL OpenAI do endpoint (https://api.runpod.ai/v2/<ID>/openai/v1/chat/completions), que o
     RunPod entrega aqui como input.openai_route + input.openai_input — sem tradução nenhuma.

O handler é um gerador: com "stream": true cada chunk SSE do llama-server vira um item do /stream;
sem stream, um único item com a resposta inteira. Por isso o output de /runsync é sempre uma lista.
"""
import json
import os
import time

import requests
import runpod

PORT = int(os.environ.get("LLAMA_PORT", "8080"))
BASE = f"http://127.0.0.1:{PORT}"
PID_FILE = "/tmp/llama-server.pid"
# tempo máximo pro modelo carregar na VRAM. Com o GGUF na imagem e FlashBoot costuma ser < 30 s.
READY_TIMEOUT = int(os.environ.get("LLAMA_READY_TIMEOUT", "600"))

# rotas OpenAI que o llama-server expõe; qualquer outra vira erro em vez de proxy cego
ALLOWED_ROUTES = {
    "/v1/chat/completions",
    "/v1/completions",
    "/v1/embeddings",
    "/v1/models",
}
# chaves do input "simples" que vão direto pro corpo do chat/completions
PASSTHROUGH = (
    "messages", "temperature", "top_p", "top_k", "min_p", "max_tokens", "stop", "seed",
    "presence_penalty", "frequency_penalty", "repeat_penalty", "tools", "tool_choice",
    "response_format", "reasoning_effort", "reasoning_budget", "chat_template_kwargs",
    "n_probs", "logprobs", "top_logprobs", "stream",
)


def _server_alive():
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def wait_ready():
    """Espera o /health responder 200 (503 enquanto carrega). Se o processo morrer, desiste."""
    deadline = time.time() + READY_TIMEOUT
    while time.time() < deadline:
        try:
            if requests.get(f"{BASE}/health", timeout=2).status_code == 200:
                return True
        except requests.RequestException:
            pass
        if not _server_alive():
            raise RuntimeError("llama-server morreu antes de ficar pronto (ver log do worker)")
        time.sleep(0.5)
    raise RuntimeError(f"llama-server não ficou pronto em {READY_TIMEOUT}s")


def _build_chat_body(inp):
    body = {k: inp[k] for k in PASSTHROUGH if k in inp}
    if "messages" not in body:
        prompt = inp.get("prompt")
        if not prompt:
            raise ValueError("input precisa de 'messages' (lista OpenAI) ou 'prompt' (string)")
        msgs = []
        if inp.get("system"):
            msgs.append({"role": "system", "content": inp["system"]})
        msgs.append({"role": "user", "content": prompt})
        body["messages"] = msgs
    # thinking=false: desliga o raciocínio (modo instruct do model card)
    if inp.get("thinking") is False:
        kw = dict(body.get("chat_template_kwargs") or {})
        kw["enable_thinking"] = False
        body["chat_template_kwargs"] = kw
        body.setdefault("temperature", 0.7)
        body.setdefault("top_p", 0.8)
    return body


def _proxy(route, body, method="POST"):
    stream = bool(body.get("stream")) if isinstance(body, dict) else False
    url = f"{BASE}{route}"
    if method == "GET":
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        yield r.json()
        return
    r = requests.post(url, json=body, stream=stream, timeout=(10, 3600))
    if r.status_code >= 400:
        raise RuntimeError(f"llama-server {r.status_code}: {r.text[:2000]}")
    if not stream:
        yield r.json()
        return
    # SSE: "data: {...}" por linha; "[DONE]" fecha
    for line in r.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        yield json.loads(payload)


def handler(job):
    inp = job.get("input") or {}
    try:
        route = inp.get("openai_route")
        if route:
            if route not in ALLOWED_ROUTES:
                raise ValueError(f"rota não suportada: {route}")
            method = "GET" if route == "/v1/models" else "POST"
            yield from _proxy(route, inp.get("openai_input") or {}, method)
        else:
            yield from _proxy("/v1/chat/completions", _build_chat_body(inp))
    except Exception as e:  # noqa: BLE001 - erro vira output legível em vez de 500 mudo
        yield {"error": str(e)}


if __name__ == "__main__":
    wait_ready()
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True,
    })
