#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
project-wiki search: Obsidian CLI wrapper + knowledge metadata enrichment

Wraps the official Obsidian CLI (obsidian search/read/backlinks) and adds
knowledge governance metadata (knowledge_kind, knowledge_color, authority_level)
from YAML frontmatter. Outputs structured results compatible with the
project-knowledge-curator's Knowledge Pack template.

Usage:
    python3 search.py search "query" [--domain <域>] [-n 5]
    python3 search.py hit-detect "query"
    python3 search.py knowledge-pack "query" --domain <域> --feature-point <fp>
    python3 search.py read "file.md"
    python3 search.py backlinks "file.md"

Requires: Obsidian app running + CLI registered (Settings → General → CLI)
"""

import subprocess
import json
import re
import sys
import argparse
from pathlib import Path


# ============ Obsidian CLI Layer ============

def obsidian(cmd: str, *args) -> str:
    """Call Obsidian CLI. Fail loudly if unavailable."""
    try:
        result = subprocess.run(
            ["obsidian", cmd, *args],
            capture_output=True, text=True, timeout=15
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
        print(f"ERROR: obsidian {cmd} timed out (15s)", file=sys.stderr)
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


# ============ Frontmatter Parsing (pure stdlib) ============

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


def extract_feature_points(content: str) -> list:
    """Extract [[wikilink]] targets from content."""
    return re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)


def domain_from_path(filepath: str) -> str:
    """Infer business domain from file path (first directory segment)."""
    parts = filepath.split('/')
    if len(parts) > 1 and not parts[0].startswith('_'):
        return parts[0]
    return ""


# ============ Result Enrichment ============

def enrich_result(result: dict) -> dict:
    """Read file frontmatter and attach knowledge governance metadata."""
    filename = result.get("filename", "")
    try:
        content = obsidian("read", filename)
    except SystemExit:
        content = ""

    fm = parse_frontmatter(content)
    result["knowledge_kind"] = fm.get("knowledge_kind")        # prd / constraint / architecture
    result["knowledge_color"] = fm.get("knowledge_color")       # white / gray / black
    result["authority_level"] = fm.get("authority_level")        # A.authoritative / B / C / D
    result["business_domain"] = domain_from_path(filename)
    result["feature_points"] = extract_feature_points(content)
    return result


def authority_sort_key(result: dict) -> int:
    """Sort key: A=0, B=1, C=2, D=3, unknown=4"""
    level = result.get("authority_level") or ""
    for i, prefix in enumerate(["A", "B", "C", "D"]):
        if level.startswith(prefix):
            return i
    return 4


# ============ Commands ============

def cmd_search(args):
    """Search vault + enrich with knowledge metadata."""
    query = args.query
    if args.domain:
        query = f"path:{args.domain} {query}"

    raw = obsidian("search", query, "--format", "json")
    try:
        results = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try line-based parsing
        results = [{"filename": line.strip()} for line in raw.strip().split('\n') if line.strip()]

    enriched = [enrich_result(r) for r in results[:args.n]]
    enriched.sort(key=authority_sort_key)

    if args.json:
        print(json.dumps(enriched, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(enriched, 1):
            color = r.get("knowledge_color") or "?"
            auth = r.get("authority_level") or "?"
            kind = r.get("knowledge_kind") or "?"
            domain = r.get("business_domain") or "?"
            score = r.get("score", "")
            print(f"{i}. [{color}/{auth}] {r['filename']}")
            print(f"   domain={domain}  kind={kind}  score={score}")
            fps = r.get("feature_points", [])
            if fps:
                print(f"   features: {', '.join(fps[:5])}")
            print()


def cmd_hit_detect(args):
    """knowledge-hit-detect: determine if current task hits existing knowledge."""
    query = args.query
    raw = obsidian("search", query, "--format", "json")
    try:
        results = json.loads(raw)
    except json.JSONDecodeError:
        results = []

    if not results:
        output = {"status": "no_hit"}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    enriched = [enrich_result(r) for r in results[:3]]

    has_writeback = any(
        r.get("knowledge_color") == "gray" or
        (r.get("authority_level") or "").startswith("D")
        for r in enriched
    )

    all_features = list(set(
        fp for r in enriched for fp in r.get("feature_points", [])
    ))

    output = {
        "status": "hit_writeback_required" if has_writeback else "hit_readonly",
        "matched_domain": enriched[0].get("business_domain"),
        "matched_features": all_features[:10],
        "matched_files": [r["filename"] for r in enriched],
        "writeback_reason": (
            "gray knowledge needs confirmation or stale knowledge found"
            if has_writeback else None
        )
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_knowledge_pack(args):
    """Generate Knowledge Pack matching Curator template format."""
    query = args.query
    if args.domain:
        query = f"path:{args.domain} {query}"

    raw = obsidian("search", query, "--format", "json")
    try:
        results = json.loads(raw)
    except json.JSONDecodeError:
        results = []

    enriched = [enrich_result(r) for r in results[:10]]

    # Classify by knowledge_color
    baseline = [r for r in enriched if r.get("knowledge_color") == "white"]
    advisory = [r for r in enriched if r.get("knowledge_color") == "gray"]
    blocked = [r for r in enriched if r.get("knowledge_color") == "black"]
    authoritative = [r for r in enriched if (r.get("authority_level") or "").startswith("A")]

    def fmt(r):
        return (
            f"- path: {r['filename']}\n"
            f"  knowledge_kind: {r.get('knowledge_kind') or 'unknown'}\n"
            f"  knowledge_color: {r.get('knowledge_color') or 'unknown'}\n"
            f"  authority_level: {r.get('authority_level') or 'unknown'}\n"
            f"  business_domain: {r.get('business_domain') or 'unknown'}\n"
            f"  feature_point: {args.feature_point}"
        )

    none = "- (none found)"

    pack = f"""## Knowledge Pack

### 业务域
- {args.domain}

### 功能点
- [[{args.feature_point}]]

### authoritative sources
{chr(10).join(fmt(r) for r in authoritative) or none}

### baseline sources
{chr(10).join(fmt(r) for r in baseline) or none}

### advisory sources
{chr(10).join(fmt(r) for r in advisory) or '- (none)'}

### blocked sources
{chr(10).join(fmt(r) for r in blocked) or '- (none)'}

### locked facts
- (to be filled by Curator)

### open conflicts
- (to be filled by Curator)

### stale sources to ignore
- (to be filled by Curator)

### writeback targets
- {args.domain}/README.md
- {args.domain}/knowledge/README.md
- [[{args.feature_point}]]
"""
    print(pack)


def cmd_read(args):
    """Read a file via Obsidian CLI, with parsed frontmatter metadata."""
    content = obsidian("read", args.file)
    fm = parse_frontmatter(content)

    if args.meta_only:
        fm["business_domain"] = domain_from_path(args.file)
        fm["feature_points"] = extract_feature_points(content)
        print(json.dumps(fm, ensure_ascii=False, indent=2))
    else:
        print(content)


def cmd_backlinks(args):
    """List backlinks to a file via Obsidian CLI."""
    raw = obsidian("backlinks", args.file, "--format", "json")
    try:
        results = json.loads(raw)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            if not results:
                print(f"No backlinks found for: {args.file}")
            else:
                print(f"Backlinks to {args.file}:")
                for r in results:
                    name = r if isinstance(r, str) else r.get("filename", str(r))
                    print(f"  ← {name}")
    except json.JSONDecodeError:
        print(raw)


# ============ CLI Entry Point ============

def main():
    parser = argparse.ArgumentParser(
        description="project-wiki: Obsidian CLI wrapper + knowledge metadata enrichment"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Search vault with metadata enrichment")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--domain", "-d", help="Filter by business domain (path prefix)")
    p_search.add_argument("-n", type=int, default=5, help="Max results (default: 5)")
    p_search.add_argument("--json", action="store_true", help="Output as JSON")

    # hit-detect
    p_hit = sub.add_parser("hit-detect", help="Knowledge hit detection for Curator")
    p_hit.add_argument("query", help="Query to check against existing knowledge")

    # knowledge-pack
    p_kp = sub.add_parser("knowledge-pack", help="Generate Knowledge Pack (Curator format)")
    p_kp.add_argument("query", help="Search query")
    p_kp.add_argument("--domain", "-d", required=True, help="Business domain")
    p_kp.add_argument("--feature-point", "-f", required=True, help="Feature point name")

    # read
    p_read = sub.add_parser("read", help="Read file with metadata extraction")
    p_read.add_argument("file", help="File path in vault")
    p_read.add_argument("--meta-only", action="store_true", help="Only output frontmatter metadata as JSON")

    # backlinks
    p_bl = sub.add_parser("backlinks", help="List backlinks to a file")
    p_bl.add_argument("file", help="File path in vault")
    p_bl.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    commands = {
        "search": cmd_search,
        "hit-detect": cmd_hit_detect,
        "knowledge-pack": cmd_knowledge_pack,
        "read": cmd_read,
        "backlinks": cmd_backlinks,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
