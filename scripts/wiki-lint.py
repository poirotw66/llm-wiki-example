#!/usr/bin/env python3
"""Validate this repository's OKF knowledge bundle and repository invariants.

Content rules are checked directly from the working tree.  History-sensitive
rules (raw archive immutability and append-only logs) are checked only when a
Git base revision is supplied; CI supplies that revision for pull requests.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:  # scripts/ uses hyphenated, unimportable filenames.
    sys.path.append(_SCRIPTS)

from _common import (
    LOG_BRACKET_OPERATION,
    LOG_DATE,
    LOG_OPERATION,
    ROOT,
    Paths,
    sha256_file,
)
from _common import git_output as _git_output

#: Bundle under inspection.  ``configure`` repoints every location at once.
PATHS = Paths(ROOT)
FM = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
LINKS = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
MD_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)")
WIKI_STYLE_LINK = re.compile(r"\[\[[^\]]+\]\]")
HEADING = re.compile(r"(?m)^##\s+(.+?)\s*$")
INDEX_SECTIONS = ("Overview", "Concepts", "Entities", "Sources", "Queries", "FAQ")
SOURCE_HEADINGS = ("Summary", "Key Concepts", "Entities", "Notable Claims", "Limitations / Gaps")
VE_HEAD = re.compile(r"(?:^|\n)(?:#{2,4}\s*)?(?:\*\*)?Visual Evidence(?:\*\*)?[^\n]*\n", re.IGNORECASE)
VE_BAN = ("細節以原圖為準", "請見原圖", "請看原圖", "略過圖內", "圖略")
VE_NODE = re.compile(r"層\s*[／/]\s*節點|節點盤點|架構層級")
VE_FLOW = re.compile(r"資料流|控制流|主要資料流|→")
ASSET_EMBED = re.compile(r"!\[[^\]]*\]\((?:(?:\.\./)+)assets/[^)\s]+/p\d+\.png\)")
H2_VE = re.compile(r"(?m)^## Visual Evidence\s*$")
H2_ANY = re.compile(r"(?m)^## ")
V02_STATUS = {"draft", "stable", "deprecated"}
V01_FIELDS = {"timestamp", "updated", "source_count"}
V01_CITATIONS = re.compile(r"(?m)^# Citations\s*$")
RESOURCE_REF = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|/|\./|\.\./|[^\s]+/)[^\s]*$")
CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
REDACTION_STATES = {"none", "applied", "required"}
OWNER = re.compile(r"^(?:team|human|process):[^\s:]+$")
ACCESS_SCOPE = re.compile(r"^(?:public|organization|team:[^\s:]+|named:[^\s:]+)$")
RETENTION = re.compile(r"^(?:permanent|per-policy:[^\s:]+|until:\d{4}-\d{2}-\d{2})$")
ACTOR = re.compile(r"^(?:human:[^\s:]+|process:[^\s:]+|[^\s/]+/[^\s/]+)$")


def configure(root: Path | str) -> Paths:
    """Point every check at ``root``; returns the resulting layout."""
    global PATHS
    PATHS = Paths(Path(root))
    return PATHS


def relative(path: Path) -> str:
    return PATHS.relative(path)


def parse_frontmatter(path: Path, text: str, err: list[str]) -> dict[str, Any] | None:
    match = FM.match(text)
    if not match:
        err.append(f"missing YAML frontmatter: {relative(path)}")
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        err.append(f"invalid YAML frontmatter: {relative(path)}: {exc.problem or exc}")
        return None
    if not isinstance(data, dict):
        err.append(f"frontmatter must be a YAML mapping: {relative(path)}")
        return None
    return data


def is_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_iso_datetime(value: Any) -> bool:
    if isinstance(value, dt.datetime):
        return True
    if not isinstance(value, str):
        return False
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def is_iso_date(value: Any) -> bool:
    if isinstance(value, dt.datetime):
        return False
    if isinstance(value, dt.date):
        return True
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def check_sources(value: Any, page: str, err: list[str]) -> None:
    if not isinstance(value, list):
        err.append(f"frontmatter sources must be a list: {page}")
        return
    if not value:
        err.append(f"frontmatter sources must not be empty: {page}")
        return
    ids: set[str] = set()
    for number, source in enumerate(value, 1):
        if not isinstance(source, dict):
            err.append(f"frontmatter sources[{number}] must be a mapping: {page}")
            continue
        if not is_string(source.get("resource")):
            err.append(f"frontmatter sources[{number}].resource must be a non-empty string: {page}")
        for key in ("id", "title", "author"):
            if key in source and not is_string(source[key]):
                err.append(f"frontmatter sources[{number}].{key} must be a non-empty string: {page}")
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in ids:
                err.append(f"frontmatter sources id must be unique ({source_id!r}): {page}")
            ids.add(source_id)
        usage_count = source.get("usage_count")
        if usage_count is not None and (
            isinstance(usage_count, bool) or not isinstance(usage_count, int) or usage_count < 0
        ):
            err.append(f"frontmatter sources[{number}].usage_count must be a non-negative integer: {page}")
        if "last_modified" in source and not is_iso_date(source["last_modified"]):
            err.append(f"frontmatter sources[{number}].last_modified must be an ISO date: {page}")


def check_event(value: Any, name: str, page: str, err: list[str]) -> None:
    events = value if isinstance(value, list) else [value]
    if not isinstance(value, (dict, list)) or not events:
        err.append(f"frontmatter {name} must be a mapping or non-empty list of mappings: {page}")
        return
    for number, event in enumerate(events, 1):
        if not isinstance(event, dict):
            err.append(f"frontmatter {name}[{number}] must be a mapping: {page}")
            continue
        for key in ("by", "at"):
            if key not in event:
                err.append(f"frontmatter {name}[{number}] requires {key}: {page}")
        if "by" in event and not is_string(event["by"]):
            err.append(f"frontmatter {name}[{number}].by must be a non-empty string: {page}")
        elif "by" in event and not ACTOR.fullmatch(event["by"]):
            err.append(f"frontmatter {name}[{number}].by does not follow the OKF actor convention: {page}")
        if "at" in event and not is_iso_datetime(event["at"]):
            err.append(f"frontmatter {name}[{number}].at must be ISO 8601: {page}")


def check_usage_window(value: Any, page: str, err: list[str]) -> None:
    if not isinstance(value, dict):
        err.append(f"frontmatter usage_window must be a mapping: {page}")
        return
    if not is_iso_date(value.get("from")) or not is_iso_date(value.get("to")):
        err.append(f"frontmatter usage_window requires ISO date from/to values: {page}")


def check_governance(meta: dict[str, Any], page: str, err: list[str]) -> None:
    keys = ("classification", "owner", "access_scope", "contains_pii", "retention", "redaction")
    uses_v02 = "generated" in meta or "sources" in meta
    if uses_v02:
        missing = [key for key in keys if key not in meta]
        if missing:
            err.append(f"v0.2 page missing governance fields ({', '.join(missing)}): {page}")
    if "classification" in meta and meta["classification"] not in CLASSIFICATIONS:
        err.append(f"frontmatter classification has an invalid value: {page}")
    if "owner" in meta and (not is_string(meta["owner"]) or not OWNER.fullmatch(meta["owner"])):
        err.append(f"frontmatter owner must be team:<id>, human:<id>, or process:<id>: {page}")
    if "access_scope" in meta and (
        not is_string(meta["access_scope"]) or not ACCESS_SCOPE.fullmatch(meta["access_scope"])
    ):
        err.append(f"frontmatter access_scope has an invalid value: {page}")
    if "contains_pii" in meta and meta["contains_pii"] not in (True, False, "unknown"):
        err.append(f"frontmatter contains_pii must be true, false, or unknown: {page}")
    if "retention" in meta and (not is_string(meta["retention"]) or not RETENTION.fullmatch(meta["retention"])):
        err.append(f"frontmatter retention has an invalid value: {page}")
    elif isinstance(meta.get("retention"), str) and meta["retention"].startswith("until:"):
        retention_date = meta["retention"].removeprefix("until:")
        if not is_iso_date(retention_date):
            err.append(f"frontmatter retention until date must be an ISO date: {page}")
        elif dt.date.today() >= dt.date.fromisoformat(retention_date):
            err.append(f"retention deadline reached: {page}")
    if "redaction" in meta and meta["redaction"] not in REDACTION_STATES:
        err.append(f"frontmatter redaction has an invalid value: {page}")
    if meta.get("contains_pii") in (True, "unknown") and meta.get("redaction") == "none":
        err.append(f"PII true/unknown cannot use redaction: none: {page}")


def check_metadata(path: Path, meta: dict[str, Any], err: list[str]) -> None:
    page = relative(path)
    if not is_string(meta.get("type")):
        err.append(f"missing or invalid frontmatter type: {page}")
    for key in ("title", "description", "resource"):
        if key in meta and not is_string(meta[key]):
            err.append(f"frontmatter {key} must be a non-empty string: {page}")
    if isinstance(meta.get("resource"), str) and not RESOURCE_REF.fullmatch(meta["resource"]):
        err.append(f"frontmatter resource must be a URI or resolvable path, not a bare slug: {page}")
    if "tags" in meta and (
        not isinstance(meta["tags"], list) or any(not is_string(tag) for tag in meta["tags"])
    ):
        err.append(f"frontmatter tags must be a list of non-empty strings: {page}")
    if "status" in meta and meta["status"] not in V02_STATUS:
        err.append(f"frontmatter status must be draft, stable, or deprecated: {page}")
    for field in sorted(V01_FIELDS & meta.keys()):
        err.append(f"OKF v0.1 field {field!r} is forbidden; use v0.2 metadata: {page}")
    if "sources" in meta:
        check_sources(meta["sources"], page, err)
    if "usage_window" in meta:
        check_usage_window(meta["usage_window"], page, err)
    if "generated" in meta:
        if not isinstance(meta["generated"], dict):
            err.append(f"frontmatter generated must be a mapping: {page}")
        else:
            check_event(meta["generated"], "generated", page, err)
    if "verified" in meta:
        check_event(meta["verified"], "verified", page, err)
    if "stale_after" in meta and not is_iso_date(meta["stale_after"]):
        err.append(f"frontmatter stale_after must be an ISO date: {page}")
    check_governance(meta, page, err)


def load_pages(err: list[str]) -> dict[Path, tuple[str, dict[str, Any]]]:
    pages: dict[Path, tuple[str, dict[str, Any]]] = {}
    for path in PATHS.wiki_pages():
        text = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(path, text, err)
        if meta is not None:
            check_metadata(path, meta, err)
            if V01_CITATIONS.search(text):
                err.append(f"OKF v0.1 '# Citations' section is forbidden; use sources and keyed footnotes: {relative(path)}")
            pages[path] = (text, meta)
    return pages


def check_index(err: list[str]) -> None:
    path = PATHS.index
    if not path.is_file():
        err.append("missing bundle root index: wiki/index.md")
        return
    text = path.read_text(encoding="utf-8")
    meta_match = FM.match(text)
    if meta_match:
        try:
            meta = yaml.safe_load(meta_match.group(1))
        except yaml.YAMLError as exc:
            err.append(f"invalid YAML frontmatter: wiki/index.md: {exc.problem or exc}")
            meta = None
        if not isinstance(meta, dict) or set(meta) - {"okf_version"}:
            err.append("wiki/index.md frontmatter may contain only okf_version")
        elif str(meta.get("okf_version")) != "0.2":
            err.append('wiki/index.md must declare okf_version: "0.2"')
    else:
        err.append('wiki/index.md must declare okf_version: "0.2" in frontmatter')
    headings = HEADING.findall(text)
    missing = [section for section in INDEX_SECTIONS if section not in headings]
    if missing:
        err.append(f"wiki/index.md missing required sections: {', '.join(missing)}")
    order = [headings.index(section) for section in INDEX_SECTIONS if section in headings]
    if order != sorted(order):
        err.append("wiki/index.md required sections are out of order")


def check_log(err: list[str]) -> None:
    path = PATHS.log
    if not path.is_file():
        err.append("missing reserved operation log: wiki/log.md")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "# Wiki Log":
        err.append("wiki/log.md must start with '# Wiki Log'")
    in_date_group = False
    for line in lines:
        if line.startswith("## "):
            in_date_group = bool(LOG_DATE.fullmatch(line))
            if not in_date_group:
                err.append(f"invalid wiki/log.md operation heading: {line}")
        elif LOG_OPERATION.fullmatch(line) and not in_date_group:
            err.append(f"wiki/log.md operation must be under an ISO date heading: {line}")
        elif line.startswith("- **") and " | " in line and not LOG_OPERATION.fullmatch(line):
            err.append(f"invalid wiki/log.md operation entry: {line}")


def check_links(pages: dict[Path, tuple[str, dict[str, Any]]], err: list[str]) -> dict[Path, int]:
    backlinks: dict[Path, int] = defaultdict(int)
    for path, (text, _) in pages.items():
        if WIKI_STYLE_LINK.search(text):
            err.append(f"wiki-style link is forbidden: {relative(path)}")
        for target in LINKS.findall(text) + IMG.findall(text):
            target = target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            rel = target.split("#", 1)[0]
            if not rel:
                continue
            if rel.startswith("/"):
                err.append(f"root-path link: {relative(path)} -> {target}")
                continue
            destination = (path.parent / rel).resolve()
            if not destination.is_file():
                err.append(f"broken link: {relative(path)} -> {target}")
            elif destination in pages:
                backlinks[destination] += 1
    return backlinks


def archive_slug(meta: dict[str, Any]) -> str | None:
    slug = meta.get("archive_slug")
    if isinstance(slug, str) and slug.strip():
        return slug.removesuffix(".md").split("/")[-1]
    for source in meta.get("sources", []):
        if not isinstance(source, dict):
            continue
        resource = source.get("resource")
        if isinstance(resource, str) and "raw/sources/" in resource and resource.endswith(".md"):
            return Path(resource).stem
    return None


def check_purpose(err: list[str]) -> None:
    path = PATHS.purpose
    if not path.is_file():
        err.append("missing operational purpose file: ops/purpose.md")
        return
    text = path.read_text(encoding="utf-8")
    if "# Purpose" not in text and "# 目的" not in text:
        err.append("ops/purpose.md must contain '# Purpose' or '# 目的'")
        return
    match = FM.match(text)
    if not match:
        err.append("ops/purpose.md must declare mode: template or production in YAML frontmatter")
        return
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        err.append("ops/purpose.md has invalid YAML frontmatter")
        return
    mode = meta.get("mode") if isinstance(meta, dict) else None
    if mode not in {"template", "production"}:
        err.append("ops/purpose.md mode must be template or production")
    if mode == "production":
        if "（填寫）" in text or "<填寫" in text:
            err.append("production ops/purpose.md must not retain template placeholders")
        for heading in ("Goals", "Key questions", "Scope", "Audience & owners"):
            if f"## {heading}" not in text:
                err.append(f"production ops/purpose.md missing ## {heading}")


def check_archive_has_source_page(err: list[str]) -> None:
    """Every raw/sources archive must have a matching wiki/sources summary page."""
    if not PATHS.raw_sources.is_dir():
        return
    wiki_stems = {
        path.stem
        for path in PATHS.wiki_sources.glob("*.md")
        if path.is_file()
    } if PATHS.wiki_sources.is_dir() else set()
    for archive in sorted(PATHS.raw_sources.glob("*.md")):
        if archive.stem not in wiki_stems:
            err.append(
                "raw archive missing wiki/sources summary page: "
                f"raw/sources/{archive.name} (expected wiki/sources/{archive.stem}.md)"
            )


def check_resources(pages: dict[Path, tuple[str, dict[str, Any]]], err: list[str]) -> None:
    for path, (_, meta) in pages.items():
        slug = archive_slug(meta)
        if path.parent == PATHS.wiki_sources and not slug:
            err.append(f"wiki/sources page must declare archive_slug or a raw/sources entry: {relative(path)}")
        if slug and not (PATHS.raw_sources / f"{slug}.md").is_file():
            err.append(f"missing raw archive: {relative(path)} archive_slug={slug}")


def check_staleness(pages: dict[Path, tuple[str, dict[str, Any]]], err: list[str]) -> None:
    today = dt.date.today()
    for path, (_, meta) in pages.items():
        stale_after = meta.get("stale_after")
        if isinstance(stale_after, str):
            try:
                stale_after = dt.date.fromisoformat(stale_after)
            except ValueError:
                stale_after = None
        if isinstance(stale_after, dt.date) and today >= stale_after:
            err.append(f"stale page (stale_after reached): {relative(path)}")


def check_source_schema(pages: dict[Path, tuple[str, dict[str, Any]]], err: list[str]) -> None:
    for path, (text, meta) in pages.items():
        if path.parent != PATHS.wiki_sources:
            continue
        if meta.get("type") != "source":
            err.append(f"wiki/sources page must have type: source: {relative(path)}")
        headings = set(HEADING.findall(text))
        missing = [heading for heading in SOURCE_HEADINGS if heading not in headings]
        if missing:
            err.append(f"source page missing required headings ({', '.join(missing)}): {relative(path)}")
        receipt = meta.get("analysis_receipt")
        if not isinstance(receipt, dict):
            err.append(f"wiki/sources page missing analysis_receipt: {relative(path)}")
            continue
        if not is_string(receipt.get("version")):
            err.append(f"analysis_receipt.version must be a non-empty string: {relative(path)}")
        for key in ("sha256", "source_sha256"):
            digest = receipt.get(key)
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                err.append(f"analysis_receipt.{key} must be a lowercase SHA-256 digest: {relative(path)}")
        actor = receipt.get("generated_by")
        if not is_string(actor) or not ACTOR.fullmatch(actor):
            err.append(f"analysis_receipt.generated_by must follow the OKF actor convention: {relative(path)}")
        if not is_iso_datetime(receipt.get("generated_at")):
            err.append(f"analysis_receipt.generated_at must be ISO 8601: {relative(path)}")
        slug = archive_slug(meta)
        archive = PATHS.raw_sources / f"{slug}.md" if slug else None
        if archive and archive.is_file() and receipt.get("source_sha256") != sha256_file(archive):
            err.append(f"analysis_receipt.source_sha256 does not match raw archive: {relative(path)}")


def check_catalog_and_backlinks(pages: dict[Path, tuple[str, dict[str, Any]]], backlinks: dict[Path, int], err: list[str]) -> None:
    index = PATHS.index
    index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
    indexed: set[Path] = set()
    for target in MD_LINK.findall(index_text):
        destination = (index.parent / target.split("#", 1)[0]).resolve()
        if destination in pages:
            indexed.add(destination)
    for path in pages:
        if path not in indexed:
            err.append(f"page missing from wiki/index.md: {relative(path)}")
        # The canonical catalog is a valid inbound bundle reference even though
        # index.md itself is a reserved, non-Concept page.
        if not backlinks[path] and path not in indexed:
            err.append(f"orphan page (no inbound wiki link): {relative(path)}")


def split_visual_evidence_blocks(text: str) -> list[str]:
    starts = [match.start() for match in VE_HEAD.finditer(text)]
    starts.append(len(text))
    return [text[starts[i] : starts[i + 1]].strip() for i in range(len(starts) - 1)]


def visual_evidence_issues(block: str) -> list[str]:
    issues = [f"banned phrase {phrase!r}" for phrase in VE_BAN if phrase in block]
    if not VE_NODE.search(block):
        issues.append("missing 層／節點盤點")
    if not VE_FLOW.search(block):
        issues.append("missing 資料流／控制流")
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", block)
    body = re.sub(r"(?m)^[-*]\s*\*\*[^*]+\*\*[：:].*$", "", body)
    if len(re.sub(r"\s+", "", body)) < 120:
        issues.append("structured transcription too short")
    return issues


def visual_evidence_placement_issues(text: str) -> list[str]:
    embeds = ASSET_EMBED.findall(text)
    if len(embeds) < 2:
        return []
    for match in H2_VE.finditer(text):
        next_heading = H2_ANY.search(text, match.end())
        section = text[match.end() : next_heading.start()] if next_heading else text[match.end() :]
        if len(ASSET_EMBED.findall(section)) == len(embeds):
            return ["Visual Evidence dumped at end under ## Visual Evidence; place each block inline under its page/section"]
    return []


def check_visual(pages: dict[Path, tuple[str, dict[str, Any]]], err: list[str]) -> None:
    if not PATHS.raw_assets.is_dir():
        return
    source_pages = [(path, value) for path, value in pages.items() if path.parent == PATHS.wiki_sources]
    for directory in sorted(path for path in PATHS.raw_assets.iterdir() if path.is_dir()):
        if not list(directory.glob("p*.png")):
            continue
        slug = directory.name
        candidates = [(path, value) for path, value in source_pages if archive_slug(value[1]) == slug or f"raw/assets/{slug}/" in value[0]]
        if not candidates:
            err.append(f"visual assets without wiki source: raw/assets/{slug}/")
            continue
        for page, (text, _) in candidates:
            if "## Visual Assets" not in text:
                err.append(f"missing ## Visual Assets: {relative(page)}")
                continue
            embeds = [target for target in IMG.findall(text) if f"raw/assets/{slug}/" in target]
            if not embeds:
                err.append(f"no visual embeds: {relative(page)} (raw/assets/{slug}/)")
            for target in embeds:
                if not (page.parent / target.split("#", 1)[0]).resolve().is_file():
                    err.append(f"broken visual embed: {relative(page)} -> {target}")


def check_visual_evidence(pages: dict[Path, tuple[str, dict[str, Any]]], err: list[str]) -> None:
    for page, (page_text, meta) in pages.items():
        if page.parent != PATHS.wiki_sources:
            continue
        slug = archive_slug(meta)
        if not slug:
            continue
        archive = PATHS.raw_sources / f"{slug}.md"
        if not archive.is_file():
            continue
        text = archive.read_text(encoding="utf-8")
        blocks = split_visual_evidence_blocks(text)
        if "## Visual Assets" in page_text and not blocks:
            err.append(f"wiki has visuals but archive lacks Visual Evidence: {relative(archive)}")
        for number, block in enumerate(blocks, 1):
            for issue in visual_evidence_issues(block):
                err.append(f"weak Visual Evidence #{number} in {relative(archive)}: {issue}")
        for issue in visual_evidence_placement_issues(text):
            err.append(f"{issue}: {relative(archive)}")


def git_output(*args: str) -> str | None:
    return _git_output(*args, cwd=PATHS.root)


def normalized_log_history(text: str) -> list[str]:
    """Normalize operation history so a format-only migration remains append-only."""
    tokens: list[str] = []
    current_date: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        date_match = LOG_DATE.fullmatch(line)
        bracket_match = LOG_BRACKET_OPERATION.fullmatch(line)
        operation_match = LOG_OPERATION.fullmatch(line)
        if date_match:
            current_date = line.removeprefix("## ")
        elif bracket_match:
            current_date = bracket_match.group("date")
            tokens.append(
                f"OP|{current_date}|{bracket_match.group('operation')}|{bracket_match.group('title')}"
            )
        elif operation_match and current_date:
            tokens.append(
                f"OP|{current_date}|{operation_match.group('operation')}|{operation_match.group('title')}"
            )
        elif line.startswith("- "):
            tokens.append(f"BODY|{line.removeprefix('- ').strip()}")
        elif line:
            tokens.append(f"TEXT|{line}")
    return tokens


def check_history(base: str | None, err: list[str]) -> None:
    if not base:
        return
    names = git_output("diff", "--name-status", "-M", f"{base}...HEAD")
    if names is None:
        err.append(f"cannot inspect Git base revision: {base}")
        return
    for line in names.splitlines():
        fields = line.split("\t")
        status, paths = fields[0], fields[1:]
        if any(path.startswith("raw/") for path in paths) and not status.startswith("A"):
            err.append(f"raw archive is immutable relative to {base}: {line}")
    log_diff = git_output("diff", "--unified=0", f"{base}...HEAD", "--", "wiki/log.md")
    if log_diff is not None:
        removed = [line for line in log_diff.splitlines() if line.startswith("-") and not line.startswith("---")]
        if removed:
            old_log = git_output("show", f"{base}:wiki/log.md")
            new_log = git_output("show", "HEAD:wiki/log.md")
            old_tokens = normalized_log_history(old_log or "")
            new_tokens = normalized_log_history(new_log or "")
            if not old_tokens or new_tokens[: len(old_tokens)] != old_tokens:
                err.append(f"wiki/log.md must be semantically append-only relative to {base}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git revision used for history-sensitive checks")
    parser.add_argument("--root", help="Bundle root to lint (default: this repository)")
    args = parser.parse_args(argv)
    if args.root:
        configure(args.root)
    err: list[str] = []
    check_index(err)
    check_log(err)
    check_purpose(err)
    pages = load_pages(err)
    backlinks = check_links(pages, err)
    check_resources(pages, err)
    check_archive_has_source_page(err)
    check_staleness(pages, err)
    check_source_schema(pages, err)
    check_catalog_and_backlinks(pages, backlinks, err)
    check_visual(pages, err)
    check_visual_evidence(pages, err)
    check_history(args.base or os.environ.get("WIKI_LINT_BASE"), err)
    if err:
        print(f"wiki-lint: {len(err)} issue(s)", file=sys.stderr)
        print("\n".join(err), file=sys.stderr)
        return 1
    print("wiki-lint: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
