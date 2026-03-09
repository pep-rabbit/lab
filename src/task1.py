import argparse
import os


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
    )

    args = parser.parse_args()
    config_path: str | None = args.config
    file_path: str = os.path.expanduser(
        config_path if config_path else os.environ.get("CONFIG_PATH", "~/.config.ymal")
    )

    print(file_path)


if __name__ == "__main__":
    main()
