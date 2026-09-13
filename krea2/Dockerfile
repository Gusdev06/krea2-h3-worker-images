# Krea 2 Turbo (imagem) com os modelos DENTRO da imagem: worker acorda em segundos em vez de carregar
# 18,6 GB do disco de rede (~80 s). Base: worker-comfyui 5.10.0 (ComfyUI 0.34) + handler corrigido
# (worker cujo ComfyUI morreu e descartado). Build pelo RunPod (Serverless > New Endpoint > GitHub Repo).
FROM runpod/worker-comfyui:5.10.0-base
COPY handler.py /handler.py
RUN comfy model download --url https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_fp8_scaled.safetensors --relative-path models/diffusion_models --filename krea2_turbo_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors --relative-path models/text_encoders --filename qwen3vl_4b_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors --relative-path models/vae --filename qwen_image_vae.safetensors

# LoRA "Realistic Snapshot" (Krea2 v0.5, CivitAI 2268008 / versao 3084537). O download direto da
# CivitAI exige token de conta; este espelho publico no HF e byte a byte o mesmo arquivo - o
# sha256sum abaixo e o hash publicado pela propria CivitAI, entao o build QUEBRA se o espelho mudar.
# Licenca do autor: uso comercial liberado (Image/Rent/Sell), sem credito obrigatorio.
RUN comfy model download --url https://huggingface.co/yufusoft/RealisticSnapshotKrea2/resolve/main/RealisticSnapshotKrea2.safetensors --relative-path models/loras --filename RealisticSnapshotKrea2.safetensors \
 && echo "dfd67eb881bec4caeb9409e5b7c127adcb9fb724e6007e1e77165af51e6f908d  /comfyui/models/loras/RealisticSnapshotKrea2.safetensors" | sha256sum -c -
