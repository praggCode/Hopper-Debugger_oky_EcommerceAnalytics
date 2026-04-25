from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ML_SRC = Path(__file__).resolve().parent


def run_script(script_name: str) -> None:
    script_path = ML_SRC / script_name
    subprocess.run([sys.executable, str(script_path)], check=True, cwd=ML_SRC.parent.parent)


def main() -> None:
    run_script("late_delivery_prediction.py")
    run_script("customer_segmentation.py")
    print("ML pipeline completed successfully.")


if __name__ == "__main__":
    main()
