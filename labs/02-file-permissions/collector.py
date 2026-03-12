import json
from pathlib import Path

CONFIG_PATH = Path("/home/dev/lab-02-config/config.json")


def main() -> None:
    if not CONFIG_PATH.exists():
        print(f"Config file not found: {CONFIG_PATH}")
        return

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)

    logfile_path = config.get("logFile")
    print(f"Logfile Path: {logfile_path}")


if __name__ == "__main__":
    main()