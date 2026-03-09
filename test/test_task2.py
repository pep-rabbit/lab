import sys
from unittest.mock import mock_open, patch

import pytest

from task2 import (
    SystemInfoArgs,
    filter_info,
    get_system_info,
    main,
    output_info,
    parse_args,
)


def test_parse_args_no_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["prog"])

    args = parse_args()

    assert args.os is False
    assert args.version is False
    assert args.processor is False
    assert args.kernels is False
    assert args.file == "stdout"


def test_parse_args_with_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["prog", "-o", "-v", "-f", "output.txt"])

    args = parse_args()

    assert args.os is True
    assert args.version is True
    assert args.processor is False
    assert args.kernels is False
    assert args.file == "output.txt"


def test_parse_args_all_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--os", "--version", "--processor", "--kernels", "--file", "test.txt"],
    )

    args = parse_args()

    assert args.os is True
    assert args.version is True
    assert args.processor is True
    assert args.kernels is True
    assert args.file == "test.txt"


@patch("task2.os.cpu_count")
@patch("task2.platform.machine")
@patch("task2.platform.processor")
@patch("task2.platform.version")
@patch("task2.platform.release")
@patch("task2.platform.system")
def test_get_system_info(
    mock_system: pytest.Mock,
    mock_release: pytest.Mock,
    mock_version: pytest.Mock,
    mock_processor: pytest.Mock,
    mock_machine: pytest.Mock,
    mock_cpu_count: pytest.Mock,
) -> None:
    mock_system.return_value = "Linux"
    mock_release.return_value = "5.15.0"
    mock_version.return_value = "#1 SMP"
    mock_processor.return_value = "x86_64"
    mock_machine.return_value = "AMD64"
    mock_cpu_count.return_value = 8

    info = get_system_info()

    assert info["os"] == "Linux 5.15.0"
    assert info["version"] == "#1 SMP"
    assert info["processor"] == "x86_64"
    assert info["kernels"] == "8"


@patch("task2.os.cpu_count")
@patch("task2.platform.machine")
@patch("task2.platform.processor")
def test_get_system_info_fallback_processor(
    mock_processor: pytest.Mock,
    mock_machine: pytest.Mock,
    mock_cpu_count: pytest.Mock,
) -> None:
    mock_processor.return_value = ""
    mock_machine.return_value = "arm64"
    mock_cpu_count.return_value = 4

    info = get_system_info()

    assert info["processor"] == "arm64"


def test_filter_info_no_flags() -> None:
    args = SystemInfoArgs(
        os=False,
        version=False,
        processor=False,
        kernels=False,
        file="stdout",
    )
    info = {
        "os": "Linux 5.15.0",
        "version": "#1 SMP",
        "processor": "x86_64",
        "kernels": "8",
    }

    filtered = filter_info(info, args)

    assert filtered == info


def test_filter_info_single_flag() -> None:
    args = SystemInfoArgs(
        os=True,
        version=False,
        processor=False,
        kernels=False,
        file="stdout",
    )
    info = {
        "os": "Linux 5.15.0",
        "version": "#1 SMP",
        "processor": "x86_64",
        "kernels": "8",
    }

    filtered = filter_info(info, args)

    assert filtered == {"os": "Linux 5.15.0"}


def test_filter_info_multiple_flags() -> None:
    args = SystemInfoArgs(
        os=True,
        version=False,
        processor=True,
        kernels=True,
        file="stdout",
    )
    info = {
        "os": "Linux 5.15.0",
        "version": "#1 SMP",
        "processor": "x86_64",
        "kernels": "8",
    }

    filtered = filter_info(info, args)

    assert filtered == {
        "os": "Linux 5.15.0",
        "processor": "x86_64",
        "kernels": "8",
    }


def test_output_info_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    info = {
        "os": "Linux 5.15.0",
        "version": "#1 SMP",
    }

    output_info(info, "stdout")

    captured = capsys.readouterr()
    assert "os: Linux 5.15.0" in captured.out
    assert "version: #1 SMP" in captured.out


def test_output_info_file() -> None:
    info = {
        "os": "Linux 5.15.0",
        "processor": "x86_64",
    }
    mock_file = mock_open()

    with patch("task2.open", mock_file):
        output_info(info, "test_output.txt")

    mock_file.assert_called_once_with("test_output.txt", "w")
    handle = mock_file()
    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    assert "os: Linux 5.15.0" in written_content
    assert "processor: x86_64" in written_content


@patch("task2.output_info")
@patch("task2.filter_info")
@patch("task2.get_system_info")
@patch("task2.parse_args")
def test_main_integration(
    mock_parse_args: pytest.Mock,
    mock_get_system_info: pytest.Mock,
    mock_filter_info: pytest.Mock,
    mock_output_info: pytest.Mock,
) -> None:
    mock_args = SystemInfoArgs(
        os=True,
        version=False,
        processor=False,
        kernels=False,
        file="output.txt",
    )
    mock_parse_args.return_value = mock_args

    mock_system_info = {
        "os": "Linux 5.15.0",
        "version": "#1 SMP",
        "processor": "x86_64",
        "kernels": "8",
    }
    mock_get_system_info.return_value = mock_system_info

    mock_filtered_info = {"os": "Linux 5.15.0"}
    mock_filter_info.return_value = mock_filtered_info

    main()

    mock_parse_args.assert_called_once()
    mock_get_system_info.assert_called_once()
    mock_filter_info.assert_called_once_with(mock_system_info, mock_args)
    mock_output_info.assert_called_once_with(mock_filtered_info, "output.txt")
