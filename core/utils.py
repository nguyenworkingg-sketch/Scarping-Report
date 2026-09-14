from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path


def get_report_root() -> Path:
    return Path(os.getenv("REPORT_ROOT", r"E:\Báo cáo"))


def ensure_directories():
    root = get_report_root()
    for name in ("raw", "extracted", "metadata"):
        (root / name).mkdir(parents=True, exist_ok=True)
    Path("auth").mkdir(exist_ok=True)
    return root


def safe_name(value: str, max_len: int = 140) -> str:
    value = re.sub(r"[^\w\-\.]+", "_", value.strip(), flags=re.UNICODE)
    value = re.sub(r"_+", "_", value).strip("_.")
    return value[:max_len] or "report"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def report_paths(source: str, title: str):
    root = ensure_directories()
    today = datetime.now().strftime("%Y-%m-%d")
    stem = safe_name(f"{today}_{source}_{title}")

    raw = root / "raw" / source / f"{stem}.pdf"
    meta = root / "metadata" / source / f"{stem}.json"
    text = root / "extracted" / source / f"{stem}.txt"

    for p in (raw.parent, meta.parent, text.parent):
        p.mkdir(parents=True, exist_ok=True)

    return raw, meta, text


def save_metadata(path: Path, payload: dict):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def already_downloaded(source: str, source_url: str) -> bool:
    root = ensure_directories()
    folder = root / "metadata" / source
    if not folder.exists():
        return False

    for fp in folder.glob("*.json"):
        try:
            obj = json.loads(fp.read_text(encoding="utf-8"))
            if obj.get("source_url") == source_url:
                return True
        except Exception:
            pass
    return False


def cleanup_old_files(retention_days: int | None = None) -> int:
    """Delete all report files older than retention_days based on filesystem mtime."""
    root = ensure_directories()
    retention_days = retention_days or int(os.getenv("RETENTION_DAYS", "30"))
    cutoff = time.time() - retention_days * 86400
    removed = 0

    for bucket in ("raw", "extracted", "metadata"):
        base = root / bucket
        if not base.exists():
            continue

        for fp in base.rglob("*"):
            if fp.is_file():
                try:
                    if fp.stat().st_mtime < cutoff:
                        fp.unlink()
                        removed += 1
                except FileNotFoundError:
                    pass

        for directory in sorted((p for p in base.rglob("*") if p.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass

    print(f"[CLEANUP] Removed {removed} file(s) older than {retention_days} days")
    return removed
