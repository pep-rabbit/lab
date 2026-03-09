import argparse
import json
import os
import platform
from dataclasses import dataclass


@dataclass
class SystemInfoArgs:
    os: bool
    version: bool
    processor: bool
    kernels: bool
    json: bool
    file: str


def parse_args() -> SystemInfoArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--os",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--processor",
        action="store_true",
    )
    parser.add_argument(
        "-k",
        "--kernels",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="stdout",
    )
    namespace = parser.parse_args()
    return SystemInfoArgs(
        os=namespace.os,
        version=namespace.version,
        processor=namespace.processor,
        kernels=namespace.kernels,
        json=namespace.json,
        file=namespace.file,
    )


def get_system_info() -> dict[str, str]:
    return {
        "os": f"{platform.system()} {platform.release()}",
        "version": platform.version(),
        "processor": platform.processor() or platform.machine(),
        "kernels": str(os.cpu_count() or "Unknown"),
    }


def filter_info(info: dict[str, str], args: SystemInfoArgs) -> dict[str, str]:
    has_any_flag = args.os or args.version or args.processor or args.kernels

    if not has_any_flag:
        return info

    filtered = {}
    if args.os:
        filtered["os"] = info["os"]
    if args.version:
        filtered["version"] = info["version"]
    if args.processor:
        filtered["processor"] = info["processor"]
    if args.kernels:
        filtered["kernels"] = info["kernels"]

    return filtered


def output_info(info: dict[str, str], output: str, as_json: bool = False) -> None:
    if as_json:
        text = json.dumps(info, indent=2)
    else:
        lines = [f"{key}: {value}" for key, value in info.items()]
        text = "\n".join(lines)

    if output == "stdout":
        print(text)
    else:
        with open(output, "w") as f:
            f.write(text + "\n")


def main() -> None:
    args = parse_args()
    system_info = get_system_info()
    filtered_info = filter_info(system_info, args)
    output_info(filtered_info, args.file, args.json)


if __name__ == "__main__":
    main()
