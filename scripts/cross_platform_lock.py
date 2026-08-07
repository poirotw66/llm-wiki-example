"""Portable inter-process lock using atomic creation, without platform-specific APIs."""
from __future__ import annotations

import os
import time
from pathlib import Path


class ExclusiveFileLock:
    def __init__(self, target: Path, *, timeout: float = 10.0, stale_after: float = 120.0) -> None:
        self.path = target.with_suffix(target.suffix + ".lock")
        self.timeout, self.stale_after, self.acquired = timeout, stale_after, False

    def __enter__(self) -> "ExclusiveFileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(f"pid={os.getpid()} acquired_at={time.time()}\n")
                self.acquired = True
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > self.stale_after:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out waiting for lock: {self.path}")
                time.sleep(0.02)

    def __exit__(self, *_: object) -> None:
        if self.acquired:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            self.acquired = False
