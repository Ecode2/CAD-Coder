import argparse
import importlib.util
from pathlib import Path
import cadquery as cq


def load_module_from_path(py_file):
    spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def convert(py_name):
    repo_root = Path(__file__).resolve().parent
    py_file = repo_root / f"{py_name}.py"

    if not py_file.exists():
        raise FileNotFoundError(py_file)

    module = load_module_from_path(py_file)

    if not hasattr(module, "result"):
        raise RuntimeError(
            "Generated file does not define `result`. "
            "Model must assign final CadQuery object to `result`."
        )

    step_file = repo_root / f"{py_name}.step"
    cq.exporters.export(module.result, step_file)

    print(f"[OK] STEP file saved to {step_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Base name of generated .py file")

    args = parser.parse_args()
    convert(args.name)
