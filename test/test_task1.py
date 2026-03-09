import os
import sys

import pytest

from task1 import main


def test_main_uses_cli_arg(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["prog", "--config", "~/cli_config.yaml"])

    main()

    captured = capsys.readouterr()
    assert captured.out.strip() == os.path.expanduser("~/cli_config.yaml")


def test_main_uses_env_when_cli_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["prog"])
    monkeypatch.setenv("CONFIG_PATH", "~/env_config.yaml")

    main()

    captured = capsys.readouterr()
    assert captured.out.strip() == os.path.expanduser("~/env_config.yaml")


def test_main_uses_default_when_cli_and_env_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["prog"])
    monkeypatch.delenv("CONFIG_PATH", raising=False)

    main()

    captured = capsys.readouterr()
    assert captured.out.strip() == os.path.expanduser("~/.config.ymal")
