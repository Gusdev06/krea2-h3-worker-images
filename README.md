# krea2-h3-worker-images

Imagens Docker para o RunPod Serverless com os modelos embutidos (nada de disco de rede):

- `krea2/Dockerfile`: Krea 2 Turbo, imagem. 18,6 GB de modelo.
- `h3/Dockerfile`: MiniMax H3, video com audio. 43 GB de modelo.

Os dois usam `runpod/worker-comfyui:5.10.0-base` e o `handler.py` corrigido (worker cujo ComfyUI morreu
devolve `refresh_worker` e e descartado). Cliente, pagina e validacao: repositorio `krea2-comfy-api`.

## Como publicar (painel do RunPod, conta com o GitHub conectado)

1. Fork deste repositorio na sua conta do GitHub.
2. Serverless > New Endpoint > GitHub Repo > escolha o fork.
3. Endpoint de imagem: Dockerfile path `krea2/Dockerfile`, GPU 24 GB (4090, 5090, e as de 48 GB como reserva),
   workers 0 a 6, idle timeout 300 s, FlashBoot ligado. Sem network volume.
4. Endpoint de video: Dockerfile path `h3/Dockerfile`, GPU 48 GB (L40S, L40, A6000, A40, 6000 Ada), depois 5090
   e 80 GB, 4090 por ultimo como reserva; workers 0 a 4, idle 300 s, execution timeout 40 min. Sem volume.
5. O RunPod constroi (limite de 30 min por build) e reconstroi a cada push na branch.
