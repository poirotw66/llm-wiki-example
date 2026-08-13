"""Shared helpers for the repository's maintenance scripts.

Scripts in this directory use hyphenated filenames so they read well on the
command line, which makes them unimportable as modules.  Each one therefore
appends ``scripts/`` to ``sys.path`` before importing this module::

    _SCRIPTS = str(Path(__file__).resolve().parent)
    if _SCRIPTS not in sys.path:
        sys.path.append(_SCRIPTS)

    from _common import ROOT, sha256_file

Everything here is either a repository-wide invariant (the wiki log grammar,
the bundle layout) or a primitive that more than one script needs.  Keeping a
single definition matters most for the log grammar: ``wiki-lint`` enforces it
and ``wiki-usage`` parses it for token attribution, so two copies can drift
into a state where a log passes lint but loses its usage attribution.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Reserved bundle files that are not knowledge pages.
SKIP_PAGES = frozenset({"index.md", "log.md"})

#: The five wiki operations, in the order they are documented.
OPERATIONS = ("ingest", "query", "lint", "faq", "graph")

_OPERATION = "|".join(OPERATIONS)

#: ``## 2026-08-05`` — the ISO date heading a day's operations live under.
LOG_DATE = re.compile(r"^## (?P<date>\d{4}-\d{2}-\d{2})$")

#: ``- **ingest** | title`` — one operation entry.
LOG_OPERATION = re.compile(
    rf"^- \*\*(?P<operation>{_OPERATION})\*\* \| (?P<title>.+)$"
)

#: ``## [2026-08-05] ingest | title`` — the retired pre-migration entry form,
#: still recognised so a format-only migration stays semantically append-only.
LOG_BRACKET_OPERATION = re.compile(
    rf"^## \[(?P<date>\d{{4}}-\d{{2}}-\d{{2}})\] (?P<operation>{_OPERATION}) \| (?P<title>.+)$"
)


@dataclass(frozen=True)
class Paths:
    """Bundle layout rooted at ``root``.

    Every location is derived from ``root`` on access rather than captured at
    import time, so pointing a script at another tree is a single assignment
    and a newly added location cannot be left behind pointing at the real
    repository.
    """

    root: Path

    @property
    def wiki(self) -> Path:
        return self.root / "wiki"

    @property
    def wiki_sources(self) -> Path:
        return self.wiki / "sources"

    @property
    def index(self) -> Path:
        return self.wiki / "index.md"

    @property
    def log(self) -> Path:
        return self.wiki / "log.md"

    @property
    def raw(self) -> Path:
        return self.root / "raw"

    @property
    def raw_sources(self) -> Path:
        return self.raw / "sources"

    @property
    def raw_assets(self) -> Path:
        return self.raw / "assets"

    @property
    def raw_originals(self) -> Path:
        return self.raw / "originals"

    @property
    def raw_inbox(self) -> Path:
        return self.raw / "inbox"

    @property
    def ops(self) -> Path:
        return self.root / "ops"

    @property
    def purpose(self) -> Path:
        return self.ops / "purpose.md"

    def relative(self, path: Path) -> str:
        """Render ``path`` for human-readable output, relative to the root."""
        return str(path.relative_to(self.root))

    def display(self, path: Path) -> str:
        """Like :meth:`relative`, but falls back to the absolute path.

        Used for paths a caller may point anywhere, such as an output file.
        """
        try:
            return self.relative(path)
        except ValueError:
            return str(path)

    def wiki_pages(self) -> list[Path]:
        """Knowledge pages in the bundle, excluding the reserved files."""
        if not self.wiki.is_dir():
            return []
        return sorted(
            path for path in self.wiki.rglob("*.md") if path.name not in SKIP_PAGES
        )


def sha256_file(path: Path) -> str:
    """Digest a file in chunks so large archives do not land in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, content: str) -> None:
    """Replace ``path`` with ``content`` atomically, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def git(*args: str, cwd: Path | None = None) -> str:
    """Run git and return stdout; raises ``CalledProcessError`` on failure."""
    return subprocess.check_output(
        ["git", *args], cwd=cwd or ROOT, text=True, stderr=subprocess.DEVNULL
    )


def git_output(*args: str, cwd: Path | None = None) -> str | None:
    """Run git and return stdout, or ``None`` when git fails or is missing."""
    try:
        return git(*args, cwd=cwd)
    except (OSError, subprocess.CalledProcessError):
        return None
