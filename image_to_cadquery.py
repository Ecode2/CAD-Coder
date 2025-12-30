import argparse
import json
import subprocess
import shutil
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

    # Input JSONL
    input_jsonl = work_dir / "input.jsonl"
    with open(input_jsonl, "w") as f:
        f.write(json.dumps({
            "question_id": 0,
            "image": image_name,
            "text": (
                "Generate CadQuery code for this CAD part. "
                "Output only valid Python CadQuery code. "
                "Assign the final solid to a variable named `result`."
            )
        }) + "\n")

    # Output paths
    results_dir = repo_root / "inference" / "inference_results" / output_name
    results_dir.mkdir(parents=True, exist_ok=True)
    output_jsonl = results_dir / f"{output_name}.jsonl"

    # Run inference
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
    print("[INFO] Conversion to STEP must be run in cad_iou environment")


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
