"""
One-shot setup: generate data, run dbt, train model.
Usage:  python setup.py
"""
import subprocess, sys, os

def run(cmd, cwd=None):
    print(f"\n>>> {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=cwd)
    if r.returncode != 0:
        print(f"[WARN] command exited with code {r.returncode}")

if __name__ == "__main__":
    # 1. Generate synthetic data
    run("python data/generate_data.py")

    # 2. dbt run
    run("dbt run", cwd="dbt_project")

    # 3. Train ML model
    run("python ml/train_model.py")

    print("\n✅  Setup complete — run:  streamlit run dashboard/app.py")
