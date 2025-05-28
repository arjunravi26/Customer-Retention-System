from pathlib import Path

try:
    for path in Path(".").rglob("*"):
        if "venv" in path.parts:
            continue
        print(path)
except OSError as e:
    print(f"Error accessing {path}: {e}")

