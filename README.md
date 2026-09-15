# krea2-h3-worker-images

Imagens Docker para o RunPod Serverless com os modelos embutidos (nada de disco de rede):

- `krea2/Dockerfile`: Krea 2 Turbo, imagem. 18,6 GB de modelo + a LoRA "Realistic Snapshot"
  (CivitAI 2268008 v3084537, 229 MB) puxada de um espelho publico no HF com conferencia de sha256
  contra o hash publicado pela CivitAI.
- `h3/Dockerfile`: MiniMax H3 fl2va, video com audio a partir do primeiro/ultimo frame. 43 GB de modelo.
- `h3-aio/Dockerfile`: **MiniMax H3 All-In-One (ref2va)**, o checkpoint HIBRIDO fl2va+ref2va: prompt +
  ate 9 imagens, 3 videos e 3 audios de referencia -> video com audio, citando cada referencia no
  proprio prompt como `<Picture i>` / `<Video k>` / `<Audio j>`. ~42,5 GB. Duas etapas (base +
  upscale do latente). Unico custom node: `Comfyui_Minimax_h3_latent_Upscaler`. Detalhe, limites do
  modelo e o grafo em formato de API: `h3-aio/README.md`.
- `ideogram4/Dockerfile`: Ideogram 4, imagem. ~32 GB de modelo (dois checkpoints: condicional +
  unconditional, encoder Qwen3-VL 8B, VAE do Flux 2) mais o custom node RES4LYF (sampler `res_2m`) e
  as LoRAs Realism Engine Ideogram V5 e V4. **Licenca NAO COMERCIAL** (ideogram-non-commercial-model-
  agreement) - endpoint de teste/avaliacao, nao use a saida em anuncio ou entrega de cliente.
- `qwen-edit/Dockerfile`: Qwen-Image-Edit 2511, edicao por instrucao ("mesma pessoa, troca a roupa").
  ~31 GB de modelo. Apache-2.0. Resolve o que o img2img do Krea 2 nao resolve: a imagem de referencia
  entra como condicionamento (`TextEncodeQwenImageEditPlus` -> `reference_latents`), entao a identidade
  se mantem em vez de ser reinventada. Traz as LoRAs Lightning de 4 e 8 passos (treinadas no Edit 2509,
  nao no 2511 - use como teste A/B).

Os dois usam `runpod/worker-comfyui:5.10.0-base` e o `handler.py` corrigido (worker cujo ComfyUI morreu
devolve `refresh_worker` e e descartado). Cliente, pagina e validacao: repositorio `krea2-comfy-api`.

## Como publicar (painel do RunPod, conta com o GitHub conectado)

1. Fork deste repositorio na sua conta do GitHub.
2. Serverless > New Endpoint > GitHub Repo > escolha o fork.
3. Endpoint de imagem: Dockerfile path `krea2/Dockerfile`, GPU 24 GB (4090, 5090, e as de 48 GB como reserva),
   workers 0 a 6, idle timeout 300 s, FlashBoot ligado. Sem network volume.
4. Endpoint de video: Dockerfile path `h3/Dockerfile`, GPU 48 GB (L40S, L40, A6000, A40, 6000 Ada), depois 5090
   e 80 GB, 4090 por ultimo como reserva; workers 0 a 4, idle 300 s, execution timeout 40 min. Sem volume.
5. Endpoint de edicao: Dockerfile path `qwen-edit/Dockerfile`, GPU 48 GB (mesma familia do video),
   workers 0 a 4, idle 300 s, execution timeout 10 min. Sem volume.
6. Endpoint do Ideogram 4: Dockerfile path `ideogram4/Dockerfile`, GPU 48 GB, workers 0 a 2,
   idle 300 s, execution timeout 15 min. Sem volume.
7. Endpoint do H3 All-In-One: Dockerfile path `h3-aio/Dockerfile`, GPU **96 GB** (RTX PRO 6000, pool
   `BLACKWELL_96` - o text encoder e NVFP4 e so Blackwell roda isso nativo), workers 0 a 2, idle 300 s,
   execution timeout 40 min. Sem volume.
8. O RunPod constroi (limite de 30 min por build) e reconstroi a cada push na branch.

## Lipsync

O worker de lipsync (Wan 2.2 S2V 14B, foto + audio -> video falando) mora em um repositorio proprio:
https://github.com/Gusdev06/wan-s2v
