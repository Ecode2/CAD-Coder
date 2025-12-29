import argparse
import json
import subprocess
import shutil
import os
import sys
from pathlib import Path


def run_single_image(model, image_path, output_name):
    repo_root = Path(__file__).resolve().parent

    work_dir = repo_root / "inference" / "single_run"
    images_dir = work_dir / "images"
    work_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    # Copy image
    image_path = Path(image_path).resolve()
    image_name = image_path.name
    shutil.copy(image_path, images_dir / image_name)

    # Create input jsonl
    input_jsonl = work_dir / "input.jsonl"
    with open(input_jsonl, "w") as f:
        f.write(json.dumps({
            "question_id": 0,
            "image": image_name,
            "text": "Generate CadQuery code for this CAD part. Output only valid Python CadQuery code."
        }) + "\n")

    # Output paths
    results_dir = repo_root / "inference" / "inference_results" / output_name
    results_dir.mkdir(parents=True, exist_ok=True)
    output_jsonl = results_dir / f"{output_name}.jsonl"

    # Run inference via official loader
    cmd = [
        sys.executable, "-m", "llava.eval.model_vqa_loader",
        "--model-path", model,
        "--question-file", str(input_jsonl),
        "--image-folder", str(images_dir),
        "--answers-file", str(output_jsonl),
        "--num-chunks", "1",
        "--chunk-idx", "0",
        "--temperature", "0",
        "--max_new_tokens", "3450",
        "--conv-mode", "vicuna_v1"
    ]

    subprocess.run(cmd, check=True)

    # Extract CadQuery code
    with open(output_jsonl) as f:
        line = json.loads(f.readline())
        cadquery_code = line["text"]

    cq_file = repo_root / f"{output_name}.py"
    with open(cq_file, "w") as f:
        f.write(cadquery_code)

    print(f"[OK] CadQuery code saved to {cq_file}")

    # Convert to STEP
    step_file = repo_root / f"{output_name}.step"

    step_wrapper = f"""
import cadquery as cq
from {output_name} import result

cq.exporters.export(result, "{step_file}")
"""

    tmp_runner = repo_root / "_cq_to_step.py"
    with open(tmp_runner, "w") as f:
        f.write(step_wrapper)

    subprocess.run([sys.executable, str(tmp_runner)], check=True)

    tmp_runner.unlink()

    print(f"[OK] STEP file saved to {step_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="HF model name or local path")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--output", required=True, help="Base name for output files")

    args = parser.parse_args()

    run_single_image(
        model=args.model,
        image_path=args.image,
        output_name=args.output
    )




""" import argparse
import json
import os
import tempfile
import subprocess


def run_single_image(model, image_path, output_name):
    workdir = "/workspace/CAD-Coder/inference/single_run"
    os.makedirs(workdir, exist_ok=True)

    jsonl_path = os.path.join(workdir, "input.jsonl")

    # Create a single-item JSONL (this matches CAD-Coder expectations)
    with open(jsonl_path, "w") as f:
        item = {
            "question_id": 0,
            "image": os.path.basename(image_path),
            "text": "Generate CADQuery code that reconstructs the 3D CAD model shown in the image."
        }
        f.write(json.dumps(item) + "\n")

    image_dir = os.path.join(workdir, "images")
    os.makedirs(image_dir, exist_ok=True)

    # Symlink image
    target = os.path.join(image_dir, os.path.basename(image_path))
    if not os.path.exists(target):
        os.symlink(image_path, target)

    output_dir = f"/workspace/CAD-Coder/inference/inference_results/{output_name}"
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "python", "-m", "llava.eval.model_vqa_loader",
        "--model-path", model,
        "--question-file", jsonl_path,
        "--image-folder", image_dir,
        "--answers-file", f"{output_dir}/{output_name}.jsonl",
        "--num-chunks", "1",
        "--chunk-idx", "0",
        "--temperature", "0",
        "--max_new_tokens", "3450",
        "--conv-mode", "vicuna_v1"
    ]

    subprocess.run(cmd, check=True)

    print("[OK] Inference completed")
    print(f"[OK] Output JSONL: {output_dir}/{output_name}.jsonl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    run_single_image(
        model=args.model,
        image_path=args.image,
        output_name=args.output
    )


python single_image_infer.py \
  --model CADCODER/CAD-Coder \
  --image /workspace/CAD-Coder/inference/test100_images/00342885_0.png \
  --output flange_output
 """