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
# Python Environment Setup
############################################
if [ ! which python ]; then
    echo "Python is not installed. Please install Python before running this script."
    exit 1
fi
# check for the use of python version 3.10
echo "Using Python: $(which python)"
python -m pip install virtualenv

python -m venv $CADCODER_DIR/cad_env
python -m venv $CADCODER_DIR/iou_env

############################################
# CAD-Coder environment and dependencies
############################################
source $CADCODER_DIR/cad_env/bin/activate
cd "$CADCODER_DIR"

pip install --upgrade pip
pip install -e .
pip install -e ".[train]"
pip install datasets peft==0.10.0 tensorboard

deactivate

############################################
# cad_iou environment and dependencies
############################################
source $CADCODER_DIR/cad_env/bin/activate
cd "$CADCODER_DIR"

pip install cadquery
pip install trimesh plyfile pandas tqdm

deactivate

############################################
# HuggingFace & Torch cache (local, safe)
############################################
HF_CACHE="$CADCODER_DIR/hf_cache"
TORCH_CACHE="$CADCODER_DIR/torch_cache"

mkdir -p "$HF_CACHE"/transformers
mkdir -p "$HF_CACHE"/datasets
mkdir -p "$TORCH_CACHE"

EXPORT_BLOCK=$(cat <<EOF
# CAD-Coder Model caches
export HF_HOME=$HF_CACHE
export TRANSFORMERS_CACHE=$HF_CACHE/transformers
export HF_DATASETS_CACHE=$HF_CACHE/datasets
export TORCH_HOME=$TORCH_CACHE
EOF
)

if [ -f ~/.bashrc ]; then
    echo "$EXPORT_BLOCK" >> ~/.bashrc
elif [ -f ~/.zshrc ]; then
    echo "$EXPORT_BLOCK" >> ~/.zshrc
else
    echo "No .bashrc or .zshrc found. Please add the following lines to your shell configuration file:"
    echo "$EXPORT_BLOCK"
fi

echo "Setup complete."
echo "Run: source ~/.bashrc"
