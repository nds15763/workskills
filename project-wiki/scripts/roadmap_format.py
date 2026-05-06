#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
roadmap_format: reflow roadmap closure trees in Obsidian JSON canvas files.

This formatter is intentionally opinionated for the closure-tree pattern used by:
- project-roadmap-board
- project-knowledge-curator
- project-wiki

It only updates node positions (`x`, `y`) for nodes that participate in a
closure loop:

    parent -> start -> ... -> end -> parent

Nested loops are detected recursively through `bottom -> top` edges and laid out
with stable horizontal/vertical spacing. Text, colors, widths, heights, and all
edges remain unchanged.

Usage:
    python3 roadmap_format.py /path/to/file.canvas
    python3 roadmap_format.py /path/to/file.canvas --check
    python3 roadmap_format.py /path/to/file.canvas --stdout
"""

import argparse
import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


HORIZONTAL_GAP = 180
VERTICAL_GAP = 160


@dataclass(frozen=True)
class Edge:
    edge_id: str
    from_node: str
    to_node: str
    from_side: str
    to_side: str


@dataclass
class Loop:
    parent_id: str
    chain: List[str]


def load_canvas(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_canvas(path: Path, canvas: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(canvas, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def build_edge_indexes(canvas: dict) -> Tuple[Dict[str, List[Edge]], Dict[str, List[Edge]]]:
    outgoing: Dict[str, List[Edge]] = {}
    incoming: Dict[str, List[Edge]] = {}
    for raw_edge in canvas.get("edges", []):
        edge = Edge(
            edge_id=raw_edge["id"],
            from_node=raw_edge["fromNode"],
            to_node=raw_edge["toNode"],
            from_side=raw_edge.get("fromSide", ""),
            to_side=raw_edge.get("toSide", ""),
        )
        outgoing.setdefault(edge.from_node, []).append(edge)
        incoming.setdefault(edge.to_node, []).append(edge)
    return outgoing, incoming


def first_text_line(node: dict) -> str:
    raw = str(node.get("text", "")).splitlines()[0].strip()
    return raw.lstrip("#").strip()


def is_start_node(node: dict) -> bool:
    return first_text_line(node).startswith("开始")


def bottom_start_edges(
    nodes: Dict[str, dict],
    outgoing: Dict[str, List[Edge]],
    parent_id: str,
) -> List[Edge]:
    return [
        edge for edge in outgoing.get(parent_id, [])
        if (
            edge.from_side == "bottom"
            and edge.to_side == "top"
            and is_start_node(nodes[edge.to_node])
        )
    ]


def has_return_edge(outgoing: Dict[str, List[Edge]], current_id: str, parent_id: str) -> bool:
    return any(edge.to_node == parent_id for edge in outgoing.get(current_id, []))


def find_path_to_parent(
    outgoing: Dict[str, List[Edge]],
    current_id: str,
    parent_id: str,
    visited: Set[str],
) -> Optional[List[str]]:
    if current_id in visited:
        return None

    next_visited = set(visited)
    next_visited.add(current_id)

    if has_return_edge(outgoing, current_id, parent_id):
        return [current_id]

    candidates = [
        edge for edge in outgoing.get(current_id, [])
        if edge.to_node != parent_id and edge.to_node not in next_visited
    ]
    candidates.sort(key=lambda edge: (edge.from_side == "bottom", edge.to_node))

    for edge in candidates:
        suffix = find_path_to_parent(outgoing, edge.to_node, parent_id, next_visited)
        if suffix is not None:
            return [current_id] + suffix

    return None


def trace_loop(nodes: Dict[str, dict], outgoing: Dict[str, List[Edge]], parent_id: str) -> Optional[Loop]:
    for start_edge in bottom_start_edges(nodes, outgoing, parent_id):
        chain = find_path_to_parent(outgoing, start_edge.to_node, parent_id, set())
        if chain is not None:
            return Loop(parent_id=parent_id, chain=chain)
    return None


def discover_loops(canvas: dict) -> Dict[str, Loop]:
    nodes = {node["id"]: node for node in canvas.get("nodes", [])}
    outgoing, _incoming = build_edge_indexes(canvas)
    loops: Dict[str, Loop] = {}
    for node in canvas.get("nodes", []):
        loop = trace_loop(nodes, outgoing, node["id"])
        if loop is not None:
            loops[node["id"]] = loop
    return loops


def root_parents(loops: Dict[str, Loop]) -> List[str]:
    nested_parents = {
        node_id
        for loop in loops.values()
        for node_id in loop.chain
        if node_id in loops
    }
    roots = [parent_id for parent_id in loops if parent_id not in nested_parents]
    return sorted(roots)


def format_canvas_layout(canvas: dict) -> dict:
    nodes = {node["id"]: node for node in canvas.get("nodes", [])}
    loops = discover_loops(canvas)
    if not loops:
        return canvas

    slot_width_cache: Dict[str, int] = {}

    def loop_width(parent_id: str) -> int:
        loop = loops[parent_id]
        total = 0
        for index, child_id in enumerate(loop.chain):
            total += slot_width(child_id)
            if index < len(loop.chain) - 1:
                total += HORIZONTAL_GAP
        return total

    def slot_width(node_id: str) -> int:
        if node_id in slot_width_cache:
            return slot_width_cache[node_id]
        base_width = int(nodes[node_id].get("width", 0))
        if node_id in loops:
            base_width = max(base_width, loop_width(node_id))
        slot_width_cache[node_id] = base_width
        return base_width

    def layout_loop(parent_id: str) -> None:
        parent = nodes[parent_id]
        loop = loops[parent_id]
        total_width = loop_width(parent_id)
        center_x = int(parent.get("x", 0)) + int(parent.get("width", 0)) / 2
        cursor_x = round(center_x - total_width / 2)
        row_y = int(parent.get("y", 0)) + int(parent.get("height", 0)) + VERTICAL_GAP

        for child_id in loop.chain:
            child = nodes[child_id]
            child_slot_width = slot_width(child_id)
            child["x"] = int(round(cursor_x + (child_slot_width - int(child.get("width", 0))) / 2))
            child["y"] = int(row_y)
            if child_id in loops:
                layout_loop(child_id)
            cursor_x += child_slot_width + HORIZONTAL_GAP

    for parent_id in root_parents(loops):
        layout_loop(parent_id)

    return canvas


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Format roadmap closure-tree canvas layout")
    parser.add_argument("canvas", help="Path to .canvas file")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if formatting would change the file")
    parser.add_argument("--stdout", action="store_true", help="Print formatted JSON instead of writing the file")
    args = parser.parse_args(argv)

    path = Path(args.canvas)
    original = load_canvas(path)
    formatted = format_canvas_layout(copy.deepcopy(original))

    changed = formatted != original
    if args.check:
        if changed:
            print(f"would reformat: {path}")
            return 1
        print(f"already formatted: {path}")
        return 0

    if args.stdout:
        json.dump(formatted, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    save_canvas(path, formatted)
    if changed:
        print(f"formatted: {path}")
    else:
        print(f"unchanged: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
