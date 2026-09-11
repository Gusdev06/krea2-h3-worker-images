# Krea 2 Turbo (imagem) com os modelos DENTRO da imagem: worker acorda em segundos em vez de carregar
# 18,6 GB do disco de rede (~80 s). Base: worker-comfyui 5.10.0 (ComfyUI 0.34) + handler corrigido
# (worker cujo ComfyUI morreu e descartado). Build pelo RunPod (Serverless > New Endpoint > GitHub Repo).
FROM runpod/worker-comfyui:5.10.0-base
COPY handler.py /handler.py
RUN comfy model download --url https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_fp8_scaled.safetensors --relative-path models/diffusion_models --filename krea2_turbo_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors --relative-path models/text_encoders --filename qwen3vl_4b_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors --relative-path models/vae --filename qwen_image_vae.safetensors
