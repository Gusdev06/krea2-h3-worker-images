# MiniMax H3 (video com audio) com os 43 GB de modelo DENTRO da imagem: worker acorda em segundos em
# vez de carregar do disco de rede (~200 s). Base: worker-comfyui 5.10.0 + handler corrigido.
# Limite do build do RunPod: 30 min. Se estourar, o caminho e construir fora e publicar num registry.
FROM runpod/worker-comfyui:5.10.0-base
COPY handler.py /handler.py
RUN comfy model download --url https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors --relative-path models/diffusion_models --filename minimax_h3_fl2va_pruned_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors --relative-path models/text_encoders --filename qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors --relative-path models/vae --filename minimax_h3_video_vae_fp16.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors --relative-path models/vae --filename minimax_h3_audio_vae_fp32.safetensors
RUN comfy model download --url https://huggingface.co/lightx2v/Minimax-h3-Turbo/resolve/main/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors --relative-path models/loras --filename minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors
