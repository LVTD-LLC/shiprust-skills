#!/usr/bin/env python3
"""Install the portable skill without secrets, downloads or config replacement."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DESTINATIONS = {
    "codex": ".agents/skills", "claude": ".claude/skills",
    "cursor": ".cursor/skills", "openclaw": ".openclaw/skills",
    "hermes": ".hermes/skills", "opencode": ".config/opencode/skills",
    "copilot": ".copilot/skills",
}


def install(destination: Path, dry_run=False):
    source = ROOT / "skills" / "shiprust"
    files = [p for p in source.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    # Preflight the entire tree; never leave half an install on a known conflict.
    for file in files:
        target = destination / file.relative_to(source)
        for parent in [target, *target.parents]:
            if parent.is_symlink():
                raise ValueError("Refusing to install through a symlink")
        if target.exists() and (not target.is_file() or target.read_bytes() != file.read_bytes()):
            raise ValueError(f"Existing file differs: {target}. Review/update it manually; nothing overwritten.")
    if not dry_run:
        for file in files:
            target = destination / file.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                # Exclusive creation also protects against a file appearing after preflight.
                with target.open("xb") as out:
                    out.write(file.read_bytes())
    return len(files)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    choice = p.add_mutually_exclusive_group(required=True)
    choice.add_argument("--agent", choices=DESTINATIONS)
    choice.add_argument("--skills-dir", type=Path, help="Custom active profile's skills directory")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    base = args.skills_dir or Path.home() / DESTINATIONS[args.agent]
    destination = base.expanduser().absolute() / "shiprust"
    try:
        count = install(destination, args.dry_run)
    except (ValueError, OSError) as e:
        p.exit(1, f"Install stopped: {e}\n")
    print(f"{'Would install' if args.dry_run else 'Installed'} {count} files at {destination}")
    print("Next: follow references/agents.md to merge your client's MCP config and verify account access.")
    print("No credentials, MCP settings, approvals, or services were changed.")


if __name__ == "__main__":
    main()
