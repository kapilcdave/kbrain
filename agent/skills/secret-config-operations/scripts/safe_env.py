#!/usr/bin/env python3
"""Value-blind inspection and key renaming for dotenv-style secret files."""
from __future__ import annotations

import argparse
import os
import re
import stat
import tempfile
from pathlib import Path

LINE = re.compile(r"^(?P<prefix>\s*(?:export\s+)?)(?P<key>[A-Za-z_][A-Za-z0-9_]*)(?P<sep>\s*=)(?P<value>.*)$")


def inspect(path: Path) -> int:
    mode = stat.S_IMODE(path.stat().st_mode)
    print(f"file={path}")
    print(f"owner_uid={path.stat().st_uid}")
    print(f"permissions={mode:03o}")
    malformed: list[int] = []
    for number, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = LINE.match(raw)
        if not match:
            malformed.append(number)
            continue
        value = match.group("value").strip().strip("\"'")
        print(f"{match.group('key')}: {'set' if value else 'EMPTY'} ({len(value)} chars)")
    print("malformed_lines=" + (",".join(map(str, malformed)) if malformed else "none"))
    return 0


def rename(path: Path, old: str, new: str) -> int:
    if not old.isidentifier() or not new.isidentifier():
        raise SystemExit("key names must be identifiers")
    lines = path.read_text().splitlines(keepends=True)
    old_hits = 0
    new_hits = 0
    output: list[str] = []
    for raw in lines:
        body = raw[:-1] if raw.endswith("\n") else raw
        newline = "\n" if raw.endswith("\n") else ""
        match = LINE.match(body)
        if match and match.group("key") == new:
            new_hits += 1
        if match and match.group("key") == old:
            old_hits += 1
            body = match.group("prefix") + new + match.group("sep") + match.group("value")
        output.append(body + newline)
    if old_hits != 1:
        raise SystemExit(f"expected exactly one {old} key; found {old_hits}")
    if new_hits:
        raise SystemExit(f"refusing duplicate destination key {new}")

    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.writelines(output)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f"renamed {old} -> {new}; permissions=600; values_not_printed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("inspect")
    show.add_argument("path", type=Path)
    move = sub.add_parser("rename")
    move.add_argument("path", type=Path)
    move.add_argument("old_key")
    move.add_argument("new_key")
    args = parser.parse_args()
    if args.command == "inspect":
        return inspect(args.path)
    return rename(args.path, args.old_key, args.new_key)


if __name__ == "__main__":
    raise SystemExit(main())
