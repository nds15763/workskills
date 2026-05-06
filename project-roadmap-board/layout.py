#!/usr/bin/env python3
"""Forward layout generator: JSON spec → .canvas (JSON Canvas v2 form).

Reads a high-level roadmap spec (no coordinates) and produces a fully
laid-out .canvas file with:
- vertical spine (开始 在下、结束 在上)
- horizontal runtime chains attached to colored spine nodes
- canvas.group nodes wrapping each colored spine node + its full runtime tree
- gate nodes wrapped in independent Gate: groups (left of spine)
- edges with precise fromSide/toSide per rule 1A / 1B / 1C

Input format (JSON):
    {
      "root": "v14-root",
      "title": "morph72-v14",
      "spine": [
        {"id": "开始", "state": "green"},
        {"id": "工作块1", "state": "yellow",
         "runtime": [
           {"id": "调查",
            "runtime": [{"id": "实现"}]},
           {"id": "实现2"}
         ]},
        {"id": "结束"}
      ],
      "gates": [{"id": "KP-00", "label": "Domain Locked"}]
    }

`state` is one of `green` / `yellow` / `red` (omit for grey).

Workblock groups are emitted ONLY for colored spine nodes (rule 0K).

CLI:
    python3 layout.py spec.json -o out.canvas [--validate]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from geometry import (
    DIR_RUNTIME_CHAIN,
    DIR_RUNTIME_END_TO_PARENT,
    DIR_RUNTIME_INNER_CHAIN,
    DIR_RUNTIME_INNER_END_TO_PARENT,
    DIR_RUNTIME_INNER_PARENT_TO_START,
    DIR_RUNTIME_PARENT_TO_START,
    DIR_SPINE_CHAIN,
    DIR_SPINE_END_TO_ROOT,
    DIR_SPINE_ROOT_TO_START,
    EDGE_ROUTE_CLEARANCE,
    GAP_HORIZONTAL_RUNTIME,
    GAP_MATERIAL,
    GAP_RING_REGION_MARGIN,
    GAP_VERTICAL_LANE,
    GAP_VERTICAL_SPINE,
    GATE_GROUP_COLOR,
    GREEN,
    GROUP_COLOR_BY_STATUS,
    GROUP_PADDING,
    GROUP_STATUS_BY_NODE_COLOR,
    OFFSET_GATE_GROUP_X,
    OFFSET_SPINE_TO_RUNTIME,
    PURPLE,
    RED,
    SIZE_MATERIAL,
    SIZE_RUNTIME,
    SIZE_SPINE,
    YELLOW,
    derive_parent_color,
    gate_label,
    workblock_label,
)

STATE_TO_COLOR = {
    "green": GREEN,
    "yellow": YELLOW,
    "red": RED,
}
MATERIAL_COLORS = {RED, YELLOW, GREEN, "5", PURPLE}
MATERIAL_TEXT_PREFIX = "说明:"


def _runtime_below_extent(runtime_specs, depth):
    """How far below the runtime parent's center does its sub-tree extend?

    `depth=1` means top-level runtime (same y-lane as parent — extent is
    SIZE_RUNTIME.h/2 below parent center). `depth=2+` adds GAP_VERTICAL_LANE
    per nesting level.
    """
    if not runtime_specs:
        return 0.0
    own = SIZE_RUNTIME[1] / 2 + (depth - 1) * GAP_VERTICAL_LANE
    deeper = max(
        (_runtime_below_extent(s.get("runtime", []), depth + 1) for s in runtime_specs),
        default=0.0,
    )
    return max(own, deeper)


def workblock_y_extents(spine_item):
    """Return (top_offset, bottom_offset) — distance from the spine node CENTER
    to the workblock bbox top/bottom (including GROUP_PADDING).

    Used by region-packing in `Generator.generate()` to allocate enough vertical
    space between spine nodes so that workblock groups don't partial-intersect.
    """
    spine_h_half = SIZE_SPINE[1] / 2
    has_color = STATE_TO_COLOR.get(spine_item.get("state")) in (YELLOW, GREEN, RED)
    if not has_color:
        # No workblock group emitted; bbox is just the spine node itself.
        return (spine_h_half, spine_h_half)
    runtime = spine_item.get("runtime", [])
    materials = spine_item.get("materials", [])
    top_offset = spine_h_half + GROUP_PADDING
    bottom_content_offset = spine_h_half
    if runtime:
        below = _runtime_below_extent(runtime, depth=1)
        bottom_content_offset = max(bottom_content_offset, below)
    if materials:
        material_h = SIZE_MATERIAL[1]
        material_total_h = len(materials) * material_h + (len(materials) - 1) * GAP_MATERIAL
        bottom_content_offset = (
            bottom_content_offset + EDGE_ROUTE_CLEARANCE + GAP_MATERIAL + material_total_h
        )
    bottom_offset = bottom_content_offset + GROUP_PADDING
    return (top_offset, bottom_offset)


def validate_color_consistency(spine_specs, parent_label="<root>", errors=None):
    """Reject spec where a spine/runtime parent's state contradicts its
    children's states under the propagation matrix, OR where a grey parent
    has any runtime children (rule 6).

    The generator output must be auditable; if the spec already disagrees,
    layout.py should fail-fast rather than emit a canvas the audit will
    reject.
    """
    if errors is None:
        errors = []
    for item in spine_specs:
        item_id = item.get("id", "<no-id>")
        item_color = STATE_TO_COLOR.get(item.get("state"))
        children = item.get("runtime", [])
        if children:
            # Rule 6: grey parent shouldn't have any runtime children — runtime
            # only makes sense once the parent is being processed (yellow).
            if item_color is None:
                errors.append(
                    f"{parent_label}/{item_id}: grey parent (no state) has "
                    f"runtime children {[c.get('id') for c in children]} "
                    f"(rule 6: grey nodes shouldn't have runtime chains)"
                )
            else:
                child_colors = [STATE_TO_COLOR.get(c.get("state")) for c in children]
                expected = derive_parent_color(child_colors)
                if item_color != expected:
                    errors.append(
                        f"{parent_label}/{item_id}: state={item.get('state')!r} "
                        f"(color {item_color!r}) but runtime children states "
                        f"{[c.get('state') for c in children]} imply parent color "
                        f"{expected!r}"
                    )
            validate_color_consistency(children, f"{parent_label}/{item_id}", errors)
    return errors


# --------------------------------------------------------------------------- #
# Data classes (using plain dicts for JSON Canvas compatibility)              #
# --------------------------------------------------------------------------- #

def make_text_node(node_id, text, x, y, w, h, color=None, extra=None) -> dict:
    n = {
        "id": node_id,
        "type": "text",
        "text": text,
        "x": int(x),
        "y": int(y),
        "width": int(w),
        "height": int(h),
    }
    if color is not None:
        n["color"] = color
    if extra:
        n.update(extra)
    return n


def make_group_node(group_id, label, x, y, w, h, color) -> dict:
    return {
        "id": group_id,
        "type": "group",
        "label": label,
        "x": int(x),
        "y": int(y),
        "width": int(w),
        "height": int(h),
        "color": color,
    }


def make_edge(edge_id, from_node, from_side, to_node, to_side, color=None) -> dict:
    e = {
        "id": edge_id,
        "fromNode": from_node,
        "fromSide": from_side,
        "toNode": to_node,
        "toSide": to_side,
    }
    if color is not None:
        e["color"] = color
    return e


def is_gate_item(item: dict) -> bool:
    item_id = item.get("id", "")
    return item.get("kind") == "gate" or item_id.startswith("KP-")


def normalize_material_spec(parent_id: str, index: int, item) -> dict:
    """Normalize a spine item's material/note spec into a text-node spec."""
    if isinstance(item, str):
        spec = {"text": item}
    elif isinstance(item, dict):
        spec = dict(item)
    else:
        raise ValueError(f"{parent_id}/materials[{index}] must be string or object")

    text = spec.get("text") or spec.get("label") or spec.get("id") or ""
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{parent_id}/materials[{index}] missing text/label")
    text = text.strip()
    if not text.startswith((MATERIAL_TEXT_PREFIX, "材料:", "图例:", "护栏:")):
        text = f"{MATERIAL_TEXT_PREFIX}{text}"

    color = str(spec.get("color", "5"))
    if color not in MATERIAL_COLORS:
        raise ValueError(
            f"{parent_id}/materials[{index}] color {color!r} must be one of "
            f"{sorted(MATERIAL_COLORS)}"
        )

    return {
        "id": spec.get("id") or f"{parent_id}-material-{index + 1}",
        "text": text,
        "color": color,
        "role": spec.get("role") or "material",
        "roadmapRole": spec.get("roadmapRole") or "material",
        "kind": spec.get("kind") or "material",
        "width": int(spec.get("width", SIZE_MATERIAL[0])),
        "height": int(spec.get("height", SIZE_MATERIAL[1])),
    }


# --------------------------------------------------------------------------- #
# Layout                                                                       #
# --------------------------------------------------------------------------- #

class Generator:
    def __init__(self, spec: dict):
        self.spec = spec
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self._edge_seq = 0

    def _next_edge_id(self) -> str:
        self._edge_seq += 1
        return f"e{self._edge_seq}"

    def emit_edge(self, from_node, direction, to_node, color=None):
        e = make_edge(self._next_edge_id(), from_node, direction[0], to_node, direction[1], color=color)
        self.edges.append(e)

    def generate(self) -> dict:
        root_id = self.spec["root"]
        spine_specs = self.spec.get("spine", [])
        gate_specs = self.spec.get("gates", [])
        if gate_specs:
            raise ValueError("Gate nodes must be inline spine items, not side-lane gates")

        # ---- Spine layout (开始最下、结束最上) with region packing ---- #
        # Reserve enough vertical room for each workblock's expanded bbox so
        # that adjacent workblock groups never partial-intersect.
        spine_w, spine_h = SIZE_SPINE
        n = len(spine_specs)
        extents = [workblock_y_extents(item) for item in spine_specs]
        # Place from i = n-1 (top spine, smallest y) down to i = 0 (bottom spine,
        # largest y). y_centers[i] is spine_specs[i]'s center y.
        y_centers = [0.0] * n
        if n > 0:
            # First spine node (top) sits below root with at least one ring margin.
            y_centers[n - 1] = (spine_h / 2) + extents[n - 1][0] + GAP_RING_REGION_MARGIN
            for i in range(n - 2, -1, -1):
                gap = extents[i + 1][1] + extents[i][0] + GAP_RING_REGION_MARGIN
                y_centers[i] = max(
                    y_centers[i + 1] + gap,
                    y_centers[i + 1] + GAP_VERTICAL_SPINE,  # min spine spacing
                )

        root_y = (y_centers[n - 1] - GAP_VERTICAL_SPINE) if n > 0 else 0
        root_node = make_text_node(
            root_id, root_id,
            -spine_w / 2, root_y - spine_h / 2,
            spine_w, spine_h, color=None,
        )
        self.nodes.append(root_node)

        spine_node_ids: list[str] = [root_id]
        for i, item in enumerate(spine_specs):
            y_center = y_centers[i]
            color = PURPLE if is_gate_item(item) else STATE_TO_COLOR.get(item.get("state"))
            node = make_text_node(
                item["id"], item["id"],
                -spine_w / 2, y_center - spine_h / 2,
                spine_w, spine_h, color=color,
            )
            self.nodes.append(node)
            spine_node_ids.append(item["id"])

        # ---- Runtime layout per colored spine node ---- #
        # We need workblock bounding box for group emission, so collect runtime
        # nodes per spine node first, then emit groups.
        spine_workblock_members: dict[str, list[dict]] = {}
        for i, item in enumerate(spine_specs, start=1):
            sid = item["id"]
            spine_node = next(n for n in self.nodes if n["id"] == sid)
            members: list[dict] = [spine_node]
            self._layout_runtime_chain(spine_node, item.get("runtime", []), members,
                                       parent_dir=DIR_RUNTIME_PARENT_TO_START,
                                       chain_dir=DIR_RUNTIME_CHAIN,
                                       end_dir=DIR_RUNTIME_END_TO_PARENT)
            self._layout_materials(spine_node, item.get("runtime", []), item.get("materials", []), members)
            spine_workblock_members[sid] = members

        # ---- Workblock groups (only for colored spine nodes) ---- #
        for item in spine_specs:
            sid = item["id"]
            if is_gate_item(item):
                continue
            color = STATE_TO_COLOR.get(item.get("state"))
            if color not in (YELLOW, GREEN, RED):
                continue
            members = spine_workblock_members[sid]
            x_min = min(m["x"] for m in members) - GROUP_PADDING
            y_min = min(m["y"] for m in members) - GROUP_PADDING
            x_max = max(m["x"] + m["width"] for m in members) + GROUP_PADDING
            y_max = max(m["y"] + m["height"] for m in members) + GROUP_PADDING
            status = GROUP_STATUS_BY_NODE_COLOR[color]
            label = workblock_label(sid, status)
            group_color = GROUP_COLOR_BY_STATUS[color]
            self.nodes.append(
                make_group_node(f"g-{sid}", label, x_min, y_min, x_max - x_min, y_max - y_min, group_color)
            )

        # ---- Inline Gate groups (gate nodes are on the spine) ----------- #
        for item in spine_specs:
            if not is_gate_item(item):
                continue
            gate_id = item["id"]
            gate_node = next(n for n in self.nodes if n["id"] == gate_id)
            gate_label_text = item.get("label", gate_id)
            self.nodes.append(
                make_group_node(
                    f"gate-{gate_id}",
                    gate_label(gate_id, gate_label_text),
                    gate_node["x"] - GROUP_PADDING,
                    gate_node["y"] - GROUP_PADDING,
                    gate_node["width"] + GROUP_PADDING * 2,
                    gate_node["height"] + GROUP_PADDING * 2,
                    GATE_GROUP_COLOR,
                )
            )

        # ---- Spine edges (1A) ---- #
        # root → 开始
        if spine_specs:
            first_id = spine_specs[0]["id"]
            first_color = STATE_TO_COLOR.get(spine_specs[0].get("state"))
            self.emit_edge(root_id, DIR_SPINE_ROOT_TO_START, first_id, color=first_color)
            # 链内
            for prev, cur in zip(spine_specs, spine_specs[1:]):
                cur_color = STATE_TO_COLOR.get(cur.get("state"))
                self.emit_edge(prev["id"], DIR_SPINE_CHAIN, cur["id"], color=cur_color)
            # 结束 → root
            last_id = spine_specs[-1]["id"]
            self.emit_edge(last_id, DIR_SPINE_END_TO_ROOT, root_id)

        return {
            "nodes": self.nodes,
            "edges": self.edges,
        }

    def _layout_runtime_chain(self, parent_node: dict, chain_specs: list[dict],
                              members_acc: list[dict],
                              parent_dir, chain_dir, end_dir,
                              y_offset: int = 0):
        """Lay out one runtime chain horizontally to the right of parent_node.

        Recursively expands child runtime chains by adding GAP_VERTICAL_LANE
        below the current chain.
        """
        if not chain_specs:
            return
        run_w, run_h = SIZE_RUNTIME
        py_center = parent_node["y"] + parent_node["height"] / 2
        chain_y = py_center - run_h / 2 + y_offset

        # First runtime node x: to the right of parent + offset
        prev_right = parent_node["x"] + parent_node["width"]
        chain_node_ids: list[str] = []
        for j, item in enumerate(chain_specs):
            x = prev_right + (OFFSET_SPINE_TO_RUNTIME if j == 0 else GAP_HORIZONTAL_RUNTIME)
            # All non-first chain nodes use compact GAP_HORIZONTAL_RUNTIME spacing
            color = STATE_TO_COLOR.get(item.get("state"))
            n = make_text_node(item["id"], item["id"], x, chain_y, run_w, run_h, color=color)
            self.nodes.append(n)
            members_acc.append(n)
            chain_node_ids.append(item["id"])
            prev_right = x + run_w

        # Edges within the chain
        first_node_id = chain_node_ids[0]
        first_color = STATE_TO_COLOR.get(chain_specs[0].get("state"))
        self.emit_edge(parent_node["id"], parent_dir, first_node_id, color=first_color)
        for prev, cur in zip(chain_specs, chain_specs[1:]):
            cur_color = STATE_TO_COLOR.get(cur.get("state"))
            self.emit_edge(prev["id"], chain_dir, cur["id"], color=cur_color)
        last_id = chain_node_ids[-1]
        # End → parent edge color must mirror the parent's color (toNode rule).
        self.emit_edge(last_id, end_dir, parent_node["id"], color=parent_node.get("color"))

        # Recurse into each chain node's inner runtime
        for spec, node_id in zip(chain_specs, chain_node_ids):
            inner = spec.get("runtime", [])
            if not inner:
                continue
            inner_parent = next(n for n in self.nodes if n["id"] == node_id)
            self._layout_runtime_chain(
                inner_parent, inner, members_acc,
                parent_dir=DIR_RUNTIME_INNER_PARENT_TO_START,
                chain_dir=DIR_RUNTIME_INNER_CHAIN,
                end_dir=DIR_RUNTIME_INNER_END_TO_PARENT,
                y_offset=GAP_VERTICAL_LANE,
            )

    def _layout_materials(self, spine_node: dict, runtime_specs: list[dict],
                          material_specs: list, members_acc: list[dict]):
        """Place visual-only material nodes inside the spine workblock bbox.

        Materials intentionally get no edges. Their role markers make audit.py
        treat them as non-business nodes even if they use red/yellow/green
        colors to communicate drift, decisions, deletion, or evidence state.
        """
        if not material_specs:
            return
        sx = spine_node["x"]
        sw = spine_node["width"]
        sh = spine_node["height"]
        spine_center_y = spine_node["y"] + sh / 2
        below = max(sh / 2, _runtime_below_extent(runtime_specs, depth=1))
        # Keep material cards to the right of runtime geometry and below the
        # bottom return channel so generated canvases pass visual-overlap audit.
        x = max(m["x"] + m["width"] for m in members_acc) + GAP_HORIZONTAL_RUNTIME
        y = spine_center_y + below + EDGE_ROUTE_CLEARANCE + GAP_MATERIAL

        for i, raw in enumerate(material_specs):
            spec = normalize_material_spec(spine_node["id"], i, raw)
            node = make_text_node(
                spec["id"],
                spec["text"],
                x,
                y,
                spec["width"],
                spec["height"],
                color=spec["color"],
                extra={
                    "roadmapRole": spec["roadmapRole"],
                    "role": spec["role"],
                    "kind": spec["kind"],
                },
            )
            self.nodes.append(node)
            members_acc.append(node)
            y += spec["height"] + GAP_MATERIAL


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Forward layout generator: JSON spec → .canvas")
    parser.add_argument("spec", help="path to JSON spec")
    parser.add_argument("-o", "--output", required=True, help="output .canvas path")
    parser.add_argument("--validate", action="store_true", help="run audit.py against the generated canvas")
    args = parser.parse_args(argv)

    spec_path = Path(args.spec)
    out_path = Path(args.output)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"failed to read spec: {exc}", file=sys.stderr)
        return 3

    if "root" not in spec:
        print("spec missing 'root' field", file=sys.stderr)
        return 3
    if "spine" not in spec:
        print("spec missing 'spine' field", file=sys.stderr)
        return 3

    # Reject spec where parent state contradicts children states (P2-5 from review).
    color_errors = validate_color_consistency(spec["spine"])
    if color_errors:
        print("spec color-consistency errors:", file=sys.stderr)
        for err in color_errors:
            print(f"  - {err}", file=sys.stderr)
        return 3

    try:
        canvas = Generator(spec).generate()
    except ValueError as exc:
        print(f"spec error: {exc}", file=sys.stderr)
        return 3
    out_path.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"generated {out_path} with {len(canvas['nodes'])} nodes, {len(canvas['edges'])} edges")

    if args.validate:
        audit_path = Path(__file__).resolve().parent / "audit.py"
        cmd = [sys.executable, str(audit_path), str(out_path), "--root", spec["root"]]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
