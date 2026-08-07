from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path

import pytest


def _load():
    path = Path(__file__).resolve().parents[1] / "scripts/cross_platform_lock.py"
    spec = importlib.util.spec_from_file_location("cross_platform_lock", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exclusive_lock_blocks_then_releases(tmp_path: Path) -> None:
    module = _load()
    target = tmp_path / "state.json"
    with module.ExclusiveFileLock(target):
        with pytest.raises(TimeoutError):
            with module.ExclusiveFileLock(target, timeout=0.03):
                pass
    with module.ExclusiveFileLock(target, timeout=0.03):
        pass


def test_stale_lock_is_recovered(tmp_path: Path) -> None:
    module = _load()
    target = tmp_path / "state.json"
    lock = target.with_suffix(".json.lock")
    lock.write_text("stale", encoding="utf-8")
    os.utime(lock, (time.time() - 10, time.time() - 10))
    with module.ExclusiveFileLock(target, stale_after=0.01):
        assert lock.exists()
    assert not lock.exists()
