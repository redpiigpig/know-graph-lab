"""Shared fixtures + import bootstrap for the pipeline test suite.

The pipeline scripts read `os.environ["SUPABASE_URL"]` / service-role key at
*import* time (module-level `URL = os.environ[...]`). All network/DB calls live
*inside* functions, so once dummy env vars are present the pure heuristics
(TOC parsing, chapter classification, HTML→markdown, split/align, s2tw) import
and run with no network, DB, Drive, or LLM access.

This conftest sets those dummy vars and puts scripts/ on sys.path BEFORE any
test module imports a pipeline module (pytest imports conftest first).
"""
import os
import sys
from pathlib import Path

# Dummy creds so `URL = os.environ["SUPABASE_URL"]` doesn't KeyError on import.
os.environ.setdefault("SUPABASE_URL", "http://dummy.local")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "dummy-service-role-key")
os.environ.setdefault("R2_BUCKET", "dummy-bucket")
os.environ.setdefault("R2_ACCOUNT_ID", "dummy")
os.environ.setdefault("R2_ACCESS_KEY_ID", "dummy")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "dummy")

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
