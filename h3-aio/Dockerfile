# MiniMax H3 All-In-One (ref2va): prompt + ate 9 imagens, 3 videos e 3 audios de referencia -> video
# com audio nativo, em duas etapas (amostragem base + upscale de latente). Modelos DENTRO da imagem,
# no mesmo padrao de krea2/, h3/, ideogram4/ e qwen-edit/.
#
# Diferenca pro h3/: aquele carrega o checkpoint fl2va puro (primeiro/ultimo frame -> video). Este usa
# o checkpoint HIBRIDO fl2va+ref2va, que e o que habilita o no MiniMaxH3ReferenceToVideo - varias
# referencias de imagem/video/audio ao mesmo tempo, citadas no prompt como <Picture i>, <Video k> e
# <Audio j>. O h3/ continua valendo pra first/last-frame; este substitui ele pra tudo mais.
#
# ~42,5 GB de peso. O limite de build do RunPod e 30 min: cada modelo vai em um RUN proprio pra que um
# rebuild reaproveite as camadas ja baixadas.
FROM runpod/worker-comfyui:5.10.0-base
COPY handler.py /handler.py

# --- custom node: Minimax H3 Latent Upscaler ------------------------------------------------------
# O MinimaxH3LatentUpscaler3D e o unico no do grafo que NAO existe no ComfyUI 0.34 que a base traz.
# Ele faz o upscale direto no latente de 24 canais, pulando o decode->upscale->encode (o VAE do H3 tem
# ~5B de parametros, o round-trip e caro). Commit fixado pra o build ser reprodutivel.
# Sem requirements.txt: o no usa so torch/numpy, que a base ja tem.
RUN git clone https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler.git /comfyui/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler \
 && cd /comfyui/custom_nodes/Comfyui_Minimax_h3_latent_Upscaler \
 && git checkout d7c01b9011f2e8439493f6c02c29995a27df276f

# --- diffusion model: checkpoint hibrido fl2va + ref2va (int8) -------------------------------------
# b25-49 = os blocos 25 a 49 vem do ref2va; o repo tem tambem b15-49, b20-49 e b30-49 (mesmo tamanho),
# que deslocam o equilibrio entre fidelidade a referencia e liberdade de movimento.
RUN comfy model download --url https://huggingface.co/smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models/resolve/main/minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors --relative-path models/diffusion_models --filename minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors

# --- text encoder: Qwen3-VL 32B em NVFP4 ----------------------------------------------------------
# NVFP4 roda nativo em Blackwell (RTX PRO 6000, 5090, B200). Em Ada/Ampere ele e emulado e o encoder
# fica ~2,3x mais lento - por isso o endpoint vai no pool BLACKWELL_96.
RUN comfy model download --url https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors --relative-path models/text_encoders --filename qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors

# --- VAEs: video (int8 convrot, do Kijai) e audio (fp32, da Comfy-Org) ----------------------------
RUN comfy model download --url https://huggingface.co/Kijai/MiniMax-H3-experimental/resolve/main/minimax_h3_video_vae_int8_convrot.safetensors --relative-path models/vae --filename minimax_h3_video_vae_int8_convrot.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors --relative-path models/vae --filename minimax_h3_audio_vae_fp32.safetensors

# --- LoRAs ----------------------------------------------------------------------------------------
# Turbo v4: e o que faz o grafo fechar em 12 passos no total (8 na etapa 1 + 4 no upscale). Sempre 1.0.
RUN comfy model download --url https://huggingface.co/drbaph/MiniMax-H3-Turbo-Lora-ComfyUI/resolve/main/minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors --relative-path models/loras --filename minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors
# Spatial physics: vinha desligada no workflow de referencia; 160 MB, fica disponivel pra teste (0.3).
RUN comfy model download --url https://huggingface.co/Jojocodex/minimax-h3-spatial-physics-lora/resolve/main/wushu_spatial_physics_v2_1000_pruned.safetensors --relative-path models/loras --filename wushu_spatial_physics_v2_1000_pruned.safetensors
# MysticXXX: LoRA NSFW que vinha ligada em 0.5 no workflow original. Fica na imagem, mas o cliente
# manda strength 0 por padrao - ela so entra no grafo quando pedida explicitamente.
RUN comfy model download --url https://huggingface.co/noname1992/loras/resolve/main/MysticXXX_MMH3-V1.safetensors --relative-path models/loras --filename MysticXXX_MMH3-V1.safetensors

# --- modelo do upscaler de latente ----------------------------------------------------------------
# O custom node procura em models/latent_upscale_models/.
RUN comfy model download --url https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/main/minimax_h3_latent_upscaler_3d_fp16.safetensors --relative-path models/latent_upscale_models --filename minimax_h3_latent_upscaler_3d_fp16.safetensors
