"""Schema and repository-invariant tests for wiki-lint."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_lint():
    path = Path(__file__).resolve().parents[1] / "scripts" / "wiki-lint.py"
    spec = importlib.util.spec_from_file_location("wiki_lint_schema", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["wiki_lint_schema"] = module
    spec.loader.exec_module(module)
    return module


def _bundle(tmp_path: Path) -> tuple[Path, Path]:
    wiki = tmp_path / "wiki"
    for directory in (wiki / "concepts", tmp_path / "raw/sources", tmp_path / "raw/assets"):
        directory.mkdir(parents=True, exist_ok=True)
    (wiki / "index.md").write_text(
        """---\nokf_version: \"0.2\"\n---\n\n# Index\n\n## Overview\n\n## Concepts\n\n- [API](./concepts/api.md)\n\n## Entities\n\n## Sources\n\n## Queries\n\n## FAQ\n""",
        encoding="utf-8",
    )
    (wiki / "log.md").write_text("# Wiki Log\n", encoding="utf-8")
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops/purpose.md").write_text(
        "---\nmode: template\n---\n\n# Purpose\n\n## Goals\n\n- demo\n", encoding="utf-8"
    )
    page = wiki / "concepts/api.md"
    page.write_text(
        """---\ntype: concept\ntitle: API\ndescription: Application programming interface\ntags: [api]\nstatus: stable\nsources:\n  - id: spec\n    resource: https://example.com/spec\ngenerated: {by: agent/test, at: 2026-08-05T12:00:00Z}\nstale_after: 2099-01-01\nclassification: internal\nowner: team:platform\naccess_scope: team:platform\ncontains_pii: false\nretention: permanent\nredaction: none\n---\n\n# API\n\nSee [Index](../index.md).\n""",
        encoding="utf-8",
    )
    return wiki, page


def _configure(module, tmp_path: Path) -> None:
    """Point every lint location at the fixture bundle in one call."""
    module.configure(tmp_path)


def test_valid_okf_v02_bundle_passes(tmp_path: Path) -> None:
    module = _load_lint()
    _bundle(tmp_path)
    _configure(module, tmp_path)

    assert module.main([]) == 0


def test_invalid_yaml_is_reported_not_silently_parsed(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    _, page = _bundle(tmp_path)
    page.write_text("---\ntype: [concept\n---\n# API\n", encoding="utf-8")
    _configure(module, tmp_path)

    assert module.main([]) == 1
    assert "invalid YAML frontmatter" in capsys.readouterr().err


def test_schema_rejects_wrong_field_types(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    _, page = _bundle(tmp_path)
    page.write_text(
        """---\ntype: 7\nresource: bare-slug\ntags: api\nstatus: retired\nsources: bad\ngenerated: bad\nstale_after: someday\n---\n# API\n[Home](../index.md)\n""",
        encoding="utf-8",
    )
    _configure(module, tmp_path)

    assert module.main([]) == 1
    output = capsys.readouterr().err
    assert "frontmatter type" in output
    assert "bare slug" in output
    assert "tags must be" in output
    assert "status must be" in output
    assert "sources must be" in output
    assert "generated must be" in output
    assert "stale_after must be" in output


def test_v02_metadata_families_are_validated_without_restricting_type(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    _, page = _bundle(tmp_path)
    page.write_text(
        """---\ntype: attested-computation\nstatus: stable\nsources:\n  - id: source-1\n    resource: https://example.com/source\ngenerated: {by: agent/test, at: 2026-08-05T12:00:00Z}\nverified:\n  - by: human:reviewer\n    at: 2026-08-05T13:00:00Z\nstale_after: 2026-09-01\nclassification: internal\nowner: team:platform\naccess_scope: team:platform\ncontains_pii: false\nretention: per-policy:knowledge\nredaction: none\n---\n# API\n[Home](../index.md)\n""",
        encoding="utf-8",
    )
    _configure(module, tmp_path)
    assert module.main([]) == 0

    page.write_text(
        """---\ntype: attested-computation\nstatus: stable\nsources: bad\ngenerated: {by: agent/test, at: 2026-08-05T12:00:00Z}\nstale_after: someday\nclassification: internal\nowner: team:platform\naccess_scope: team:platform\ncontains_pii: false\nretention: per-policy:knowledge\nredaction: none\n---\n# API\n[Home](../index.md)\n""",
        encoding="utf-8",
    )
    assert module.main([]) == 1
    output = capsys.readouterr().err
    assert "sources must be a list" in output
    assert "stale_after must be" in output


def test_v02_governance_schema_is_required_and_validated(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    _, page = _bundle(tmp_path)
    page.write_text(
        """---\ntype: concept\nsources:\n  - resource: https://example.com/source\ngenerated: {by: agent/test, at: 2026-08-05T12:00:00Z}\nclassification: secret\nowner: nobody\naccess_scope: everyone\ncontains_pii: maybe\nretention: someday\nredaction: skipped\n---\n# API\n[Home](../index.md)\n""",
        encoding="utf-8",
    )
    _configure(module, tmp_path)

    assert module.main([]) == 1
    output = capsys.readouterr().err
    for field in ("classification", "owner", "access_scope", "contains_pii", "retention", "redaction"):
        assert field in output


def test_stale_after_date_is_enforced(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    _, page = _bundle(tmp_path)
    page.write_text(
        page.read_text(encoding="utf-8").replace(
            "stale_after: 2099-01-01", "stale_after: 2000-01-01"
        ),
        encoding="utf-8",
    )
    _configure(module, tmp_path)

    assert module.main([]) == 1
    assert "stale_after reached" in capsys.readouterr().err


def test_source_schema_and_forbidden_wiki_link_are_checked(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    wiki, page = _bundle(tmp_path)
    page.unlink()
    source = wiki / "sources/source.md"
    source.parent.mkdir()
    source.write_text(
        """---\ntype: source\ntitle: Source\n---\n# Source\n\n[[concepts/api]]\n""",
        encoding="utf-8",
    )
    (wiki / "index.md").write_text((wiki / "index.md").read_text(encoding="utf-8").replace("./concepts/api.md", "./sources/source.md"), encoding="utf-8")
    _configure(module, tmp_path)

    assert module.main([]) == 1
    output = capsys.readouterr().err
    assert "source page missing required headings" in output
    assert "wiki-style link is forbidden" in output


def test_every_non_reserved_markdown_is_a_concept_and_production_purpose_is_complete(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    wiki, _ = _bundle(tmp_path)
    (wiki / "purpose.md").write_text("# accidentally in bundle\n", encoding="utf-8")
    purpose = tmp_path / "ops/purpose.md"
    purpose.write_text("---\nmode: production\n---\n\n# Purpose\n\n- （填寫）\n", encoding="utf-8")
    _configure(module, tmp_path)
    assert module.main([]) == 1
    output = capsys.readouterr().err
    assert "missing YAML frontmatter: wiki/purpose.md" in output
    assert "must not retain template placeholders" in output


def test_source_page_requires_private_analysis_receipt(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    wiki, page = _bundle(tmp_path)
    page.unlink()
    source = wiki / "sources/source.md"
    source.parent.mkdir()
    source.write_text(
        "---\ntype: source\ntitle: Source\narchive_slug: source\nsources:\n  - resource: ../../raw/sources/source.md\ngenerated: {by: agent/test, at: 2026-08-05T12:00:00Z}\nclassification: internal\nowner: team:platform\naccess_scope: team:platform\ncontains_pii: false\nretention: permanent\nredaction: none\n---\n# Source\n\n## Summary\n\n## Key Concepts\n\n## Entities\n\n## Notable Claims\n\n## Limitations / Gaps\n", encoding="utf-8")
    (tmp_path / "raw/sources/source.md").write_text("# source\n", encoding="utf-8")
    (wiki / "index.md").write_text((wiki / "index.md").read_text(encoding="utf-8").replace("./concepts/api.md", "./sources/source.md"), encoding="utf-8")
    _configure(module, tmp_path)
    assert module.main([]) == 1
    assert "missing analysis_receipt" in capsys.readouterr().err


def test_analysis_receipt_must_bind_to_raw_archive(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    wiki, page = _bundle(tmp_path)
    page.unlink()
    (tmp_path / "raw/sources/source.md").write_text("# archive\n", encoding="utf-8")
    source = wiki / "sources/source.md"
    source.parent.mkdir()
    source.write_text("---\ntype: source\ntitle: Source\narchive_slug: source\nanalysis_receipt: {version: '1', sha256: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', source_sha256: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', generated_by: 'agent/test', generated_at: '2026-08-07T00:00:00Z'}\nsources:\n  - resource: ../../raw/sources/source.md\ngenerated: {by: agent/test, at: 2026-08-07T00:00:00Z}\nclassification: internal\nowner: team:platform\naccess_scope: team:platform\ncontains_pii: false\nretention: permanent\nredaction: none\n---\n# Source\n\n## Summary\n\n## Key Concepts\n\n## Entities\n\n## Notable Claims\n\n## Limitations / Gaps\n", encoding="utf-8")
    (wiki / "index.md").write_text((wiki / "index.md").read_text(encoding="utf-8").replace("./concepts/api.md", "./sources/source.md"), encoding="utf-8")
    _configure(module, tmp_path)
    assert module.main([]) == 1
    assert "source_sha256 does not match raw archive" in capsys.readouterr().err


def test_raw_archive_requires_wiki_source_page(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    _bundle(tmp_path)
    (tmp_path / "raw/sources/missing-summary.md").write_text("# archive\n", encoding="utf-8")
    _configure(module, tmp_path)

    assert module.main([]) == 1
    assert "raw archive missing wiki/sources summary page" in capsys.readouterr().err


def test_history_checks_reject_raw_changes_and_log_rewrites(tmp_path: Path, monkeypatch, capsys) -> None:
    module = _load_lint()
    _bundle(tmp_path)
    _configure(module, tmp_path)

    def fake_git_output(*args: str) -> str:
        if "--name-status" in args:
            return "M\traw/sources/immutable.md\nA\traw/sources/new.md\n"
        if args[:1] == ("show",):
            if args[1].startswith("base:"):
                return "# Wiki Log\n\n## 2026-08-05\n\n- **lint** | original\n  - pass\n"
            return "# Wiki Log\n\n## 2026-08-05\n\n- **lint** | changed\n  - pass\n"
        return "@@ -1 +1 @@\n-old\n+new\n"

    monkeypatch.setattr(module, "git_output", fake_git_output)
    assert module.main(["--base", "base"]) == 1
    output = capsys.readouterr().err
    assert "raw archive is immutable" in output
    assert "append-only" in output


def test_history_allows_format_only_log_migration(tmp_path: Path, monkeypatch) -> None:
    module = _load_lint()
    _bundle(tmp_path)
    _configure(module, tmp_path)

    def fake_git_output(*args: str) -> str:
        if "--name-status" in args:
            return ""
        if args[:1] == ("show",):
            if args[1].startswith("base:"):
                return "# Wiki Log\n\n## [2026-08-05] lint | original\n\n- pass\n"
            return "# Wiki Log\n\n## 2026-08-05\n\n- **lint** | original\n  - pass\n"
        return "@@ -1 +1 @@\n-old format\n+new format\n"

    monkeypatch.setattr(module, "git_output", fake_git_output)

    assert module.main(["--base", "base"]) == 0


def test_log_headings_and_stale_pages_are_reported(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    wiki, page = _bundle(tmp_path)
    (wiki / "log.md").write_text("# wrong\n\n## bad entry\n", encoding="utf-8")
    page.write_text(page.read_text(encoding="utf-8").replace("2099-01-01", "2000-01-01"), encoding="utf-8")
    _configure(module, tmp_path)

    assert module.main([]) == 1
    output = capsys.readouterr().err
    assert "must start" in output
    assert "invalid wiki/log.md operation heading" in output
    assert "stale page" in output


def test_v02_date_grouped_log_passes(tmp_path: Path) -> None:
    module = _load_lint()
    wiki, _ = _bundle(tmp_path)
    (wiki / "log.md").write_text(
        "# Wiki Log\n\n"
        "## 2026-08-05\n\n"
        "- **lint** | schema migration\n"
        "  - pass\n",
        encoding="utf-8",
    )
    _configure(module, tmp_path)

    assert module.main([]) == 0


def test_v01_frontmatter_citations_version_and_log_are_rejected(tmp_path: Path, capsys) -> None:
    module = _load_lint()
    wiki, page = _bundle(tmp_path)
    page.write_text(
        page.read_text(encoding="utf-8").replace(
            "status: stable", "status: active\ntimestamp: 2026-08-05T12:00:00Z\nupdated: 2026-08-05\nsource_count: 1"
        ) + "\n# Citations\n\n- legacy\n",
        encoding="utf-8",
    )
    (wiki / "index.md").write_text(
        (wiki / "index.md").read_text(encoding="utf-8").replace('"0.2"', '"0.1"'),
        encoding="utf-8",
    )
    (wiki / "log.md").write_text(
        "# Wiki Log\n\n## [2026-08-05] lint | legacy\n\n- pass\n",
        encoding="utf-8",
    )
    _configure(module, tmp_path)

    assert module.main([]) == 1
    output = capsys.readouterr().err
    for expected in ("status must be", "v0.1 field", "# Citations", 'okf_version: "0.2"', "invalid wiki/log.md"):
        assert expected in output
