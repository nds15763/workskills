#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claim-hash · canonical identity layer hash calculator

Computes hashes for concept and claim yaml files in _glossary/.

Algorithm (近似 RFC 8785 JCS):
  - sort keys
  - no whitespace
  - utf-8
  - sha256 hex

Hashes:
  concept_identity_hash = sha256(canonical_json({
    kind, identity_condition, not_same_as: [{ref, reason}, ...]
  }))
  local_truth_hash = sha256(canonical_json({
    kind, truth_condition, concept_refs: [{id, identity_hash}, ...]
  }))
  closure_truth_hash = sha256(canonical_json({
    local_truth_hash, depends_on: [{id, closure_truth_hash}, ...]
  }))

Usage:
  # Dry-run (print to stdout, no write)
  claim-hash.py path/to/concept_or_claim.yml

  # Update single file
  claim-hash.py path/to/file.yml --update

  # Batch update all (concept first, then claim by topo order)
  claim-hash.py --all _glossary --update

  # Verify all (drift detection; exit 1 on mismatch)
  claim-hash.py --all _glossary --verify

Exit codes:
  0 - ok
  1 - hash mismatch / drift (--verify mode)
  2 - missing required field / invalid input
  3 - I/O error
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


def canonical_json(obj) -> str:
    """近似 RFC 8785 JCS canonical serialization.

    sorted keys, no whitespace, utf-8.
    Note: 数值规范化非完整 JCS, 对 string-heavy schema 够用.
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_hex(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_concept_identity_hash(concept: dict) -> str:
    """Hash for a concept card.

    Only kind / identity_condition / not_same_as enter the hash.
    Everything else (canonical, aliases, source_ref, status) is excluded.
    """
    for field in ("kind", "identity_condition"):
        if field not in concept:
            raise ValueError(f"concept missing required field: {field}")

    not_same_as = concept.get("not_same_as", []) or []
    payload = {
        "kind": concept["kind"],
        "identity_condition": concept["identity_condition"],
        "not_same_as": sorted(
            [{"ref": x["ref"], "reason": x.get("reason", "")} for x in not_same_as],
            key=lambda x: x["ref"],
        ),
    }
    return sha256_hex(canonical_json(payload))


def compute_local_truth_hash(claim: dict) -> str:
    """Hash for a claim's own statement (intrinsic meaning).

    Only kind / truth_condition / concept_refs (with identity_hash) enter.
    depends_on is NOT in local hash; it's in closure hash.
    """
    for field in ("kind", "truth_condition"):
        if field not in claim:
            raise ValueError(f"claim missing required field: {field}")

    concept_refs = claim.get("concept_refs", []) or []
    for ref in concept_refs:
        if "id" not in ref:
            raise ValueError(f"concept_ref missing 'id': {ref}")
        if "identity_hash" not in ref:
            raise ValueError(
                f"concept_ref {ref['id']} missing 'identity_hash' "
                f"(run claim-hash on the referenced concept first)"
            )

    payload = {
        "kind": claim["kind"],
        "truth_condition": claim["truth_condition"],
        "concept_refs": sorted(
            [{"id": r["id"], "identity_hash": r["identity_hash"]} for r in concept_refs],
            key=lambda x: x["id"],
        ),
    }
    return sha256_hex(canonical_json(payload))


def compute_closure_truth_hash(claim: dict, local_hash: str) -> str:
    """Hash for a claim including its full dependency closure.

    local_truth_hash + depends_on (with closure_truth_hash) enter.
    Cascades up when any upstream claim changes.
    """
    depends_on = claim.get("depends_on", []) or []
    for dep in depends_on:
        if "id" not in dep:
            raise ValueError(f"depends_on entry missing 'id': {dep}")
        if "closure_truth_hash" not in dep:
            raise ValueError(
                f"depends_on {dep['id']} missing 'closure_truth_hash' "
                f"(run claim-hash on the referenced claim first; "
                f"DAG required: no cycles)"
            )

    payload = {
        "local_truth_hash": local_hash,
        "depends_on": sorted(
            [{"id": d["id"], "closure_truth_hash": d["closure_truth_hash"]} for d in depends_on],
            key=lambda x: x["id"],
        ),
    }
    return sha256_hex(canonical_json(payload))


def is_proposed(obj: dict) -> bool:
    """proposed / pending status does not freeze hash."""
    return obj.get("semantic_status") in ("proposed", "pending")


def process_file(path: Path, update: bool = False, verify: bool = False) -> int:
    """Process one yaml file.

    Returns:
      0 - ok
      1 - drift (--verify only)
      2 - missing field / invalid
      3 - I/O error
    """
    try:
        with path.open(encoding="utf-8") as f:
            obj = yaml.safe_load(f)
    except Exception as e:
        print(f"ERR  {path}: read failed: {e}", file=sys.stderr)
        return 3

    if obj is None or not isinstance(obj, dict):
        print(f"SKIP {path}: empty or not a dict", file=sys.stderr)
        return 0

    is_concept = "concept_id" in obj
    is_claim = "claim_id" in obj

    if is_concept and is_claim:
        print(f"ERR  {path}: both concept_id and claim_id present", file=sys.stderr)
        return 2
    if not is_concept and not is_claim:
        print(f"SKIP {path}: neither concept_id nor claim_id", file=sys.stderr)
        return 0

    if is_proposed(obj):
        print(f"SKIP {path}: semantic_status=proposed (hash frozen)", file=sys.stderr)
        return 0

    try:
        if is_concept:
            new_hash = compute_concept_identity_hash(obj)
            old_hash = obj.get("concept_identity_hash")

            if verify:
                if old_hash != new_hash:
                    print(f"DRIFT {path}: concept_identity_hash mismatch", file=sys.stderr)
                    print(f"  expected: {new_hash}", file=sys.stderr)
                    print(f"  current:  {old_hash}", file=sys.stderr)
                    return 1
                print(f"OK   {path}", file=sys.stderr)
                return 0

            if update:
                obj["concept_identity_hash"] = new_hash
                _write_yaml(path, obj)
                print(f"WROTE {path}", file=sys.stderr)
                print(f"  concept_identity_hash: {new_hash}", file=sys.stderr)
            else:
                print(f"{path}:")
                print(f"  concept_identity_hash: {new_hash}")
            return 0

        # claim
        new_local = compute_local_truth_hash(obj)
        new_closure = compute_closure_truth_hash(obj, new_local)
        old_local = obj.get("local_truth_hash")
        old_closure = obj.get("closure_truth_hash")

        if verify:
            rc = 0
            if old_local != new_local:
                print(f"DRIFT {path}: local_truth_hash mismatch", file=sys.stderr)
                print(f"  expected: {new_local}", file=sys.stderr)
                print(f"  current:  {old_local}", file=sys.stderr)
                rc = 1
            if old_closure != new_closure:
                print(f"DRIFT {path}: closure_truth_hash mismatch", file=sys.stderr)
                print(f"  expected: {new_closure}", file=sys.stderr)
                print(f"  current:  {old_closure}", file=sys.stderr)
                rc = 1
            if rc == 0:
                print(f"OK   {path}", file=sys.stderr)
            return rc

        if update:
            obj["local_truth_hash"] = new_local
            obj["closure_truth_hash"] = new_closure
            _write_yaml(path, obj)
            print(f"WROTE {path}", file=sys.stderr)
            print(f"  local_truth_hash:   {new_local}", file=sys.stderr)
            print(f"  closure_truth_hash: {new_closure}", file=sys.stderr)
        else:
            print(f"{path}:")
            print(f"  local_truth_hash:   {new_local}")
            print(f"  closure_truth_hash: {new_closure}")
        return 0

    except ValueError as e:
        print(f"ERR  {path}: {e}", file=sys.stderr)
        return 2


def _write_yaml(path: Path, obj: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            obj,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def process_all(root: Path, update: bool, verify: bool) -> int:
    """Process all concepts/*.yml then claims/*.yml under _glossary root.

    Order matters: concept hashes must exist before claim local_truth_hash,
    and claim hashes must exist before upstream claim closure_truth_hash.
    Within claims/, we sort by filename — DAG-correct ordering left to users
    (claim-hash will error if depends_on closure_truth_hash is missing).
    """
    concept_files = sorted(root.glob("concepts/*.yml"))
    claim_files = sorted(root.glob("claims/*.yml"))

    files = concept_files + claim_files

    if not files:
        print(f"no concepts/*.yml or claims/*.yml under {root}", file=sys.stderr)
        return 0

    exit_code = 0
    for path in files:
        rc = process_file(path, update=update, verify=verify)
        if rc != 0:
            exit_code = max(exit_code, rc)
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="canonical identity layer hash tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", nargs="?", help="yaml file path (single-file mode)")
    parser.add_argument(
        "--all",
        metavar="GLOSSARY_DIR",
        help="process all concepts/*.yml + claims/*.yml under this _glossary dir",
    )
    parser.add_argument("--update", action="store_true", help="write hash back to files")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="verify current hashes match computed (drift detection); exit 1 on mismatch",
    )
    args = parser.parse_args()

    if args.update and args.verify:
        print("ERROR: --update and --verify are mutually exclusive", file=sys.stderr)
        return 2

    if args.all:
        return process_all(Path(args.all), update=args.update, verify=args.verify)

    if not args.path:
        parser.print_help()
        return 2

    return process_file(Path(args.path), update=args.update, verify=args.verify)


if __name__ == "__main__":
    sys.exit(main())
