#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
project-wiki lint: knowledge link audit via Obsidian CLI

Audits vault health by checking for broken wikilinks, orphan notes,
missing index entries, and missing knowledge metadata. Outputs structured
reports compatible with the project-knowledge-curator's link_health format.

Usage:
    python3 lint.py [--domain <域>] [--json] [--fix]

Requires: Obsidian app running + CLI registered (Settings → General → CLI)
"""

import subprocess
import json
import re
import sys
import argparse
from pathlib import Path


# ============ Obsidian CLI Layer (shared with search.py) ============

def obsidian(cmd: str, *args) -> str:
    """Call Obsidian CLI. Fail loudly if unavailable."""
    try:
        result = subprocess.run(
            ["obsidian", cmd, *args],
            capture_output=True, text=True, timeout=30
        )
    except FileNotFoundError:
        print(
            "ERROR: 'obsidian' command not found.\n"
            "  Obsidian CLI must be registered: Settings → General → CLI\n"
            "  See: https://obsidian.md/cli",
            file=sys.stderr
        )
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"ERROR: obsidian {cmd} timed out (30s)", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(
            f"ERROR: obsidian {cmd} failed (exit {result.returncode}).\n"
            f"  Is Obsidian running?\n"
            f"  stderr: {result.stderr.strip()}",
            file=sys.stderr
        )
        sys.exit(1)

    return result.stdout


def obsidian_safe(cmd: str, *args) -> str:
    """Call Obsidian CLI, returning empty string on failure instead of exiting."""
    try:
        result = subprocess.run(
            ["obsidian", cmd, *args],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return ""
        return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


# ============ Frontmatter Parsing ============

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content using regex only."""
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        kv = line.split(':', 1)
        if len(kv) == 2:
            key = kv[0].strip()
            val = kv[1].strip().strip('"').strip("'")
            if val:
                fm[key] = val
    return fm


# ============ Audit Checks ============

def check_broken_links(domain=None):
    """Check for unresolved wikilinks (broken links)."""
    findings = []
    raw = obsidian_safe("unresolved", "--format", "json")
    if not raw:
        return findings

    try:
        unresolved = json.loads(raw)
    except json.JSONDecodeError:
        return findings

    for item in unresolved:
        source = item.get("source", "") if isinstance(item, dict) else str(item)
        if domain and not source.startswith(domain + "/"):
            continue
        target = item.get("target", "") if isinstance(item, dict) else ""
        findings.append({
            "type": "missing_wikilink",
            "source": source,
            "target": target,
            "severity": "P1"
        })

    return findings


def check_orphan_notes(domain=None):
    """Check for notes with no incoming links."""
    findings = []
    raw = obsidian_safe("files", "--format", "json")
    if not raw:
        return findings

    try:
        all_files = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: line-based
        all_files = [f.strip() for f in raw.strip().split('\n') if f.strip()]

    for f in all_files:
        filepath = f if isinstance(f, str) else f.get("path", str(f))

        # Skip non-domain files
        if domain and not filepath.startswith(domain + "/"):
            continue

        # Skip infrastructure files
        if any(filepath.startswith(p) for p in ["_sources/", "_schema/", "."]):
            continue

        # Skip index files
        basename = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
        if basename in ["README.md", "index.md", "log.md"]:
            continue

        # Check backlinks
        bl_raw = obsidian_safe("backlinks", filepath, "--format", "json")
        has_backlinks = False
        if bl_raw:
            try:
                bl = json.loads(bl_raw)
                has_backlinks = bool(bl)
            except json.JSONDecodeError:
                has_backlinks = bool(bl_raw.strip())

        if not has_backlinks:
            findings.append({
                "type": "orphan_note",
                "path": filepath,
                "severity": "P2"
            })

    return findings


def check_missing_index(domain):
    """Check for domain files not referenced in the domain's README.md."""
    findings = []
    if not domain:
        return findings

    readme_content = obsidian_safe("read", f"{domain}/README.md")
    if not readme_content:
        findings.append({
            "type": "missing_readme",
            "path": f"{domain}/README.md",
            "severity": "P0"
        })
        return findings

    raw = obsidian_safe("files", "--format", "json")
    if not raw:
        return findings

    try:
        all_files = json.loads(raw)
    except json.JSONDecodeError:
        all_files = [f.strip() for f in raw.strip().split('\n') if f.strip()]

    for f in all_files:
        filepath = f if isinstance(f, str) else f.get("path", str(f))

        if not filepath.startswith(domain + "/"):
            continue

        # Skip subdirectory indexes and non-.md files
        basename = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
        if not basename.endswith(".md"):
            continue
        name_no_ext = basename.replace(".md", "")
        if name_no_ext == "README":
            continue

        # Check if referenced in README (as wikilink or markdown link)
        if (f"[[{name_no_ext}]]" not in readme_content and
                f"[[{name_no_ext}|" not in readme_content and
                f"]({basename})" not in readme_content and
                f"]({filepath})" not in readme_content):
            findings.append({
                "type": "missing_index",
                "path": filepath,
                "expected_in": f"{domain}/README.md",
                "severity": "P1"
            })

    return findings


def check_missing_metadata(domain=None):
    """Check for wiki pages missing knowledge governance metadata."""
    findings = []
    raw = obsidian_safe("files", "--format", "json")
    if not raw:
        return findings

    try:
        all_files = json.loads(raw)
    except json.JSONDecodeError:
        all_files = [f.strip() for f in raw.strip().split('\n') if f.strip()]

    required_fields = ["knowledge_kind", "knowledge_color", "authority_level"]

    for f in all_files:
        filepath = f if isinstance(f, str) else f.get("path", str(f))

        if domain and not filepath.startswith(domain + "/"):
            continue

        # Skip infrastructure and index files
        if any(filepath.startswith(p) for p in ["_sources/", "_schema/", "."]):
            continue
        basename = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
        if basename in ["README.md", "index.md", "log.md"]:
            continue
        if not basename.endswith(".md"):
            continue

        content = obsidian_safe("read", filepath)
        if not content:
            continue

        fm = parse_frontmatter(content)
        missing = [k for k in required_fields if k not in fm]

        if missing:
            findings.append({
                "type": "missing_metadata",
                "path": filepath,
                "missing_fields": missing,
                "severity": "P2"
            })

    return findings


# ============ Report Generation ============

def generate_report(findings, domain=None):
    """Generate structured report matching Curator link_health format."""
    health = "ok" if not findings else "issues_found"

    # Collect unique repair targets
    repair_targets = list(set(
        f.get("expected_in") or f.get("source") or f.get("path")
        for f in findings
        if f.get("expected_in") or f.get("source") or f.get("path")
    ))

    # Count by severity
    by_severity = {}
    for f in findings:
        sev = f.get("severity", "P2")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return {
        "link_health": health,
        "domain": domain or "all",
        "total_issues": len(findings),
        "by_severity": by_severity,
        "findings": findings,
        "repair_targets": repair_targets
    }


def print_human_report(report):
    """Print human-readable report."""
    domain = report["domain"]
    total = report["total_issues"]

    print(f"=== Wiki Health Report ({domain}) ===")
    print()

    if total == 0:
        print("  All checks passed. No issues found.")
        return

    print(f"  Total issues: {total}")
    for sev, count in sorted(report["by_severity"].items()):
        print(f"  {sev}: {count}")
    print()

    # Group by type
    by_type = {}
    for f in report["findings"]:
        by_type.setdefault(f["type"], []).append(f)

    for t, items in by_type.items():
        print(f"{t} ({len(items)}):")
        for item in items:
            path = item.get("path") or item.get("source") or "?"
            detail = ""
            if item.get("target"):
                detail = f" → [[{item['target']}]]"
            elif item.get("expected_in"):
                detail = f" (not in {item['expected_in']})"
            elif item.get("missing_fields"):
                detail = f" (missing: {', '.join(item['missing_fields'])})"
            print(f"  [{item.get('severity', '?')}] {path}{detail}")
        print()

    if report["repair_targets"]:
        print("Repair targets:")
        for t in report["repair_targets"]:
            print(f"  → {t}")


# ============ CLI Entry Point ============

def main():
    parser = argparse.ArgumentParser(
        description="project-wiki lint: knowledge link audit via Obsidian CLI"
    )
    parser.add_argument(
        "--domain", "-d",
        help="Audit specific business domain (directory prefix)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON (compatible with Curator link_health)"
    )
    parser.add_argument(
        "--check", nargs="*",
        choices=["links", "orphans", "index", "metadata"],
        help="Run specific checks only (default: all)"
    )

    args = parser.parse_args()

    checks_to_run = args.check or ["links", "orphans", "index", "metadata"]
    all_findings = []

    if "links" in checks_to_run:
        all_findings.extend(check_broken_links(args.domain))

    if "orphans" in checks_to_run:
        all_findings.extend(check_orphan_notes(args.domain))

    if "index" in checks_to_run:
        all_findings.extend(check_missing_index(args.domain))

    if "metadata" in checks_to_run:
        all_findings.extend(check_missing_metadata(args.domain))

    report = generate_report(all_findings, args.domain)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human_report(report)

    # Exit code: 0 if healthy, 1 if issues found
    sys.exit(0 if report["link_health"] == "ok" else 1)


if __name__ == "__main__":
    main()
