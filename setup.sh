#!/usr/bin/env bash
set -e

############################################
# Paths (portable across pods)
############################################
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Root directory: $ROOT_DIR"

# Detect CAD-Coder location
if [ -d "$ROOT_DIR/CAD-Coder" ]; then
    CADCODER_DIR="$ROOT_DIR/CAD-Coder"
else
    CADCODER_DIR="$ROOT_DIR"
fi
echo "CAD-Coder directory: $CADCODER_DIR"

############################################
# Miniconda setup
############################################
MINICONDA_DIR="$ROOT_DIR/miniconda3"
MINICONDA_INSTALLER="$ROOT_DIR/Miniconda3-latest-Linux-x86_64.sh"

if [ ! -d "$MINICONDA_DIR" ]; then
    echo "Installing Miniconda..."
    if [ ! -f "$MINICONDA_INSTALLER" ]; then
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O "$MINICONDA_INSTALLER"
    fi
    bash "$MINICONDA_INSTALLER" -b -p "$MINICONDA_DIR"
fi

# Initialize conda (no hardcoded paths)
source "$MINICONDA_DIR/etc/profile.d/conda.sh"

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

############################################
# llava environment
############################################
if conda env list | grep -q "^llava"; then
    echo "Using existing llava environment"
else
    conda create -n llava python=3.10 -y
fi

conda activate llava

############################################
# Python dependencies (CAD-Coder)
############################################
cd "$CADCODER_DIR"

pip install --upgrade pip
pip install -e .
pip install -e ".[train]"
pip install datasets peft==0.10.0 tensorboard

############################################
# PyTorch (CUDA 12.1)
############################################
pip uninstall -y torch torchvision torchaudio || true
pip install torch==2.4.0+cu121 torchvision --index-url https://download.pytorch.org/whl/cu121

############################################
# FlashAttention (wheel-based, portable)
############################################
FLASH_ATTN_WHL="flash_attn-2.8.3+cu12torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl"
FLASH_ATTN_URL="https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/$FLASH_ATTN_WHL"

cd "$ROOT_DIR"

if [ ! -f "$FLASH_ATTN_WHL" ]; then
    echo "Downloading FlashAttention wheel..."
    wget "$FLASH_ATTN_URL"
fi

pip install "$FLASH_ATTN_WHL"

conda deactivate

############################################
# cad_iou environment
############################################
if conda env list | grep -q "^cad_iou"; then
    echo "cad_iou environment already exists"
else
    conda create -n cad_iou python=3.10 -y
fi

conda activate cad_iou
conda install -c conda-forge cadquery -y
pip install trimesh plyfile pandas tqdm
conda deactivate

############################################
# HuggingFace & Torch cache (local, safe)
############################################
HF_CACHE="$ROOT_DIR/hf_cache"
TORCH_CACHE="$ROOT_DIR/torch_cache"

mkdir -p "$HF_CACHE"/{transformers,datasets}
mkdir -p "$TORCH_CACHE"

EXPORT_BLOCK=$(cat <<EOF
# CAD-Coder caches
export HF_HOME=$HF_CACHE
export TRANSFORMERS_CACHE=$HF_CACHE/transformers
export HF_DATASETS_CACHE=$HF_CACHE/datasets
export TORCH_HOME=$TORCH_CACHE
EOF
)

if ! grep -q "CAD-Coder caches" ~/.bashrc; then
    echo "$EXPORT_BLOCK" >> ~/.bashrc
fi

echo "Setup complete."
echo "Run: source ~/.bashrc"
