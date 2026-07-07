# hash:sha256:afe3aa2069596914d075655748e9b3aafdce5c30eb4f6d1201123639b8909d71
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/pytorch:2.4.0-cuda12.4.0-mambaforge24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN conda install -y \
        jupyter==1.1.1 \
        scanpy==1.11.3 \
        scvi-tools==1.3.3 \
        scikit-misc==0.5.1 \     
        leidenalg\
    && conda clean -ya
# The conda install above pulls the CPU-only (cpu_mkl) build of pytorch from
# conda-forge, which silently disables GPU support (torch.cuda.is_available() == False).
# Reinstall the CUDA 12.4 build so scvi-tools trains on the GPU. This wheel bundles its
# own cudnn 9 / nccl / cublas etc., so it is self-consistent regardless of conda's solve.
RUN pip install --no-cache-dir torch==2.4.0 torchvision==0.19.0 \
        --index-url https://download.pytorch.org/whl/cu124
RUN pip install --upgrade numpyro
RUN pip install --no-cache-dir "numpy<2.3"
RUN pip install mygene
# RUN conda install -c conda-forge python-igraph
RUN pip install scikit-image
RUN pip install toml
RUN pip install opencv-python

ADD "https://github.com/coder/code-server/releases/download/v4.100.3/code-server-4.100.3-linux-amd64.tar.gz" /.code-server/code-server.tar.gz
	
RUN cd /.code-server \
    && tar -xvf code-server.tar.gz \
    && rm code-server.tar.gz \
    && ln -s /.code-server/code-server-4.100.3-linux-amd64/bin/code-server /usr/bin/code-server \
    && mkdir -p /.vscode/extensions

RUN code-server --extensions-dir="/.vscode/extensions" --install-extension ms-python.python@2025.14.0 \
    && code-server --extensions-dir="/.vscode/extensions" --install-extension ms-toolsai.jupyter@2025.4.1 \
    && code-server --extensions-dir="/.vscode/extensions" --install-extension reditorsupport.r@2.8.6 \
    && code-server --extensions-dir="/.vscode/extensions" --install-extension saoudrizwan.claude-dev@3.35.1



