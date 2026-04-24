from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"


def run_script(script_name: str) -> None:
    script_path = SCRIPTS_DIR / script_name
    subprocess.run([sys.executable, str(script_path)], check=True, cwd=ROOT_DIR)


def main() -> None:
    run_script("eda_analysis.py")
    run_script("statistical_analysis.py")
    print("EDA and statistical analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
