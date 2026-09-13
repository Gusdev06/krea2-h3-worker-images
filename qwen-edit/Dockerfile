# Qwen-Image-Edit 2511 (edicao por instrucao: "mesma pessoa, troca a roupa / o fundo") com os modelos
# DENTRO da imagem, no mesmo padrao do krea2/ e do h3/. ~31 GB de peso.
# Ao contrario do img2img do Krea 2, aqui a imagem de referencia entra como condicionamento
# (TextEncodeQwenImageEditPlus -> reference_latents), que e o que preserva a identidade.
# Base: worker-comfyui 5.10.0 (ComfyUI 0.34, nos de edicao ja nativos) + handler corrigido.
# Pesos: Apache-2.0 (Qwen-Image-Edit) - uso comercial liberado.
FROM runpod/worker-comfyui:5.10.0-base
COPY handler.py /handler.py

# modelo de edicao, fp8 mixed (bf16 seria 40,9 GB)
RUN comfy model download --url https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors --relative-path models/diffusion_models --filename qwen_image_edit_2511_fp8mixed.safetensors

# text encoder multimodal (Qwen 2.5 VL 7B): e ele que "le" a imagem de referencia
RUN comfy model download --url https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors --relative-path models/text_encoders --filename qwen_2.5_vl_7b_fp8_scaled.safetensors

# VAE (o mesmo do Krea 2)
RUN comfy model download --url https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors --relative-path models/vae --filename qwen_image_vae.safetensors

# LoRAs Lightning de 4 e 8 passos: cortam a edicao de ~20 passos para 4-8. Foram treinadas para o
# Edit 2509, NAO para o 2511 - ficam aqui para o teste A/B, ligadas pelo cliente. Se degradar, desliga.
RUN comfy model download --url https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors --relative-path models/loras --filename qwen_image_edit_2509_lightning_4steps_bf16.safetensors
RUN comfy model download --url https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-8steps-V1.0-bf16.safetensors --relative-path models/loras --filename qwen_image_edit_2509_lightning_8steps_bf16.safetensors
