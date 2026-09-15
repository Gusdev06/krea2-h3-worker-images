# h3-aio — MiniMax H3 All-In-One (ref2va)

Prompt + **ate 9 imagens, 3 videos e 3 audios de referencia** -> video com audio nativo, 24 fps.
As referencias sao citadas dentro do proprio prompt como `<Picture i>`, `<Video k>` e `<Audio j>`
(numeracao 1-based por tipo, na ordem em que entram nos slots).

| | |
|---|---|
| Base | `runpod/worker-comfyui:5.10.0-base` (ComfyUI 0.34) |
| Diffusion model | `minimax_h3_hybrid_fl2va_ref2va_b25-49-int8` (21 GB) — checkpoint hibrido fl2va **+ ref2va** |
| Text encoder | Qwen3-VL 32B NVFP4 AWQ (15,7 GB) |
| Custom node | so **um**: [`Comfyui_Minimax_h3_latent_Upscaler`](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) (commit `d7c01b9`) |
| Peso total no build | ~42,5 GB |
| GPU | pool `BLACKWELL_96` (RTX PRO 6000 96 GB) — NVFP4 roda nativo so em Blackwell |
| Saida | MP4 com audio embutido |

## Por que nao e o `h3/`

O `h3/Dockerfile` carrega o checkpoint **fl2va puro**: primeiro/ultimo frame -> video. Este carrega o
**hibrido**, que e o que habilita o no `MiniMaxH3ReferenceToVideo` — varias referencias de imagem,
video e audio ao mesmo tempo. Os dois convivem; o `h3/` continua sendo o caminho de first/last-frame.

## Limites do modelo (do proprio workflow de referencia)

- Imagens: ate 9.
- Videos: ate 3 clipes, cada um de 2 a 15 s, somando no maximo 15 s.
- Audios: ate 3 clipes, 2 a 15 s cada. **Audio nao pode ser a unica entrada** — precisa vir junto de
  imagem ou video.
- Total: no maximo 12 arquivos somando todos os tipos.
- `length` e contagem de frames a 24 fps e tem que cair na grade **17k+5** (124 = ~5,2 s; a faixa
  treinada e ~124 a 362). O cliente arredonda pra cima sozinho.

## Duas etapas

O grafo amostra numa resolucao base leve (0,5 MP = 960x544), separa o latente AV, passa o latente de
video pelo `MinimaxH3LatentUpscaler3D` (upscale direto no latente de 24 canais, sem o round-trip
decode->upscale->encode, que e caro porque o VAE do H3 tem ~5B de parametros), reconcatena com o audio
e refina. O `SplitSigmas` e quem divide os passos entre as duas etapas — por isso existe um scheduler
so. **Etapa 1 precisa de 6 passos no minimo (8 pra audio bom) e a etapa 2, de 4.** O padrao e 12 = 8+4.

Tabela de resolucao do autor (aspecto 16:9, multiplo de 32): 0,5 MP = 960x544 · 1,0 MP = 1376x768 ·
1,5 MP = 1664x928 · 2,0 MP = 1920x1088.

## Publicar

1. RunPod -> **Serverless -> New Endpoint -> GitHub Repo** -> este repositorio.
2. Dockerfile path: `h3-aio/Dockerfile`.
3. GPU: **RTX PRO 6000 (96 GB)**, pool `BLACKWELL_96`. Em Ada o NVFP4 e emulado (~2,3x mais lento no
   encoder) e 48 GB fica apertado no refino a 2 MP.
4. Workers 0-2, idle timeout 300 s, **execution timeout 40 min**, FlashBoot ligado, sem network volume.
5. O build baixa ~42,5 GB e o limite do RunPod e 30 min por build. Cada modelo esta num `RUN` proprio
   pra que um rebuild reaproveite as camadas ja baixadas — se estourar o tempo, rode de novo.

## Chamar

Mesmo contrato do resto do repo: grafo do ComfyUI em `input.workflow`, arquivos em `input.images`
(o handler sobe qualquer arquivo pro `input/` do ComfyUI via `/upload/image`, que grava os bytes crus
sem validar o tipo — por isso `.wav` e `.mp4` funcionam nesse mesmo campo).

O cliente pronto e a aba **H3 AIO** do `apps/krea-studio` do AIOS, que monta o grafo abaixo.

```jsonc
{
  "input": {
    "images": [
      { "name": "refimg0.png", "image": "<base64>" },
      { "name": "refvid0.mp4", "image": "<base64>" },
      { "name": "refaud0.wav", "image": "<base64>" }
    ],
    "workflow": {
      "1":  { "class_type": "UNETLoader", "inputs": { "unet_name": "minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors", "weight_dtype": "default" } },
      // o workflow original traz um patch de sage attention aqui; a base nao tem sageattention e o
      // proprio autor diz que a atencao do comfy kitchen e igual ou mais rapida.
      "2":  { "class_type": "ModelAttentionBackend", "inputs": { "model": ["1", 0], "attention": "comfy kitchen attention" } },
      "5":  { "class_type": "LoraLoaderModelOnly", "inputs": { "model": ["2", 0], "lora_name": "minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors", "strength_model": 1 } },
      "6":  { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default" } },
      "7":  { "class_type": "VAELoader", "inputs": { "vae_name": "minimax_h3_video_vae_int8_convrot.safetensors" } },
      "8":  { "class_type": "VAELoader", "inputs": { "vae_name": "minimax_h3_audio_vae_fp32.safetensors" } },

      "101": { "class_type": "LoadImage", "inputs": { "image": "refimg0.png" } },
      "121": { "class_type": "LoadVideo", "inputs": { "file": "refvid0.mp4" } },
      "131": { "class_type": "GetVideoComponents", "inputs": { "video": ["121", 0] } },
      "141": { "class_type": "LoadAudio", "inputs": { "audio": "refaud0.wav" } },

      // Autogrow do ComfyUI 0.34: no formato de API as chaves dos slots sao PONTUADAS.
      "10": { "class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
                "clip": ["6", 0], "vae": ["7", 0], "audio_vae": ["8", 0],
                "prompt": "<Subject 1> is the woman from <Picture 1> ...",
                "width": 960, "height": 544, "length": 124,
                "ref_image_size": "max",
                "ref_images.ref_image_0": ["101", 0],
                "ref_videos.ref_video_0": ["131", 0],
                "ref_video_audios.ref_video_audio_0": ["131", 1],
                "ref_audios.ref_audio_0": ["141", 0] } },

      "11": { "class_type": "BasicGuider", "inputs": { "model": ["5", 0], "conditioning": ["10", 0] } },
      "12": { "class_type": "BasicScheduler", "inputs": { "model": ["5", 0], "scheduler": "beta", "steps": 12, "denoise": 1 } },
      "13": { "class_type": "SplitSigmas", "inputs": { "sigmas": ["12", 0], "step": 8 } },
      "14": { "class_type": "KSamplerSelect", "inputs": { "sampler_name": "euler" } },
      "15": { "class_type": "RandomNoise", "inputs": { "noise_seed": 42 } },
      // etapa 1: sigmas[0] = os 8 primeiros passos; saida 1 = denoised_output
      "16": { "class_type": "SamplerCustomAdvanced", "inputs": {
                "noise": ["15", 0], "guider": ["11", 0], "sampler": ["14", 0],
                "sigmas": ["13", 0], "latent_image": ["10", 1] } },

      "17": { "class_type": "LTXVSeparateAVLatent", "inputs": { "av_latent": ["16", 1] } },
      "18": { "class_type": "MinimaxH3LatentUpscaler3D", "inputs": {
                "latent": ["17", 0], "model_name": "minimax_h3_latent_upscaler_3d_fp16.safetensors",
                "mode": "megapixels", "mode.megapixels": 2,
                "align": 32, "enable_temporal_chunking": false, "force_unload": true,
                "device": "cuda", "precision": "fp16" } },
      "19": { "class_type": "LTXVConcatAVLatent", "inputs": { "video_latent": ["18", 0], "audio_latent": ["17", 1] } },
      // etapa 2: sigmas[1] = os 4 passos restantes, sobre o latente ja ampliado
      "20": { "class_type": "SamplerCustomAdvanced", "inputs": {
                "noise": ["15", 0], "guider": ["11", 0], "sampler": ["14", 0],
                "sigmas": ["13", 1], "latent_image": ["19", 0] } },

      "21": { "class_type": "VAEDecode", "inputs": { "samples": ["20", 1], "vae": ["7", 0] } },
      "22": { "class_type": "VAEDecodeAudio", "inputs": { "samples": ["20", 1], "vae": ["8", 0] } },
      "23": { "class_type": "CreateVideo", "inputs": { "images": ["21", 0], "fps": 24, "audio": ["22", 0] } },
      "24": { "class_type": "SaveVideo", "inputs": { "video": ["23", 0], "filename_prefix": "H3AllInOne", "format": "mp4", "codec": "h264" } }
    }
  },
  "policy": { "executionTimeout": 2400000, "ttl": 3600000 }
}
```

Sem a etapa 2 (mais rapido, resolucao base): apague os nos `17`-`20` e aponte `21.samples` e
`22.samples` pra `["16", 1]`.

## LoRAs na imagem

| arquivo | pra que | padrao |
|---|---|---|
| `minimax_h3_turbo_v4_step600_ema_pruned_comfyui` | e o que faz fechar em 12 passos | **1.0, sempre** |
| `wushu_spatial_physics_v2_1000_pruned` | fisica/movimento; vinha desligada no workflow original | 0 (ligue em ~0.3 pra testar) |
| `MysticXXX_MMH3-V1` | **NSFW**; vinha ligada em 0.5 no workflow original | **0** — enviesa a saida inteira |

Pra ligar, insira um `LoraLoaderModelOnly` na cadeia entre o no `2` e o no `5`.

## O que ficou de fora do workflow original

- `MiniMaxH3MemoryEfficientSageAttentionPatch` (KJNodes): exigiria compilar `sageattention` no build.
  Trocado pelo `ModelAttentionBackend` com `comfy kitchen attention`, que o proprio autor indica.
- `UniBlockSwap`: so serve pra rodar em 8 GB de VRAM, bem mais lento. Irrelevante num worker de 96 GB.
- `VHS_*` (VideoHelperSuite): trocados pelos nos nativos `LoadVideo` + `GetVideoComponents` e
  `CreateVideo` + `SaveVideo`, que o ComfyUI 0.34 ja tem. Uma dependencia a menos.
- `SetNode`/`GetNode` (KJNodes) e `Fast Groups Bypasser` (rgthree): sao so organizacao visual, somem
  na conversao pro formato de API.
