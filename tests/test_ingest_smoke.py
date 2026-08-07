"""A complete local ingest hand-off regression, without invoking an LLM."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name.replace('_', '-')}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_ingest_handoff_smoke(tmp_path: Path, monkeypatch) -> None:
    cache, cleanup, review, lint = load("ingest_cache"), load("ingest_cleanup"), load("ingest_review"), load("wiki_lint")
    for module in (cache, cleanup, review):
        monkeypatch.setattr(module, "ROOT", tmp_path)
    cache.DEFAULT_CACHE = tmp_path / ".llm-wiki/ingest/cache.json"
    review.DEFAULT_QUEUE = tmp_path / "ops/review-queue.md"
    cleanup.INBOX_DIR, cleanup.ORIGINALS_DIR, cleanup.SOURCES_DIR = (tmp_path / "raw/inbox", tmp_path / "raw/originals", tmp_path / "raw/sources")
    cleanup.PROTECTED_DIRS = tuple(tmp_path / part for part in (".git", "config", "docs", "raw", "scripts", "skills", "tests", "wiki"))
    for directory in (cleanup.INBOX_DIR, cleanup.ORIGINALS_DIR, cleanup.SOURCES_DIR, tmp_path / "wiki/sources"):
        directory.mkdir(parents=True, exist_ok=True)
    source = cleanup.INBOX_DIR / "brief.md"
    source.write_text("# Brief\n", encoding="utf-8")
    digest = cache.sha256_file(source)
    assert cache.cmd_lookup(SimpleNamespace(path=str(source), cache=str(cache.DEFAULT_CACHE), force=False, require_miss=False)) == 0
    original = cleanup.ORIGINALS_DIR / "brief.md"
    original.write_bytes(source.read_bytes())
    archive = cleanup.SOURCES_DIR / "brief.md"
    archive.write_text("# Brief\n\n視覺轉換閘：未適用\n", encoding="utf-8")
    analysis = tmp_path / ".llm-wiki/ingest/analyses/brief.md"
    analysis.parent.mkdir(parents=True)
    analysis.write_text("# Analysis\n", encoding="utf-8")
    receipt = hashlib.sha256(analysis.read_bytes()).hexdigest()
    source_receipt = hashlib.sha256(archive.read_bytes()).hexdigest()
    (tmp_path / "wiki/sources/brief.md").write_text(
        f"---\ntype: source\ntitle: Brief\ndescription: smoke summary\narchive_slug: brief\nanalysis_receipt: {{version: '1', sha256: '{receipt}', source_sha256: '{source_receipt}', generated_by: 'agent/test', generated_at: '2026-08-07T00:00:00Z'}}\nsources:\n  - id: archive\n    resource: ../../raw/sources/brief.md\ngenerated: {{by: agent/test, at: 2026-08-07T00:00:00Z}}\nstatus: draft\nclassification: internal\nowner: team:test\naccess_scope: team:test\ncontains_pii: false\nretention: permanent\nredaction: none\n---\n# Brief\n\n## Summary\n\n- smoke\n\n## Key Concepts\n\n- none\n\n## Entities\n\n- none\n\n## Notable Claims\n\n- smoke[^archive]\n\n## Limitations / Gaps\n\n- none\n\n[^archive]: archive\n", encoding="utf-8")
    (tmp_path / "wiki/index.md").write_text("---\nokf_version: \"0.2\"\n---\n# Index\n\n## Overview\n\n## Concepts\n\n## Entities\n\n## Sources\n\n- [Brief](./sources/brief.md)\n\n## Queries\n\n## FAQ\n", encoding="utf-8")
    (tmp_path / "wiki/log.md").write_text("# Wiki Log\n", encoding="utf-8")
    (tmp_path / "ops").mkdir(exist_ok=True)
    (tmp_path / "ops/purpose.md").write_text("---\nmode: template\n---\n# Purpose\n", encoding="utf-8")
    assert review.cmd_append(SimpleNamespace(queue=str(review.DEFAULT_QUEUE), title="confirm", reason="smoke", source="ingest", action="human_verify", related=[], id="smoke")) == 0
    assert cache.cmd_record(SimpleNamespace(path=None, cache=str(cache.DEFAULT_CACHE), archive_slug="brief", source_page="wiki/sources/brief.md", sha256=digest, original_name=source.name, analysis_receipt=receipt, analysis_version="1", analysis_source_sha256=source_receipt, analysis_generated_by="agent/test", analysis_generated_at="2026-08-07T00:00:00Z")) == 0
    cleanup.validate_input(source)
    cleanup.validate_archives(source, [original, archive])
    cleanup.cleanup_input(source, confirmed=True)
    assert not source.exists()
    lint.ROOT, lint.WIKI, lint.RAW, lint.RAW_SOURCES, lint.RAW_ASSETS = tmp_path, tmp_path / "wiki", tmp_path / "raw", tmp_path / "raw/sources", tmp_path / "raw/assets"
    assert lint.main([]) == 0
    replacement = cleanup.INBOX_DIR / "same-content.md"
    replacement.write_bytes(original.read_bytes())
    from io import StringIO
    import contextlib
    output = StringIO()
    with contextlib.redirect_stdout(output):
        assert cache.cmd_lookup(SimpleNamespace(path=str(replacement), cache=str(cache.DEFAULT_CACHE), force=False, require_miss=False)) == 0
    assert __import__("json").loads(output.getvalue())["hit"] is True
