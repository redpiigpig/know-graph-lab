"""Run the managed DOCX renderer with LibreOffice's Windows console binary.

LibreOffice installs both ``soffice.exe`` (GUI subsystem) and ``soffice.com``
(console subsystem).  Python's Windows executable search resolves the bare
``soffice`` command in the managed renderer to the GUI binary, which can wait
indefinitely in a headless session.  This wrapper keeps the managed renderer
unchanged and redirects only that executable to the console binary.
"""

from __future__ import annotations

import os
import runpy
import subprocess
import sys
from pathlib import Path


DOCUMENTS_CACHE = Path(
    r"C:\Users\user\.codex\plugins\cache\openai-primary-runtime\documents"
)
SOFFICE_CONSOLE = Path(r"C:\Program Files\LibreOffice\program\soffice.com")
POPPLER_BIN = Path(
    r"C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin"
)


def resolve_renderer() -> Path:
    """Return the newest installed managed documents renderer."""

    candidates = list(DOCUMENTS_CACHE.glob("*/skills/documents/render_docx.py"))
    if not candidates:
        raise FileNotFoundError(
            f"No managed render_docx.py found below {DOCUMENTS_CACHE}"
        )

    def version_key(path: Path) -> tuple[int, ...]:
        try:
            return tuple(int(part) for part in path.parents[2].name.split("."))
        except ValueError:
            return (0,)

    return max(candidates, key=version_key)


def main() -> None:
    renderer = resolve_renderer()
    if not SOFFICE_CONSOLE.is_file():
        raise FileNotFoundError(SOFFICE_CONSOLE)
    if not (POPPLER_BIN / "pdfinfo.exe").is_file():
        raise FileNotFoundError(POPPLER_BIN / "pdfinfo.exe")

    os.environ["PATH"] = str(POPPLER_BIN) + os.pathsep + os.environ.get("PATH", "")

    original_run = subprocess.run

    def run_with_console(command, *args, **kwargs):
        if (
            isinstance(command, (list, tuple))
            and command
            and Path(str(command[0])).stem.lower() == "soffice"
        ):
            command = [str(SOFFICE_CONSOLE), *command[1:]]
            # The managed renderer emits ``file://C:\\...`` on Windows, which
            # LibreOffice rejects.  Normalize only this temporary profile
            # argument to the standards-compliant ``file:///C:/...`` URI.
            profile_prefix = "-env:UserInstallation=file://"
            normalized = []
            for value in command:
                value = str(value)
                if value.startswith(profile_prefix) and not value.startswith(
                    "-env:UserInstallation=file:///"
                ):
                    profile_path = value[len(profile_prefix):]
                    value = "-env:UserInstallation=" + Path(profile_path).resolve().as_uri()
                normalized.append(value)
            command = normalized
        return original_run(command, *args, **kwargs)

    subprocess.run = run_with_console
    sys.argv[0] = str(renderer)
    runpy.run_path(str(renderer), run_name="__main__")


if __name__ == "__main__":
    main()
