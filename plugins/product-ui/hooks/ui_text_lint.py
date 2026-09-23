"""PostToolUse hook: text-size and filler check on written screen files.

Runs product-ui's check_shippable_text.py with the three checks that hold for any
screen regardless of the skill that produced it:
  ST7   a visible run below the minimum size (14px; 12px for a Latin-only run of at
        most 24 characters), resolved through the stylesheets and the cascade
  ST8   placeholder filler on the screen
  ST10  a font-size declaration below the minimum in a stylesheet
An error returns decision=block so Claude raises the size or deletes the run; a
warning goes to stderr with exit 2 and the write stands. The existence checks
ST1-ST6 and ST9 are not run here: they belong to product-ui Step 4, where the surface
is known.

Never blocks permanently: a per-file counter caps consecutive blocks at 3 and
resets when a write of that file passes.
All failures exit 0 (fail-open); a broken check must not stop file writes.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_BLOCKS_PER_FILE = 3
MAX_REPORTED = 20
CHECKER = Path(__file__).resolve().parent.parent / "skills" / "product-ui" / "scripts" / "check_shippable_text.py"
CHECKS = "ST7,ST8,ST10"
EXTS = {".html", ".htm", ".css", ".scss", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}
# Third-party, generated and fixture files, and this plugin's own directory, are skipped.
SKIP = re.compile(
    r"node_modules|\.min\.|[\\/](?:\.git|fixtures|vendor|dist|build)[\\/]"
    r"|[\\/]skills[\\/]product-ui[\\/]|[\\/]plugins[\\/]product-ui[\\/]"
)


def main():
    data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    path = (data.get("tool_input") or {}).get("file_path")
    if not path or Path(path).suffix.lower() not in EXTS or SKIP.search(path):
        return 0
    if not os.path.isfile(path) or not CHECKER.is_file():
        return 0

    out = subprocess.run(
        [sys.executable, str(CHECKER), path, "--checks", CHECKS, "--json"],
        capture_output=True, timeout=60, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    ).stdout.decode("utf-8", "replace")
    if not out.strip():
        return 0
    findings = json.loads(out).get("findings") or []
    errors = [f for f in findings if f.get("severity") == "ERROR"]
    warnings = [f for f in findings if f.get("severity") == "WARN"]

    sid = data.get("session_id") or "nosid"
    key = hashlib.sha1(path.lower().encode("utf-8")).hexdigest()[:16]
    counter = Path(tempfile.gettempdir()) / f"claude-uilint-{sid}-{key}"
    if not errors:
        try:
            counter.unlink()
        except OSError:
            pass
    if not errors and not warnings:
        return 0

    if errors:
        try:
            count = int(counter.read_text().strip())
        except (OSError, ValueError):
            count = 0
        if count >= MAX_BLOCKS_PER_FILE:
            return 0
        try:
            counter.write_text(str(count + 1))
        except OSError:
            pass

    lines = [f"[ui-text-lint] {path}"]
    if errors:
        lines.append(
            f"check_shippable_text.py reported {len(errors)} error(s). Text below the minimum size "
            "(14px; 12px only for a Latin-only run of 24 characters or fewer) and filler do not ship: "
            "raise the size or delete the run, then write again."
        )
        for f in errors[:MAX_REPORTED]:
            lines.append(f'L{f.get("line")} [{f.get("id")}] {f.get("message")} | "{f.get("text")}" -> {f.get("fix")}')
        if len(errors) > MAX_REPORTED:
            lines.append(f"... and {len(errors) - MAX_REPORTED} more.")
    if warnings:
        lines.append(
            f"{len(warnings)} warning(s): a size between 12px and 14px is allowed only where every run it "
            "reaches is Latin-only and at most 24 characters. Fix the ones that hold, keep the rest with a stated reason."
        )
        for f in warnings[:MAX_REPORTED]:
            lines.append(f'L{f.get("line")} [{f.get("id")}] {f.get("message")}')
        if len(warnings) > MAX_REPORTED:
            lines.append(f"... and {len(warnings) - MAX_REPORTED} more.")

    if not errors:
        sys.stderr.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
        return 2

    lines.append(
        "The rule is product-ui's references/ban-list.md. If a run cannot be raised or deleted, state the "
        "reason and let the user decide."
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": "\n".join(lines)}))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 0
    sys.exit(code)
