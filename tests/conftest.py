"""Shared pytest configuration."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_wiki_lint_base(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ``$WIKI_LINT_BASE`` out of the tests.

    ``wiki-lint`` falls back to that variable when ``--base`` is absent, so
    the bundle tests would run history checks they never asked for and fail
    on a Git revision that does not exist in their fixture. CI scopes the
    variable to individual steps, but anyone who exports it while debugging a
    CI run locally would otherwise see four unrelated failures.
    """
    monkeypatch.delenv("WIKI_LINT_BASE", raising=False)
