# Ternary-Bonsai-2-27B (Qwen3.8-27B em pesos ternarios, 98,2% do FP16 em ~7 GB) no RunPod Serverless.
# O GGUF NAO roda no llama.cpp comum: os kernels ternarios vivem no fork PrismML-Eng/llama.cpp.
# Usamos o binario CUDA pre-compilado da release pinada pelo Bonsai-demo (nada de compilar no build) e
# deixamos o modelo DENTRO da imagem: worker acorda em segundos, sem disco de rede.
# Pesos: prism-ml/Ternary-Bonsai-2-27B-gguf, Apache-2.0 - uso comercial liberado.
FROM nvidia/cuda:12.8.1-runtime-ubuntu22.04

# release do fork (mesma que o setup.sh do PrismML-Eng/Bonsai-demo pina) e pacote de pesos
ARG LLAMA_RELEASE=prism-b10709-9a9394a
ARG LLAMA_CUDA=12.8
# PQ2_0 (7,2 GB): mais rapido em H100/A100 e no prompt processing em toda GPU - padrao do Bonsai-demo.
# PTQ1_0 (5,9 GB): decode mais rapido em 4090 / L4 / L40S / 6000 Ada (memory-bound).
ARG MODEL_FILE=Ternary-Bonsai-2-27B-PQ2_0.gguf
# torre de visao (opcional; so carrega se LLAMA_MMPROJ=1 no runtime). "" = nao baixar.
ARG MMPROJ_FILE=Ternary-Bonsai-2-27B-mmproj-Q8_0.gguf

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl python3 python3-pip libgomp1 libssl3 libcurl4 \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir runpod requests

# binarios do fork (llama-server + libggml-cuda etc.). Precisa de glibc >= 2.34 (22.04 tem 2.35).
ENV LD_LIBRARY_PATH=/opt/llama:/usr/local/cuda/lib64:${LD_LIBRARY_PATH}
RUN mkdir -p /opt/llama && cd /opt/llama \
    && curl -fL --retry 3 -o bin.tgz \
        https://github.com/PrismML-Eng/llama.cpp/releases/download/${LLAMA_RELEASE}/llama-${LLAMA_RELEASE}-bin-linux-cuda-${LLAMA_CUDA}-x64.tar.gz \
    && tar -xzf bin.tgz --strip-components=1 && rm bin.tgz \
    && (ldd ./llama-server; ldd ./libllama-common.so) | grep -q 'not found' && exit 1 || true

# pesos
RUN mkdir -p /models && cd /models \
    && curl -fL --retry 3 -o ${MODEL_FILE} \
        https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf/resolve/main/${MODEL_FILE} \
    && if [ -n "${MMPROJ_FILE}" ]; then curl -fL --retry 3 -o ${MMPROJ_FILE} \
        https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf/resolve/main/${MMPROJ_FILE}; fi
ENV MODEL_PATH=/models/${MODEL_FILE} MMPROJ_PATH=/models/${MMPROJ_FILE}

# ajustes de runtime (todos podem ser trocados no endpoint sem rebuild)
ENV LLAMA_PORT=8080 \
    LLAMA_CTX=32768 \
    LLAMA_PARALLEL=1 \
    LLAMA_NGL=99 \
    LLAMA_MMPROJ=0 \
    LLAMA_KV4=0 \
    LLAMA_EXTRA_ARGS=""

# contexto de build e a raiz do repo (Dockerfile path bonsai-2-27b/Dockerfile no RunPod)
COPY bonsai-2-27b/start.sh bonsai-2-27b/handler.py /
RUN chmod +x /start.sh
CMD ["/start.sh"]
