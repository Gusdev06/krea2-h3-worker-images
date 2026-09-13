# Ideogram 4 (imagem) com os modelos DENTRO da imagem, no mesmo padrao do krea2/, h3/ e qwen-edit/.
# ~32 GB de peso.
#
# ATENCAO - LICENCA: os pesos do Ideogram 4 estao sob "ideogram-non-commercial-model-agreement"
# (https://huggingface.co/ideogram-ai/ideogram-4-fp8/blob/main/LICENSE.md): USO NAO COMERCIAL.
# Este endpoint e para teste e avaliacao. Nao use a saida em anuncio, produto ou entrega de cliente -
# pra isso o endpoint e o do Krea 2, cujos pesos permitem uso comercial.
#
# O Ideogram 4 usa DOIS checkpoints: o condicional e um "unconditional" treinado pro outro lado do
# CFG. O no DualModelGuider (core) recebe os dois; e por isso que o grafo dele e mais complexo que o
# do Krea 2 Turbo, que roda cfg 1 com o negativo zerado.
FROM runpod/worker-comfyui:5.10.0-base
COPY handler.py /handler.py

# --- custom node: RES4LYF -------------------------------------------------------------------------
# O sampler "res_2m" do workflow de referencia NAO existe no ComfyUI padrao (o core tem
# "res_multistep"). Ele vem daqui. Commit fixado pra o build ser reprodutivel.
RUN git clone https://github.com/ClownsharkBatwing/RES4LYF.git /comfyui/custom_nodes/RES4LYF \
 && cd /comfyui/custom_nodes/RES4LYF \
 && git checkout e8437efef69c \
 && uv pip install --no-cache-dir -r requirements.txt
# (o start.sh do worker sobe o ComfyUI com o python do /opt/venv, nao com o /comfyui/.venv - por isso
#  as dependencias do custom node vao pelo uv, que instala no venv ativo do PATH.)

# --- modelos --------------------------------------------------------------------------------------
RUN comfy model download --url https://huggingface.co/Comfy-Org/Ideogram-4/resolve/main/diffusion_models/ideogram4_fp8_scaled.safetensors --relative-path models/diffusion_models --filename ideogram4_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Ideogram-4/resolve/main/diffusion_models/ideogram4_unconditional_fp8_scaled.safetensors --relative-path models/diffusion_models --filename ideogram4_unconditional_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Ideogram-4/resolve/main/text_encoders/qwen3vl_8b_fp8_scaled.safetensors --relative-path models/text_encoders --filename qwen3vl_8b_fp8_scaled.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/Ideogram-4/resolve/main/vae/flux2-vae.safetensors --relative-path models/vae --filename flux2-vae.safetensors

# --- LoRA Realism Engine (Ideogram) ---------------------------------------------------------------
# Espelho do PROPRIO autor no HF; os sha256 abaixo sao os publicados pela CivitAI (modelo 2688234),
# entao o build quebra se o arquivo mudar. A V2 que aparece no workflow de referencia foi retirada
# da CivitAI e nao da pra conferir por hash - ficam a V5 (atual) e a V4.
RUN comfy model download --url https://huggingface.co/RazzzHF/Realism_Engine_Ideogram_4/resolve/main/Realism_Engine_Ideogram_V5.safetensors --relative-path models/loras --filename Realism_Engine_Ideogram_V5.safetensors \
 && echo "1610be97fe522d196295df13ab147da288cfcb861a874a22b21f640c971e05ae  /comfyui/models/loras/Realism_Engine_Ideogram_V5.safetensors" | sha256sum -c -
RUN comfy model download --url https://huggingface.co/RazzzHF/Realism_Engine_Ideogram_4/resolve/main/Realism_Engine_Ideogram_V4.safetensors --relative-path models/loras --filename Realism_Engine_Ideogram_V4.safetensors \
 && echo "f2634943709580f92f3b00f699dc5516c99d9a3f4fc5a65287f7bb18cc5c0b80  /comfyui/models/loras/Realism_Engine_Ideogram_V4.safetensors" | sha256sum -c -
