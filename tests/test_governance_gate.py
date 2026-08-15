from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "scripts" / "governance-gate.py"
    spec = importlib.util.spec_from_file_location("governance_gate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["governance_gate"] = module
    spec.loader.exec_module(module)
    return module


def test_raw_approval_requires_human_and_clean_data() -> None:
    module = _load()
    digest = "a" * 64
    assert module.approval_issue("raw/sources/a.md", None, digest)
    bad = {"classification": "internal", "owner": "bad", "approved_by": "agent/x", "approved_at": "not-a-date", "contains_pii": False, "redaction": "none", "source_sha256": digest}
    assert "owner" in module.approval_issue("raw/sources/a.md", bad, digest)
    good = {**bad, "owner": "team:x", "approved_by": "human:reviewer", "approved_at": "2026-08-07"}
    assert module.approval_issue("raw/sources/a.md", good, digest) is None
    assert "does not match" in module.approval_issue("raw/sources/a.md", good, "b" * 64)


def test_secret_scan_detects_private_key(tmp_path: Path) -> None:
    module = _load()
    path = tmp_path / "key.pem"
    path.write_text("-----BEGIN " + "PRIVATE KEY-----\n", encoding="utf-8")
    assert module.scan(path) == ["private key"]


def test_no_base_scans_tracked_and_untracked_paths(monkeypatch) -> None:
    module = _load()
    def fake_git(*args: str) -> str:
        return "tracked.md\n" if args == ("ls-files",) else "untracked.md\n"
    monkeypatch.setattr(module, "git", fake_git)
    assert module.relevant_paths(None) == [("A", "tracked.md"), ("A", "untracked.md")]


def test_rename_uses_new_path(monkeypatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "git", lambda *args: "R100\told.md\traw/sources/new.md\n")
    assert module.relevant_paths("base") == [("R100", "raw/sources/new.md")]


def test_manifest_rejects_duplicate_paths(tmp_path: Path) -> None:
    module = _load()
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"approvals": [{"path": "raw/a.md"}, {"path": "raw/a.md"}]}', encoding="utf-8")
    try:
        module.load_manifest(manifest)
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate paths must fail")
