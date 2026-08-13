#!/usr/bin/env python3
"""Append-only Skill usage ledger and ccusage-style summaries for LLM Wiki."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:  # scripts/ uses hyphenated, unimportable filenames.
    sys.path.append(_SCRIPTS)

# The log grammar is shared with wiki-lint, which enforces it: a private copy
# here could accept entries lint rejects, or silently drop token attribution.
from _common import LOG_DATE, LOG_OPERATION, OPERATIONS as VALID_OPERATIONS

DEFAULT_LEDGER = Path(".llm-wiki/usage/events.jsonl")
DEFAULT_ACTIVE_DIR = Path(".llm-wiki/usage/active")
DEFAULT_PRICING = Path("config/skill-usage-pricing.json")
OPERATION_SKILLS = {operation: f"llm-wiki-{operation}" for operation in VALID_OPERATIONS}


def parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ledger_path(value: str | None) -> Path:
    return Path(value) if value else DEFAULT_LEDGER


def load_pricing(path: str | None) -> dict[str, dict[str, float]]:
    pricing_path = Path(path) if path else DEFAULT_PRICING
    if not pricing_path.exists():
        return {}
    try:
        payload = json.loads(pricing_path.read_text(encoding="utf-8"))
        return payload.get("models", {})
    except (OSError, json.JSONDecodeError):
        return {}


def estimated_cost_range(event: dict[str, Any], pricing: dict[str, dict[str, float]]) -> tuple[float, float] | None:
    total_tokens = number(event, "total_tokens")
    rates = pricing.get(event.get("model"))
    if total_tokens is None or not rates:
        return None
    return (
        total_tokens * rates["cached_input_per_million"] / 1_000_000,
        total_tokens * rates["output_per_million"] / 1_000_000,
    )


def active_path(operation: str, thread_id: str) -> Path:
    return DEFAULT_ACTIVE_DIR / f"{operation}-{thread_id}.json"


def codex_state_path(value: str | None) -> Path | None:
    if value:
        path = Path(value)
        return path if path.is_file() else None
    candidates = sorted((Path.home() / ".codex").glob("state_*.sqlite"), key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def codex_session_paths(codex_home: str | None) -> list[Path]:
    roots = [Path(codex_home)] if codex_home else [Path.home() / ".codex"]
    paths: list[Path] = []
    for root in roots:
        for directory in (root / "sessions", root / "archived_sessions"):
            if directory.exists():
                paths.extend(directory.rglob("*.jsonl"))
    return paths


def codex_usage_records(codex_home: str | None, all_workspaces: bool = False) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    allowed_cwds = {str(Path.cwd()), str(Path.cwd().resolve())}
    for path in codex_session_paths(codex_home):
        current_model: str | None = None
        session_cwd: str | None = None
        session_id = path.stem
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                event = json.loads(line)
                timestamp = parse_timestamp(event.get("timestamp", ""))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            if event.get("cwd"):
                session_cwd = event["cwd"]
            if event.get("session_id"):
                session_id = event["session_id"]
            payload = event.get("payload") or {}
            if not isinstance(payload, dict):
                continue
            if payload.get("cwd"):
                session_cwd = payload["cwd"]
            if payload.get("model"):
                current_model = payload["model"]
            info = payload.get("info") or {}
            usage = info.get("last_token_usage") if isinstance(info, dict) else None
            if payload.get("type") != "token_count" or not isinstance(usage, dict):
                continue
            if not all_workspaces and session_cwd not in allowed_cwds:
                continue
            record = {key: usage.get(key, 0) for key in (
                "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                "output_tokens", "reasoning_output_tokens", "total_tokens")}
            record.update({"timestamp": timestamp.isoformat(), "model": current_model or "unknown", "session_id": session_id, "cwd": session_cwd})
            records.append(record)
    return records


def codex_report(args: argparse.Namespace) -> int:
    if args.by is None:
        if args.format == "json":
            combined: dict[str, Any] = {}
            for section in ("model", "day", "session"):
                args.by = section
                # Re-enter the same aggregation path and capture the JSON-shaped result below.
                combined[section] = codex_report_data(args)
            print(json.dumps(combined, ensure_ascii=False, indent=2))
            return 0
        for index, section in enumerate(("model", "day", "session")):
            if index:
                print()
            print(f"## {section}")
            args.by = section
            codex_report(args)
        return 0
    # The data function returns a JSON-shaped object for reuse by the JSON
    # formatter.  The CLI handler itself must return an integer exit status;
    # otherwise ``sys.exit(dict)`` prints the dict and reports failure.
    codex_report_data(args, print_table=True)
    return 0


def codex_report_data(args: argparse.Namespace, print_table: bool = False) -> dict[str, Any]:
    records = codex_usage_records(args.codex_home, args.all_workspaces)
    since = parse_timestamp(args.since).date() if args.since else None
    until = parse_timestamp(args.until).date() if args.until else None
    records = [record for record in records if not since or parse_timestamp(record["timestamp"]).date() >= since]
    records = [record for record in records if not until or parse_timestamp(record["timestamp"]).date() <= until]
    pricing = load_pricing(args.pricing)
    groups: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for record in records:
        if args.by == "day":
            key = parse_timestamp(record["timestamp"]).date().isoformat()
        elif args.by == "session":
            key = record["session_id"]
        else:
            key = record["model"]
        group = groups[key]
        group["runs"] += 1
        for field in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens"):
            group[field] += record[field]
        cost = exact_cost(record, pricing)
        if cost is not None:
            group["cost_usd"] += cost
            group["cost_known"] += 1
    if args.format == "json":
        return {"event_count": len(records), "group_by": args.by, "groups": groups}
    headers = ("Group", "Turns", "Input", "Cached", "Output", "Reasoning", "Total", "Cost USD")
    rows = []
    for key, group in sorted(groups.items()):
        rows.append((key, display_number(group["runs"]), display_number(group["input_tokens"]),
                     display_number(group["cached_input_tokens"]), display_number(group["output_tokens"]),
                     display_number(group["reasoning_output_tokens"]), display_number(group["total_tokens"]),
                     f"${group['cost_usd']:.4f}" if group["cost_known"] else "—"))
    if not rows:
        print("No Codex session usage matched.")
        return {"event_count": 0, "group_by": args.by, "groups": {}}
    widths = [max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)]
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
    return {"event_count": len(records), "group_by": args.by, "groups": groups}


def codex_usage_between(start: str, end: str, codex_home: str | None) -> dict[str, Any] | None:
    start_time, end_time = parse_timestamp(start), parse_timestamp(end)
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "cache_write_input_tokens": 0,
              "output_tokens": 0, "reasoning_output_tokens": 0, "total_tokens": 0}
    model: str | None = None
    found = False
    for path in codex_session_paths(codex_home):
        current_model: str | None = None
        session_cwd: str | None = None
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                event = json.loads(line)
                timestamp = parse_timestamp(event.get("timestamp", ""))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            payload = event.get("payload") or {}
            if event.get("cwd"):
                session_cwd = event["cwd"]
            if isinstance(payload, dict):
                if payload.get("cwd"):
                    session_cwd = payload["cwd"]
                if payload.get("model"):
                    current_model = payload["model"]
                info = payload.get("info") or {}
                last_usage = info.get("last_token_usage") if isinstance(info, dict) else None
                if payload.get("type") == "token_count" and isinstance(last_usage, dict) and start_time <= timestamp <= end_time:
                    if session_cwd and session_cwd not in (str(Path.cwd()), str(Path.cwd().resolve())):
                        continue
                    found = True
                    model = current_model or model
                    for field in totals:
                        value = last_usage.get(field)
                        if isinstance(value, (int, float)):
                            totals[field] += value
    if not found:
        return None
    totals["model"] = model
    totals["token_source"] = "codex_session_jsonl.last_token_usage"
    return totals


def exact_cost(usage: dict[str, Any], pricing: dict[str, dict[str, float]]) -> float | None:
    rates = pricing.get(usage.get("model"))
    if not rates:
        return None
    input_tokens = usage.get("input_tokens", 0)
    cached_tokens = usage.get("cached_input_tokens", 0)
    cache_write_tokens = usage.get("cache_write_input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    uncached_tokens = max(input_tokens - cached_tokens - cache_write_tokens, 0)
    return (
        uncached_tokens * rates["input_per_million"]
        + cached_tokens * rates["cached_input_per_million"]
        + cache_write_tokens * rates["input_per_million"] * 1.25
        + output_tokens * rates["output_per_million"]
    ) / 1_000_000


def codex_thread(state_path: Path, thread_id: str | None = None) -> dict[str, Any] | None:
    try:
        connection = sqlite3.connect(f"file:{state_path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        if thread_id:
            row = connection.execute(
                "SELECT id, tokens_used, model FROM threads WHERE id = ?", (thread_id,)
            ).fetchone()
        else:
            cwd_paths = (str(Path.cwd()), str(Path.cwd().resolve()))
            row = connection.execute(
                "SELECT id, tokens_used, model FROM threads WHERE cwd IN (?, ?) AND archived = 0 "
                "ORDER BY updated_at_ms DESC LIMIT 1", cwd_paths
            ).fetchone()
        connection.close()
    except sqlite3.Error:
        return None
    return dict(row) if row else None


def start(args: argparse.Namespace) -> int:
    state_path = codex_state_path(args.codex_state)
    thread = codex_thread(state_path) if state_path else None
    if not thread:
        print("Codex Desktop token counter unavailable; this operation will be counted without token measurement.")
        return 0
    snapshot = {
        "schema_version": 1,
        "operation": args.operation,
        "thread_id": thread["id"],
        "tokens_used": thread["tokens_used"],
        "model": thread.get("model"),
        "started_at": iso_now(),
        "started_at_epoch": time.time(),
        "title": args.title,
    }
    destination = active_path(args.operation, thread["id"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"started {args.operation} token snapshot")
    return 0


def latest_log_entry(operation: str, log_path: Path, title: str | None = None) -> dict[str, str] | None:
    entries = [entry for entry in log_entries(log_path) if entry["operation"] == operation and (not title or entry["title"] == title)]
    return entries[-1] if entries else None


def finish(args: argparse.Namespace) -> int:
    snapshots = sorted(DEFAULT_ACTIVE_DIR.glob(f"{args.operation}-*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    snapshot_path: Path | None = snapshots[0] if snapshots else None
    if snapshot_path:
        try:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print("Token snapshot is unreadable; operation will be counted without token measurement.")
            return 0
    else:
        # Self-heal a missed `start`: use the latest valid measured event as the
        # lower bound.  This is conservative and explicitly marked below; it
        # prevents a silent zero-token event while still producing a useful
        # per-operation estimate from the session JSONL.
        prior_events = read_events(ledger_path(args.ledger))
        invalidated = {event.get("invalidates_event_id") for event in prior_events}
        prior_times = [
            parse_timestamp(event["timestamp"])
            for event in prior_events
            if event.get("event_id") not in invalidated
            and isinstance(event.get("total_tokens"), (int, float))
            and event.get("total_tokens", 0) > 0
            and event.get("measurement", "").startswith("codex_")
        ]
        if not prior_times:
            print("No start snapshot or prior measured boundary; refusing to record 0 token(s).")
            return 0
        inferred_start = max(prior_times)
        snapshot = {
            "operation": args.operation,
            "thread_id": None,
            "model": None,
            "started_at": inferred_start.isoformat(),
            "started_at_epoch": inferred_start.timestamp(),
            "title": args.title,
            "inferred_start": True,
        }
        print(f"No start snapshot; auto-recovering from previous measured boundary {inferred_start.isoformat()}")
    finished_at = iso_now()
    usage = codex_usage_between(snapshot["started_at"], finished_at, args.codex_home)
    state_path = codex_state_path(args.codex_state)
    thread = codex_thread(state_path, snapshot.get("thread_id")) if state_path else None
    if usage is None and (not thread or "tokens_used" not in snapshot):
        print("Codex session usage unavailable; operation will be counted without token measurement.")
        return 0
    entry = latest_log_entry(args.operation, Path(args.log), snapshot.get("title"))
    source_key = log_key(entry) if entry else None
    event = {
        "schema_version": 1,
        "event_id": f"codex-{uuid.uuid4().hex}",
        "timestamp": finished_at,
        "operation": args.operation,
        "primary_skill": OPERATION_SKILLS[args.operation],
        "skills": [OPERATION_SKILLS[args.operation]],
        "model": (usage or {}).get("model") or (thread or {}).get("model") or snapshot.get("model"),
        "total_tokens": (usage or {}).get("total_tokens") if usage else thread["tokens_used"] - snapshot["tokens_used"],
        "duration_seconds": round(time.time() - snapshot["started_at_epoch"], 3),
        "status": status_from_log(entry["body"]) if entry else "success",
        "measurement": (
            "codex_session_jsonl_since_previous_event_recovery"
            if usage and snapshot.get("inferred_start")
            else "codex_session_jsonl_last_token_usage" if usage
            else "codex_desktop_thread_delta_fallback"
        ),
    }
    if usage:
        for field in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens"):
            event[field] = usage.get(field, 0)
        pricing = load_pricing(args.pricing)
        event["cost_usd"] = exact_cost(usage, pricing)
    elif thread["tokens_used"] - snapshot["tokens_used"] < 0:
        print("Codex token counter moved backwards; no token event was recorded.")
        return 0
    if source_key:
        event["source_log_key"] = source_key
        event["supersedes_source_log_key"] = source_key
    destination = ledger_path(args.ledger)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    if snapshot_path:
        snapshot_path.unlink()
    cost_label = f"${event['cost_usd']:.4f}" if isinstance(event.get("cost_usd"), (int, float)) else "—"
    model_label = event.get("model") or "unknown"
    print(f"recorded {event['total_tokens']:,} token(s) for {args.operation} | model={model_label} | cost={cost_label}")
    return 0


def invalidate(args: argparse.Namespace) -> int:
    destination = ledger_path(args.ledger)
    event = {
        "schema_version": 1,
        "event_id": f"invalidate-{uuid.uuid4().hex}",
        "timestamp": iso_now(),
        "invalidates_event_id": args.event_id,
        "reason": args.reason,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"invalidated {args.event_id}")
    return 0


def record(args: argparse.Namespace) -> int:
    primary_skill = OPERATION_SKILLS[args.operation]
    skills = list(dict.fromkeys([primary_skill, *args.skill]))
    timestamp = args.timestamp or iso_now()
    try:
        parse_timestamp(timestamp)
    except ValueError as error:
        raise SystemExit(f"invalid --timestamp: {error}") from error

    event = {
        "schema_version": 1,
        "event_id": args.event_id or f"{args.operation}-{timestamp.replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:12]}",
        "timestamp": timestamp,
        "operation": args.operation,
        "primary_skill": primary_skill,
        "skills": skills,
        "model": args.model,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "cache_read_tokens": args.cache_read_tokens,
        "cache_write_tokens": args.cache_write_tokens,
        "total_tokens": args.total_tokens,
        "cost_usd": args.cost_usd,
        "duration_seconds": args.duration_seconds,
        "status": args.status,
    }
    if args.note:
        event["note"] = args.note

    destination = ledger_path(args.ledger)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"recorded {event['event_id']} -> {destination}")
    return 0


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            parse_timestamp(event["timestamp"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise SystemExit(f"invalid event at {path}:{line_number}: {error}") from error
        events.append(event)
    return events


def log_entries(log_path: Path) -> list[dict[str, str]]:
    if not log_path.exists():
        return []
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    current_date: str | None = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        date_match = LOG_DATE.match(line)
        operation_match = LOG_OPERATION.match(line)
        if date_match:
            if current:
                entries.append(current)
                current = None
            current_date = date_match.group("date")
        elif operation_match and current_date:
            if current:
                entries.append(current)
            current = {"date": current_date, **operation_match.groupdict(), "body": ""}
        elif current:
            current["body"] += line + "\n"
    if current:
        entries.append(current)
    return entries


def status_from_log(body: str) -> str:
    normalized = body.lower()
    if "no-op" in normalized:
        return "no-op"
    if "pass" in normalized:
        return "pass"
    return "success"


def log_key(entry: dict[str, str]) -> str:
    return f"{entry['date']}|{entry['operation']}|{entry['title']}"


def sync_from_log(ledger: Path, log_path: Path) -> int:
    events = read_events(ledger)
    known_keys = {event.get("source_log_key") for event in events}
    additions: list[dict[str, Any]] = []
    for entry in log_entries(log_path):
        source_key = log_key(entry)
        if source_key in known_keys:
            continue
        additions.append({
            "schema_version": 1,
            "event_id": f"log-{uuid.uuid5(uuid.NAMESPACE_URL, source_key).hex}",
            "timestamp": f"{entry['date']}T00:00:00Z",
            "operation": entry["operation"],
            "primary_skill": OPERATION_SKILLS[entry["operation"]],
            "skills": [OPERATION_SKILLS[entry["operation"]]],
            "status": status_from_log(entry["body"]),
            "source_log_key": source_key,
        })
    if additions:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as handle:
            for event in additions:
                handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    return len(additions)


def sync(args: argparse.Namespace) -> int:
    count = sync_from_log(ledger_path(args.ledger), Path(args.log))
    print(f"synced {count} operation event(s) from {args.log}")
    return 0


def number(event: dict[str, Any], field: str) -> float | None:
    value = event.get(field)
    return float(value) if isinstance(value, (int, float)) else None


def display_number(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}"


def display_metric(group: dict[str, float], field: str, decimals: int = 0) -> str:
    return display_number(group[field], decimals) if group[f"{field}_known"] else "—"


def report(args: argparse.Namespace) -> int:
    ledger = ledger_path(args.ledger)
    if not args.no_sync:
        sync_from_log(ledger, Path(args.log))
    events = read_events(ledger)
    since = parse_timestamp(args.since).date() if args.since else None
    until = parse_timestamp(args.until).date() if args.until else None
    filtered = []
    for event in events:
        date = parse_timestamp(event["timestamp"]).date()
        if (since and date < since) or (until and date > until):
            continue
        filtered.append(event)

    invalidated_event_ids = {event.get("invalidates_event_id") for event in filtered}
    pricing = load_pricing(args.pricing)
    measured_log_keys = {
        event.get("supersedes_source_log_key")
        for event in filtered
        if event.get("event_id") not in invalidated_event_ids and isinstance(event.get("total_tokens"), (int, float))
    }
    groups: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for event in filtered:
        if event.get("event_id") in invalidated_event_ids:
            continue
        if "operation" not in event:
            continue
        if event.get("source_log_key") in measured_log_keys and not isinstance(event.get("total_tokens"), (int, float)):
            continue
        if args.by == "day":
            keys = [parse_timestamp(event["timestamp"]).date().isoformat()]
        elif args.by == "run":
            source_key = event.get("source_log_key")
            if isinstance(source_key, str) and "|" in source_key:
                keys = [source_key]
            else:
                keys = [event.get("event_id", "unknown")]
        elif args.by == "operation":
            keys = [event["operation"]]
        elif args.by == "model":
            keys = [event.get("model") or "unknown"]
        else:
            keys = event.get("skills") or [event.get("primary_skill", "unknown")]
        for key in keys:
            group = groups[key]
            group["runs"] += 1
            for field in ("total_tokens", "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "cost_usd", "duration_seconds"):
                value = number(event, field)
                if value is not None:
                    group[field] += value
                    group[f"{field}_known"] += 1
            cost_range = estimated_cost_range(event, pricing)
            if cost_range:
                group["estimated_cost_usd_min"] += cost_range[0]
                group["estimated_cost_usd_max"] += cost_range[1]
                group["estimated_cost_usd_known"] += 1

    if args.format == "json":
        output = {key: dict(value) for key, value in sorted(groups.items())}
        print(json.dumps({"event_count": len(filtered), "group_by": args.by, "groups": output}, ensure_ascii=False, indent=2))
        return 0

    headers = ("Group", "Runs", "Total tokens", "API equiv. USD", "Input", "Output", "Seconds")
    rows = []
    for key, group in sorted(groups.items()):
        if group["cost_usd_known"]:
            estimated_cost = f"${group['cost_usd']:.4f}"
        elif group["estimated_cost_usd_known"]:
            estimated_cost = f"${group['estimated_cost_usd_min']:.4f}–${group['estimated_cost_usd_max']:.4f}"
        else:
            estimated_cost = "—"
        rows.append((key, display_number(group["runs"]), display_metric(group, "total_tokens"), estimated_cost,
                     display_metric(group, "input_tokens"), display_metric(group, "output_tokens"),
                     display_metric(group, "duration_seconds", 1)))
    if not rows:
        print("No usage events matched. Run a wiki operation first.")
        return 0
    widths = [max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)]
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track and report LLM Wiki Skill usage.")
    parser.add_argument("--ledger", help="override ledger path (default: .llm-wiki/usage/events.jsonl)")
    parser.add_argument("--pricing", help="override pricing JSON (default: config/skill-usage-pricing.json)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record", help="append one operation event")
    record_parser.add_argument("operation", choices=VALID_OPERATIONS)
    record_parser.add_argument("--skill", action="append", default=[], help="additional Skill or helper used; repeatable")
    record_parser.add_argument("--model", help="model identifier when supplied by the Agent runtime")
    record_parser.add_argument("--input-tokens", type=int, help="measured input tokens")
    record_parser.add_argument("--output-tokens", type=int, help="measured output tokens")
    record_parser.add_argument("--cache-read-tokens", type=int, help="measured cache-read tokens")
    record_parser.add_argument("--cache-write-tokens", type=int, help="measured cache-write tokens")
    record_parser.add_argument("--total-tokens", type=int, help="measured total tokens when input/output split is unavailable")
    record_parser.add_argument("--cost-usd", type=float, help="measured or provider-reported USD cost")
    record_parser.add_argument("--duration-seconds", type=float, help="wall-clock duration")
    record_parser.add_argument("--status", choices=("success", "pass", "no-op", "failed"), default="success")
    record_parser.add_argument("--note", help="short non-sensitive note; never store source contents")
    record_parser.add_argument("--timestamp", help="ISO 8601 timestamp; defaults to now (UTC)")
    record_parser.add_argument("--event-id", help="stable unique id; defaults to operation + timestamp")
    record_parser.set_defaults(handler=record)

    start_parser = subparsers.add_parser("start", help="snapshot the current Codex Desktop task token counter")
    start_parser.add_argument("operation", choices=VALID_OPERATIONS)
    start_parser.add_argument("--title", help="exact wiki/log.md operation title; prevents concurrent runs from being misattributed")
    start_parser.add_argument("--codex-state", help="override Codex Desktop state SQLite path")
    start_parser.set_defaults(handler=start)

    finish_parser = subparsers.add_parser("finish", help="record the token delta since the matching start snapshot")
    finish_parser.add_argument("operation", choices=VALID_OPERATIONS)
    finish_parser.add_argument("--log", default="wiki/log.md", help="operation log path (default: wiki/log.md)")
    finish_parser.add_argument("--codex-state", help="override Codex Desktop state SQLite path")
    finish_parser.add_argument("--codex-home", help="override Codex home containing sessions/*.jsonl")
    finish_parser.add_argument("--title", help="exact wiki/log.md title; used when recovering a missed start snapshot")
    finish_parser.set_defaults(handler=finish)

    invalidate_parser = subparsers.add_parser("invalidate", help="append a correction that excludes an invalid measured event from reports")
    invalidate_parser.add_argument("event_id", help="event id to exclude")
    invalidate_parser.add_argument("--reason", required=True, help="short explanation of the invalid measurement")
    invalidate_parser.set_defaults(handler=invalidate)

    sync_parser = subparsers.add_parser("sync", help="derive operation events from append-only wiki/log.md")
    sync_parser.add_argument("--log", default="wiki/log.md", help="operation log path (default: wiki/log.md)")
    sync_parser.set_defaults(handler=sync)

    report_parser = subparsers.add_parser("report", help="show an aggregate usage report")
    report_parser.add_argument("--by", choices=("day", "operation", "skill", "model", "run"), default="day")
    report_parser.add_argument("--since", help="inclusive ISO date or timestamp")
    report_parser.add_argument("--until", help="inclusive ISO date or timestamp")
    report_parser.add_argument("--format", choices=("table", "json"), default="table")
    report_parser.add_argument("--log", default="wiki/log.md", help="operation log path to sync first (default: wiki/log.md)")
    report_parser.add_argument("--no-sync", action="store_true", help="do not derive new events from wiki/log.md")
    report_parser.set_defaults(handler=report)

    codex_parser = subparsers.add_parser("codex-report", help="ccusage-style report from Codex session JSONL")
    codex_parser.add_argument("--by", choices=("day", "session", "model"), help="show one section; omit to show model, day, and session")
    codex_parser.add_argument("--since", help="inclusive ISO date or timestamp")
    codex_parser.add_argument("--until", help="inclusive ISO date or timestamp")
    codex_parser.add_argument("--format", choices=("table", "json"), default="table")
    codex_parser.add_argument("--codex-home", help="override Codex home containing sessions/*.jsonl")
    codex_parser.add_argument("--all-workspaces", action="store_true", help="include sessions from other workspaces")
    codex_parser.set_defaults(handler=codex_report)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
