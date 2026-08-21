#!/usr/bin/env python3
"""Validate and report on the AptoMDM stubs register.

The register lives in ``AptoMDM_Docs/AptoMDM_Stubs_Tracker.md``. This script exists
so that "we track our stubs" is a checkable claim rather than an intention.

Usage
-----
    python tools/stubs.py                    # summary report (default)
    python tools/stubs.py --check            # validate; exit 1 on any error
    python tools/stubs.py --list             # full open register, one line per stub
    python tools/stubs.py --open --sev S1    # filters compose
    python tools/stubs.py --module 4.6       # stubs resolving in a given module
    python tools/stubs.py --phase 4          # stubs resolving anywhere in a phase

The check worth running before every commit that closes a module is ``--check``:
besides schema validation it cross-references Bible Section 7, so a stub whose
resolving module is already marked Complete is reported as a missed close. That is
the single most common way a register like this rots.

Standard library only. Nothing here writes or deletes a file.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import (  # noqa: E402
    docs_dir,
    is_table_divider,
    parse_table_row,
    repo_root,
)

TRACKER = "AptoMDM_Stubs_Tracker.md"
ROADMAP = "AptoMDM_Design_Roadmap.md"
BIBLE = "Apto_MDM_Bible_v1.2.md"

TYPES = ("FWD", "DEF", CFG := "CFG", "DEC", "EXT", "DOC")
SEVERITIES = ("S1", "S2", "S3")
STATUSES = ("Open", "In design", "Closed", "Superseded")

#: Closing conditions that do not actually close anything.
VAGUE = re.compile(
    r"^\s*(later|tbd|t\.b\.d\.?|eventually|someday|some day|soon|at some point|"
    r"when possible|when needed|as needed|to be decided|to be determined|n/?a|\?+|-+|—+)\s*\.?\s*$",
    re.I,
)

NO_MODULE = {"", "-", "--", "—", "n/a", "na", "none"}
ID_RE = re.compile(r"^STUB-(\d{3,})$")
PLACEHOLDER = re.compile(r"_?\(none yet\)_?", re.I)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass
class Stub:
    sid: str
    type_: str
    sev: str
    text: str
    introduced_by: str
    blocks: str
    closing_condition: str
    resolves_in: str
    status: str
    line_no: int
    closed: bool = False
    closed_by: str = ""
    closed_date: str = ""

    @property
    def num(self) -> int:
        m = ID_RE.match(self.sid)
        return int(m.group(1)) if m else -1

    @property
    def phase(self) -> int | None:
        if self.resolves_in.lower() in NO_MODULE:
            return None
        m = re.match(r"^(\d{1,2})\.", self.resolves_in)
        return int(m.group(1)) if m else None

    def one_line(self) -> str:
        target = self.resolves_in if self.resolves_in.lower() not in NO_MODULE else "—"
        return (
            f"  {self.sid}  {self.sev}  {self.type_:<3}  {self.status:<10} "
            f"→ {target:<5}  {_truncate(self.text, 96)}"
        )


@dataclass
class Findings:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def _truncate(s: str, n: int) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _iter_uncoded_lines(text: str):
    """Yield (line_no, line) skipping fenced code blocks.

    The tracker embeds a Stub Summary *template* in a fenced block; parsing it as
    real rows would invent a STUB-0NN that does not exist.
    """
    in_fence = False
    for i, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield i, line


def _find_table(lines: list[tuple[int, str]], required: set[str]) -> list[tuple[int, list[str]]]:
    """Return rows of the first table whose header contains every name in *required*."""
    for idx, (_, line) in enumerate(lines):
        cells = parse_table_row(line)
        if not cells:
            continue
        header = {c.strip().lower() for c in cells}
        if not required <= header:
            continue
        if idx + 1 >= len(lines) or not is_table_divider(lines[idx + 1][1]):
            continue
        names = [c.strip().lower() for c in cells]
        out: list[tuple[int, list[str]]] = []
        for line_no, raw in lines[idx + 2 :]:
            row = parse_table_row(raw)
            if row is None:
                break
            if len(row) != len(names):
                continue
            out.append((line_no, row))
        return out
    return []


def parse_register(text: str) -> tuple[list[Stub], list[Stub]]:
    lines = list(_iter_uncoded_lines(text))

    open_rows = _find_table(
        lines, {"id", "type", "sev", "stub", "closing condition", "resolves in", "status"}
    )
    closed_rows = _find_table(lines, {"id", "type", "stub", "closed by", "date"})

    open_stubs: list[Stub] = []
    for line_no, r in open_rows:
        if PLACEHOLDER.search(r[0]) or not r[0].strip():
            continue
        open_stubs.append(
            Stub(
                sid=r[0].strip(),
                type_=r[1].strip().upper(),
                sev=r[2].strip().upper(),
                text=r[3].strip(),
                introduced_by=r[4].strip(),
                blocks=r[5].strip(),
                closing_condition=r[6].strip(),
                resolves_in=r[7].strip(),
                status=r[8].strip(),
                line_no=line_no,
            )
        )

    closed_stubs: list[Stub] = []
    for line_no, r in closed_rows:
        if PLACEHOLDER.search(r[0]) or not r[0].strip():
            continue
        closed_stubs.append(
            Stub(
                sid=r[0].strip(),
                type_=r[1].strip().upper(),
                sev="",
                text=r[2].strip(),
                introduced_by="",
                blocks="",
                closing_condition="",
                resolves_in="",
                status="Closed",
                line_no=line_no,
                closed=True,
                closed_by=r[3].strip(),
                closed_date=r[4].strip(),
            )
        )
    return open_stubs, closed_stubs


def roadmap_modules(root: Path) -> dict[str, str]:
    text = (docs_dir(root) / ROADMAP).read_text(encoding="utf-8")
    return {
        f"{a}.{b}": c.strip("* ").strip()
        for a, b, c in re.findall(r"^###\s+\*{0,2}(\d+)\.(\d+)\*{0,2}\s+(.+?)\s*$", text, re.M)
    }


def bible_complete_modules(root: Path) -> set[str]:
    """Module numbers Bible Section 7 marks complete."""
    text = (docs_dir(root) / BIBLE).read_text(encoding="utf-8")
    if "## 7." not in text:
        return set()
    section = text.split("## 7.")[1].split("## 8.")[0]
    done = set()
    for line in section.splitlines():
        m = re.match(r"\s*\|\s*(\d{1,2}\.\d{1,2})\s*\|[^|]*\|\s*([^|]*)\|", line)
        if m and "✅" in m.group(2):
            done.add(m.group(1))
    return done


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate(open_stubs, closed_stubs, modules, complete) -> Findings:
    f = Findings()
    seen: dict[str, int] = {}

    for s in open_stubs + closed_stubs:
        if not ID_RE.match(s.sid):
            f.error(f"L{s.line_no} {s.sid!r}: ID must look like STUB-001")
        if s.sid in seen:
            f.error(f"L{s.line_no} {s.sid}: duplicate ID (also at L{seen[s.sid]}) — IDs are never reused")
        seen[s.sid] = s.line_no
        if s.type_ not in TYPES:
            f.error(f"L{s.line_no} {s.sid}: type {s.type_!r} not one of {', '.join(TYPES)}")

    for s in open_stubs:
        if s.sev not in SEVERITIES:
            f.error(f"L{s.line_no} {s.sid}: severity {s.sev!r} not one of {', '.join(SEVERITIES)}")
        if s.status not in STATUSES:
            f.error(f"L{s.line_no} {s.sid}: status {s.status!r} not one of {', '.join(STATUSES)}")
        if s.status == "Closed":
            f.error(f"L{s.line_no} {s.sid}: marked Closed but still in the open register — move it to the closed table")
        if not s.text:
            f.error(f"L{s.line_no} {s.sid}: empty stub description")
        if not s.closing_condition or VAGUE.match(s.closing_condition):
            f.error(
                f"L{s.line_no} {s.sid}: closing condition {s.closing_condition!r} is not a "
                f"checkable event — a stub without one is indistinguishable from an oversight"
            )
        if not s.introduced_by:
            f.warn(f"L{s.line_no} {s.sid}: no source recorded in 'Introduced by'")

        target = s.resolves_in
        if target.lower() in NO_MODULE:
            if s.type_ != "DOC":
                f.warn(f"L{s.line_no} {s.sid}: no resolving module, but type is {s.type_} not DOC")
        elif target not in modules:
            f.error(f"L{s.line_no} {s.sid}: resolves in {target!r}, which is not one of the {len(modules)} roadmap modules")
        elif target in complete and s.status != "Closed":
            f.error(
                f"L{s.line_no} {s.sid}: MISSED CLOSE — resolving module {target} is already "
                f"✅ Complete in Bible §7, but this stub is still {s.status}"
            )

    for s in closed_stubs:
        if not s.closed_by:
            f.error(f"L{s.line_no} {s.sid}: closed with no 'Closed by' recorded")
        if not s.closed_date:
            f.warn(f"L{s.line_no} {s.sid}: closed with no date")

    nums = sorted(s.num for s in open_stubs + closed_stubs if s.num > 0)
    if nums:
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            f.warn(
                "gap in ID sequence: "
                + ", ".join(f"STUB-{n:03d}" for n in missing[:10])
                + (" …" if len(missing) > 10 else "")
                + " (fine if those were retired; suspicious otherwise)"
            )
    return f


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def tally(items, key):
    counts: dict[str, int] = {}
    for it in items:
        counts[key(it)] = counts.get(key(it), 0) + 1
    return counts


def report(open_stubs, closed_stubs, modules, complete) -> None:
    print(f"AptoMDM stubs register — {len(open_stubs)} open, {len(closed_stubs)} closed\n")

    by_sev = tally(open_stubs, lambda s: s.sev)
    print("By severity")
    for sev in SEVERITIES:
        label = {"S1": "launch-blocking", "S2": "phase-blocking", "S3": "carry"}[sev]
        print(f"  {sev} {label:<16} {by_sev.get(sev, 0):>3}")

    print("\nBy type")
    for t in TYPES:
        n = tally(open_stubs, lambda s: s.type_).get(t, 0)
        if n:
            print(f"  {t}  {n:>3}")

    print("\nBy status")
    for st in STATUSES:
        n = tally(open_stubs, lambda s: s.status).get(st, 0)
        if n:
            print(f"  {st:<12} {n:>3}")

    s1 = [s for s in open_stubs if s.sev == "S1"]
    if s1:
        print(f"\nS1 — launch-blocking, must close before first production tenant ({len(s1)})")
        for s in s1:
            print(s.one_line())

    per_phase: dict[int, int] = {}
    for s in open_stubs:
        if s.phase:
            per_phase[s.phase] = per_phase.get(s.phase, 0) + 1
    if per_phase:
        print("\nOpen stubs awaiting a phase")
        for ph in sorted(per_phase):
            bar = "█" * per_phase[ph]
            print(f"  Phase {ph:>2}  {per_phase[ph]:>2}  {bar}")

    unowned = [s for s in open_stubs if s.resolves_in.lower() in NO_MODULE]
    if unowned:
        print(f"\nNo resolving module — doc-set items needing a decision ({len(unowned)})")
        for s in unowned:
            print(s.one_line())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Validate and report on the AptoMDM stubs register.")
    p.add_argument("--check", action="store_true", help="validate only; exit 1 on any error")
    p.add_argument("--list", action="store_true", help="list stubs one per line")
    p.add_argument("--open", action="store_true", help="restrict to status Open")
    p.add_argument("--sev", choices=SEVERITIES, help="filter by severity")
    p.add_argument("--type", dest="type_", choices=TYPES, help="filter by type")
    p.add_argument("--module", help="stubs resolving in this module, e.g. 4.6")
    p.add_argument("--phase", type=int, help="stubs resolving anywhere in this phase")
    args = p.parse_args(argv)

    root = repo_root()
    tracker = docs_dir(root) / TRACKER
    if not tracker.is_file():
        print(f"error: {tracker} not found", file=sys.stderr)
        return 2

    open_stubs, closed_stubs = parse_register(tracker.read_text(encoding="utf-8"))
    modules = roadmap_modules(root)
    complete = bible_complete_modules(root)

    findings = validate(open_stubs, closed_stubs, modules, complete)

    if args.check:
        for w in findings.warnings:
            print(f"  warn   {w}")
        for e in findings.errors:
            print(f"  ERROR  {e}")
        n_open = len(open_stubs)
        if findings.ok:
            print(
                f"\nOK — {n_open} open stubs validate against {len(modules)} roadmap modules"
                f"{f', {len(findings.warnings)} warning(s)' if findings.warnings else ''}."
            )
            return 0
        print(f"\nFAILED — {len(findings.errors)} error(s), {len(findings.warnings)} warning(s).")
        return 1

    selected = list(open_stubs)
    if args.open:
        selected = [s for s in selected if s.status == "Open"]
    if args.sev:
        selected = [s for s in selected if s.sev == args.sev]
    if args.type_:
        selected = [s for s in selected if s.type_ == args.type_]
    if args.module:
        selected = [s for s in selected if s.resolves_in == args.module]
    if args.phase:
        selected = [s for s in selected if s.phase == args.phase]

    filtered = args.list or args.open or args.sev or args.type_ or args.module or args.phase
    if filtered:
        print(f"{len(selected)} stub(s)")
        for s in selected:
            print(s.one_line())
    else:
        report(open_stubs, closed_stubs, modules, complete)

    if findings.errors:
        print(f"\n{len(findings.errors)} validation error(s) — run --check for detail.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
