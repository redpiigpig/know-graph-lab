"""Run the bundled DOCX renderer with LibreOffice's console binary on Windows."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys


RENDERER = Path(
    os.environ.get(
        "CODEX_DOCX_RENDERER",
        r"C:\Users\user\.codex\plugins\cache\openai-primary-runtime\documents\26.805.11740\skills\documents\render_docx.py",
    )
)
SOFFICE_CONSOLE = Path(
    os.environ.get(
        "SOFFICE_CONSOLE",
        r"C:\Program Files\LibreOffice\program\soffice.com",
    )
)


def main() -> None:
    if not RENDERER.exists():
        raise FileNotFoundError(f"DOCX renderer not found: {RENDERER}")
    if not SOFFICE_CONSOLE.exists():
        raise FileNotFoundError(f"LibreOffice console binary not found: {SOFFICE_CONSOLE}")

    spec = importlib.util.spec_from_file_location("codex_render_docx", RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import renderer: {RENDERER}")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)

    original_run_cmd = renderer._run_cmd

    def run_cmd(command, *args, **kwargs):
        if command and command[0] == "soffice":
            command = [str(SOFFICE_CONSOLE), *command[1:]]
        return original_run_cmd(command, *args, **kwargs)

    renderer._run_cmd = run_cmd
    renderer.main()


if __name__ == "__main__":
    main()
