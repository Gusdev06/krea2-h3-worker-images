# bonsai-2-27b

Imagem Docker do **Ternary-Bonsai-2-27B** (Qwen3.8-27B em pesos ternários) para o RunPod Serverless:
LLM de raciocínio classe 27B em **7 GB**, 98,2% do FP16 nos benchmarks, rodando em GPU de 24 GB.
`llama-server` OpenAI-compatível atrás de um handler fino; **modelo dentro da imagem**, sem disco de
rede — worker acorda em segundos.

| | |
|---|---|
| Modelo | [`prism-ml/Ternary-Bonsai-2-27B-gguf`](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf), Apache-2.0 (uso comercial liberado) |
| Contexto | até 262 144 tokens (padrão aqui: 32 768 — `LLAMA_CTX`) |
| Runtime | **fork** [`PrismML-Eng/llama.cpp`](https://github.com/PrismML-Eng/llama.cpp), release `prism-b10709-9a9394a` (a pinada pelo [Bonsai-demo](https://github.com/PrismML-Eng/Bonsai-demo)), binário Linux CUDA 12.8 pré-compilado — **o llama.cpp comum rejeita/estraga esse GGUF** |
| Base | `nvidia/cuda:12.8.1-runtime-ubuntu22.04` |
| Pesos no build | PQ2_0 7,2 GB + mmproj Q8_0 0,63 GB (visão, desligada por padrão) |
| Modos | thinking (padrão: temp 1.0 / top-p 0.95 / top-k 20) ou instruct (`"thinking": false` → temp 0.7 / top-p 0.8) |

Decode medido pela PrismML (PQ2_0, batch 1): 4090 81 tok/s · L40S 74 · 6000 Ada 83 · H100 114 · L4 30.
Nas Ada/L4 o **PTQ1_0** (5,9 GB) decodifica ~10% mais rápido; o PQ2_0 ganha em H100/A100 e no
prompt processing em todas. Troque com `--build-arg MODEL_FILE=Ternary-Bonsai-2-27B-PTQ1_0.gguf`.

## Publicar

1. RunPod → **Serverless → New Endpoint → GitHub Repo** → `krea2-h3-worker-images`, Dockerfile path
   **`bonsai-2-27b/Dockerfile`**. (O deploy "direto do Hugging Face" do RunPod usa Ollama = llama.cpp
   comum e falha no `/api/create` com esse GGUF — testado em 22/09.)
2. GPU **24 GB** (RTX 4090 / L4 / A5000) já sobra: 7,2 GB de peso + 2 GB de KV a 32K. 48 GB só se
   quiser contexto de 100K+ (KV FP16 = 64 KiB/token → 6,3 GB em 100K) — ou ligue `LLAMA_KV4=1`.
3. Workers 0–3, idle timeout 60–300 s, FlashBoot ligado, sem network volume.
4. O RunPod reconstrói a cada push. O build baixa ~8 GB (binário 167 MB + pesos), bem dentro dos 30 min.

Variáveis de ambiente do endpoint (nenhuma exige rebuild):

| Var | Padrão | Pra quê |
|---|---|---|
| `LLAMA_CTX` | `32768` | tamanho do contexto (até 262144) |
| `LLAMA_PARALLEL` | `1` | slots simultâneos no mesmo worker; o contexto é dividido entre eles |
| `LLAMA_MMPROJ` | `0` | `1` carrega a torre de visão (+0,9 GB VRAM) e aceita imagem nas mensagens |
| `LLAMA_KV4` | `0` | `1` = KV cache q4_0 (~3,5× menos memória de contexto) |
| `LLAMA_EXTRA_ARGS` | `` | flags extras do llama-server, ex.: `--reasoning-budget 2048` |

## Como chamar

### 1. URL OpenAI do endpoint (recomendado)

Qualquer SDK OpenAI, só trocando `base_url` e a chave:

```python
from openai import OpenAI
client = OpenAI(base_url=f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1", api_key=RUNPOD_API_KEY)
r = client.chat.completions.create(
    model="bonsai",  # ignorado; o worker tem um modelo só
    messages=[{"role": "user", "content": "Explain quantum computing in simple terms."}],
    max_tokens=512,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},  # omita pra deixar pensar
)
print(r.choices[0].message.content)
```

Com `stream=True` vem token a token. O raciocínio (quando ligado) chega em `reasoning_content`,
separado do `content`. Rotas aceitas: `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`,
`/v1/models`.

### 2. `/run` · `/runsync` · `/stream` (input simples)

```bash
curl -X POST https://api.runpod.ai/v2/$ENDPOINT_ID/runsync \
  -H "authorization: Bearer $RUNPOD_API_KEY" -H "content-type: application/json" \
  -d '{"input": {"prompt": "Explain quantum computing in one paragraph.", "thinking": false, "max_tokens": 400}}'
```

`input` aceita `prompt` (+ `system`) **ou** `messages` no formato OpenAI, mais `temperature`,
`top_p`, `top_k`, `max_tokens`, `stop`, `tools`, `response_format`, `stream`, `thinking`. Tudo vai
direto pro `/v1/chat/completions` do llama-server. O handler é um gerador (pra `/stream` funcionar),
então o `output` de `/runsync` é **uma lista** — um item com a resposta inteira sem stream, ou um
item por chunk SSE com `"stream": true`. Erro vem como `[{"error": "..."}]`.

## Estrutura

- `Dockerfile` — (contexto de build = raiz do monorepo) base CUDA, binário do fork, pesos (`ARG MODEL_FILE`, `ARG MMPROJ_FILE`).
- `start.sh` — sobe o `llama-server` com os mesmos flags do `start_llama_server.sh` do Bonsai-demo
  (`-ngl 99 -fa on --jinja`, sampling de thinking) e depois o handler.
- `handler.py` — espera o `/health`, faz proxy (com SSE) e devolve erro legível se o servidor morrer.
- `test_input.json` — pedido de exemplo pro teste local: rodando `python3 handler.py` sem o RunPod, o SDK
  lê esse arquivo do diretório atual (precisa do `llama-server` de pé numa GPU).

## Atualizar o fork / o modelo

O Bonsai-demo é a fonte da verdade dos flags e da release; quando ele mudar a tag pinada, troque
`ARG LLAMA_RELEASE` e confira se o tarball `linux-cuda-12.8-x64` existe na nova release (às vezes
sai depois dos outros). Quantizações novas (`Q2_g64`, drafter `dspark-dflash` pra especulação) entram
por `ARG MODEL_FILE` / `LLAMA_EXTRA_ARGS`.
