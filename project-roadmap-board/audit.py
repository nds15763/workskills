#!/usr/bin/env python3
"""Roadmap canvas audit script (v2).

执行硬约束校验。主 Agent 在写回 .canvas 前必须跑一次。

v2 形态校验：
- 首环（spine）竖向：开始在下、结束在上，方向按规则 1A 三槽位精确化
- 横向 runtime：从 spine 节点向右展开，方向按规则 1B
- canvas.group 包裹工作块整体：P + P 的所有 runtime / 子链（递归）
- group 嵌套：允许完全包含，禁止部分相交
- gate 节点：必须封到独立 Gate: group

Exit code:
    0 - 通过（无 P0；P1 仅警告）
    1 - 有 P0 违规（必须修复才能提交）
    2 - --strict 模式下有 P1 违规
    3 - 读文件或解析失败

Usage:
    python3 audit.py /path/to/roadmap.canvas
    python3 audit.py /path/to/roadmap.canvas --root v14-root
    python3 audit.py /path/to/roadmap.canvas --strict
    python3 audit.py /path/to/roadmap.canvas --layout   # 同时跑布局校验
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path

from geometry import (
    ALIGN_TOLERANCE,
    ALL_LEGAL_DIR_PAIRS,
    CONTAINMENT_MARGIN,
    DIR_RUNTIME_CHAIN,
    DIR_RUNTIME_END_TO_PARENT,
    DIR_RUNTIME_INNER_CHAIN,
    DIR_RUNTIME_INNER_END_TO_PARENT,
    DIR_RUNTIME_INNER_PARENT_TO_START,
    DIR_RUNTIME_PARENT_TO_START,
    DIR_SPINE_CHAIN,
    DIR_SPINE_END_TO_ROOT,
    DIR_SPINE_ROOT_TO_START,
    GATE_GROUP_COLOR,
    GREEN,
    GROUP_COLOR_BY_STATUS,
    GROUP_KIND_GATE,
    GROUP_KIND_WORKBLOCK,
    GROUP_STATUS_BY_NODE_COLOR,
    LANE_Y_TOLERANCE,
    LEGAL_COLORS,
    MIN_RUNTIME_X_GAP,
    MIN_SPINE_Y_GAP,
    PROPAGATING_COLORS,
    PURPLE,
    RED,
    YELLOW,
    derive_parent_color,
    edge_pair,
    edge_segments,
    is_business_node,
    is_gate_like_node,
    is_group,
    is_material_node,
    node_center,
    node_color,
    node_rect,
    parse_group_label,
    rect_contains,
    rects_overlap,
    rects_partial_intersect,
    segment_intersects_rect,
)


def load_canvas(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def find_spine(root_id: str | None, by_id: dict, edges: list):
    """Walk vertical spine: root --top→bottom--> 开始 --top→bottom--> ... -> 结束.

    Returns (spine_list, fork_errors). spine_list is [root, 开始, ..., 结束];
    fork_errors lists any node that has >1 outgoing top→bottom spine edges.
    """
    fork_errors: list[str] = []
    if not root_id or root_id not in by_id:
        return [], fork_errors
    spine = [root_id]
    seen = {root_id}

    starts = [
        e["toNode"]
        for e in edges
        if e["fromNode"] == root_id
        and edge_pair(e) == DIR_SPINE_ROOT_TO_START
        and e["toNode"] in by_id
        and is_business_node(by_id[e["toNode"]])
    ]
    if not starts:
        return spine, fork_errors
    if len(starts) > 1:
        fork_errors.append(f"spine fork at root {root_id}: multiple top→bottom start successors {starts}")
        # 取第一个继续走，让后续 group 校验能继续。
    spine.append(starts[0])
    seen.add(starts[0])
    cur = starts[0]

    while True:
        nxts = [
            e["toNode"]
            for e in edges
            if e["fromNode"] == cur
            and edge_pair(e) == DIR_SPINE_CHAIN
            and e["toNode"] in by_id
            and is_business_node(by_id[e["toNode"]])
        ]
        if len(nxts) > 1:
            fork_errors.append(f"spine fork at {cur}: multiple top→bottom successors {nxts}")
            # 仍然继续走 nxts[0]，让后续校验能尽量覆盖
        if not nxts:
            break
        nxt = nxts[0]
        if nxt in seen:
            break
        spine.append(nxt)
        seen.add(nxt)
        cur = nxt
    return spine, fork_errors


def find_inner_ring(R_id: str, I0_id: str, group_id: str | None,
                    edges: list, by_id: dict, innermost: dict):
    """Walk an inner runtime ring: R → I0 → ... → top→top → R.

    Inner rings stay inside `group_id` (R's enclosing workblock group) and
    close back to R via top→top (rule 1C end). Returns (path, end_id, err).
    """
    def dfs(cur, path, seen):
        for e in edges:
            if (
                e["fromNode"] == cur
                and e["toNode"] == R_id
                and edge_pair(e) == DIR_RUNTIME_INNER_END_TO_PARENT
            ):
                return path, cur, None
        nxts = [
            e["toNode"]
            for e in edges
            if e["fromNode"] == cur
            and edge_pair(e) == DIR_RUNTIME_INNER_CHAIN
            and e["toNode"] in by_id
            and is_business_node(by_id[e["toNode"]])
            and innermost.get(e["toNode"]) == group_id
            and e["toNode"] != R_id
        ]
        if not nxts:
            return path, None, f"inner chain from R={R_id} dead-end at {cur}"
        errors = []
        for nxt in nxts:
            if nxt in seen:
                errors.append(f"inner chain revisits {nxt}")
                continue
            found, end_id, err = dfs(nxt, path + [nxt], seen | {nxt})
            if end_id is not None:
                return found, end_id, None
            errors.append(err)
        return path, None, "; ".join(e for e in errors if e) or f"inner chain {R_id}→{I0_id} not closing"

    return dfs(I0_id, [I0_id], {I0_id})


def build_group_index(nodes: list[dict]):
    """Compute for each non-group node which groups contain it geometrically.

    Decoration groups (label 不是 工作块:/Gate: 前缀) are **transparent** for
    innermost-group attribution: a node enclosed by a decoration group AND a
    workblock/Gate group will be attributed to the workblock/Gate group, not
    the decoration. This keeps cross-group edge rules anchored to semantically
    meaningful groups.

    `group_contains` still tracks every group's geometric children (including
    decorations) so the partial-intersect / Gate overlap checks still see them.

    Returns:
        group_contains: dict[group_id -> list[node_id]]  (geometric, any depth)
        innermost: dict[node_id -> innermost workblock/Gate group_id | None]
    """
    groups = [n for n in nodes if is_group(n)]
    group_contains: dict[str, list[str]] = {g["id"]: [] for g in groups}
    innermost: dict[str, str | None] = {}

    def area(g):
        x1, y1, x2, y2 = node_rect(g)
        return max(0, x2 - x1) * max(0, y2 - y1)

    def is_semantic_group(g):
        return parse_group_label(g.get("label")).kind in (GROUP_KIND_WORKBLOCK, GROUP_KIND_GATE)

    semantic_groups = [g for g in groups if is_semantic_group(g)]

    for n in nodes:
        if is_group(n):
            continue
        # Geometric containment for ALL groups (used by partial-intersect, etc.)
        for g in groups:
            if rect_contains(g, n):
                group_contains[g["id"]].append(n["id"])
        # innermost is anchored to semantic groups only — decorations are
        # transparent so they cannot accidentally split a runtime ring.
        sem_containing = [g for g in semantic_groups if rect_contains(g, n)]
        sem_containing.sort(key=area)
        innermost[n["id"]] = sem_containing[0]["id"] if sem_containing else None
    return group_contains, innermost


def find_runtime_ring(parent_id: str, start_id: str, group_id: str | None,
                     edges: list, by_id: dict, innermost: dict):
    """Walk runtime ring: parent --right→left--> start --right→left--> ... --bottom→bottom--> parent.

    Stays within `group_id` (innermost group of start). Returns
    (ring_path, end_id, error_msg). end_id None means no closure found.
    """
    def dfs(cur, path, seen):
        for e in edges:
            if (
                e["fromNode"] == cur
                and e["toNode"] == parent_id
                and edge_pair(e) == DIR_RUNTIME_END_TO_PARENT
            ):
                return path, cur, None
        nxts = [
            e["toNode"]
            for e in edges
            if e["fromNode"] == cur
            and edge_pair(e) == DIR_RUNTIME_CHAIN
            and e["toNode"] in by_id
            and is_business_node(by_id[e["toNode"]])
            and innermost.get(e["toNode"]) == group_id
        ]
        if not nxts:
            return path, None, f"runtime chain dead-end at {cur}"
        errors = []
        for nxt in nxts:
            if nxt in seen:
                errors.append(f"runtime chain revisits {nxt}")
                continue
            found, end_id, err = dfs(nxt, path + [nxt], seen | {nxt})
            if end_id is not None:
                return found, end_id, None
            errors.append(err)
        return path, None, "; ".join(e for e in errors if e) or f"runtime chain from {parent_id} does not close"

    return dfs(start_id, [start_id], {start_id})


def check_inner_rings(R_chain, exclusion, group_id, edges, by_id, innermost, p0, p1):
    """For each R on a runtime chain, recursively check inner runtime rings
    that R may have spawned (rule 1C).

    Inner ring definition: R has one or more outgoing right→left edges to nodes
    inside the same workblock group but NOT already on the outer chain. Each
    such node I0 is an inner-ring start; the chain I0→...→I_last must close
    back to R via top→top (rule 1C end).
    """
    for R in R_chain:
        inner_starts = [
            e["toNode"]
            for e in edges
            if e["fromNode"] == R
            and edge_pair(e) == DIR_RUNTIME_INNER_PARENT_TO_START
            and e["toNode"] in by_id
            and is_business_node(by_id[e["toNode"]])
            and e["toNode"] not in exclusion
            and innermost.get(e["toNode"]) == group_id
        ]
        if not inner_starts:
            if node_color(by_id[R]) in (YELLOW, RED):
                p0.append(
                    f"colored runtime node {R} has no inner runtime ring (rule 3 recursive)"
                )
            continue

        # Rule 6: a grey runtime node cannot own an inner runtime chain.
        # If R is colorless but派生了 inner chain，是 P0 违规。
        if node_color(by_id[R]) is None:
            p0.append(
                f"grey runtime node {R} has inner runtime chain (rule 6 violation)"
            )

        for I0 in inner_starts:
            inner_path, inner_end, err = find_inner_ring(
                R, I0, group_id, edges, by_id, innermost
            )
            if inner_end is None:
                p0.append(f"inner runtime ring rooted at {R} not closed: {err}")
                continue
            inner_colors = [node_color(by_id[i]) for i in inner_path]
            expected = derive_parent_color(inner_colors)
            actual = node_color(by_id[R])
            if actual is None:
                # Already flagged grey-R-with-ring above, skip propagation check.
                pass
            elif expected != actual:
                p1.append(
                    f"inner ring node {R} color {actual!r} doesn't match its "
                    f"inner ring colors {inner_colors} (expected {expected!r})"
                )

            # Recurse into inner_path for inner-inner rings.
            new_exclusion = exclusion | set(inner_path)
            check_inner_rings(
                R_chain=inner_path,
                exclusion=new_exclusion,
                group_id=group_id,
                edges=edges,
                by_id=by_id,
                innermost=innermost,
                p0=p0,
                p1=p1,
            )


def looks_like_gate_node(n: dict) -> bool:
    return is_gate_like_node(n)


def audit(canvas: dict, root_id: str | None = None) -> dict:
    nodes = canvas.get("nodes", [])
    edges = canvas.get("edges", [])
    by_id = {n["id"]: n for n in nodes}

    p0: list[str] = []
    p1: list[str] = []
    p2: list[str] = []

    # ---- 1. Basic integrity --------------------------------------------- #
    if len(nodes) != len({n["id"] for n in nodes}):
        p0.append("duplicate node id")
    if len(edges) != len({e["id"] for e in edges}):
        p0.append("duplicate edge id")

    for e in edges:
        if e["fromNode"] not in by_id:
            p0.append(f"edge {e['id']} fromNode {e['fromNode']} not found")
        if e["toNode"] not in by_id:
            p0.append(f"edge {e['id']} toNode {e['toNode']} not found")

    for n in nodes:
        if node_color(n) not in LEGAL_COLORS:
            p0.append(f"node {n['id']} illegal color {node_color(n)!r}")

    material_ids = {n["id"] for n in nodes if is_material_node(n)}
    material_edge_ids = {
        e["id"]
        for e in edges
        if e.get("fromNode") in material_ids or e.get("toNode") in material_ids
    }
    for e in edges:
        if e.get("id") in material_edge_ids:
            p1.append(
                f"material/note node must not have topology edges: "
                f"{e['id']} {e.get('fromNode')}→{e.get('toNode')}"
            )

    # ---- 2. Group index + business node set ----------------------------- #
    groups = [n for n in nodes if is_group(n)]
    group_ids = {g["id"] for g in groups}
    group_contains, innermost = build_group_index(nodes)

    biz = [n for n in nodes if is_business_node(n)]
    biz_ids = {n["id"] for n in biz}

    # Business node rectangle overlap (groups excluded by is_business_node).
    for i in range(len(biz)):
        for j in range(i + 1, len(biz)):
            if rects_overlap(biz[i], biz[j]):
                p0.append(f"overlap: {biz[i]['id']} vs {biz[j]['id']}")

    # Port separation: a node cannot receive and emit edges on the same side.
    # This catches visually ambiguous "same-side in/out" joins before they
    # become unreadable in Obsidian.
    for n in nodes:
        if is_group(n) or n["id"] in material_ids:
            continue
        incoming = {
            e.get("toSide")
            for e in edges
            if e.get("id") not in material_edge_ids
            and e.get("toNode") == n["id"]
            and e.get("toSide")
        }
        outgoing = {
            e.get("fromSide")
            for e in edges
            if e.get("id") not in material_edge_ids
            and e.get("fromNode") == n["id"]
            and e.get("fromSide")
        }
        both = sorted(incoming & outgoing)
        if both:
            p0.append(f"node {n['id']} has incoming and outgoing edges on same side(s): {both}")

    # Edge paths must not pass through unrelated node rectangles. Groups are
    # containers and are exempt; all visible non-group nodes participate.
    non_groups = [n for n in nodes if not is_group(n)]
    for e in edges:
        if e.get("id") in material_edge_ids:
            continue
        if e.get("fromNode") not in by_id or e.get("toNode") not in by_id:
            continue
        for n in non_groups:
            if n["id"] in (e.get("fromNode"), e.get("toNode")):
                continue
            if any(segment_intersects_rect(a, b, n) for a, b in edge_segments(e, by_id)):
                p0.append(f"edge {e['id']} overlaps node {n['id']}")

    # ---- 3. Directed reachability single-tree --------------------------- #
    # Root may be a purple guard (not a business node). Include root in the
    # topology so spine connects.
    if root_id is None:
        # Pick a root: prefer non-business nodes with no incoming, fall back
        # to business nodes.
        all_topo = {n["id"] for n in nodes if not is_group(n)}
        incoming = defaultdict(int)
        for e in edges:
            if e["toNode"] in all_topo and e["fromNode"] in all_topo:
                incoming[e["toNode"]] += 1
        candidates = [nid for nid in all_topo if incoming[nid] == 0]
        if len(candidates) == 1:
            root_id = candidates[0]
        elif candidates:
            root_id = candidates[0]
            p1.append(f"multiple root candidates: {candidates[:5]}")
        elif biz:
            root_id = biz[0]["id"]

    topo_ids = biz_ids | ({root_id} if root_id else set())
    adj_directed = defaultdict(set)
    for e in edges:
        f, t = e["fromNode"], e["toNode"]
        if f in topo_ids and t in topo_ids:
            adj_directed[f].add(t)

    reached = set()
    if root_id and root_id in topo_ids:
        q = deque([root_id])
        reached.add(root_id)
        while q:
            cur = q.popleft()
            for nxt in adj_directed[cur]:
                if nxt not in reached:
                    reached.add(nxt)
                    q.append(nxt)
    # unreached only counts business nodes (root itself is allowed to be non-biz).
    unreached = biz_ids - reached
    if unreached:
        p0.append(f"disconnected business nodes ({len(unreached)}): {sorted(unreached)[:10]}")

    # ---- 4. Spine identification + 1A direction validation -------------- #
    spine, spine_fork_errors = find_spine(root_id, by_id, edges)
    spine_set = set(spine)
    for err in spine_fork_errors:
        p0.append(err)

    # 一个 spine 节点不能同时有 top→bottom 出边到非 spine 节点（"伪分叉"）
    # find_spine 只走 spine 内 top→bottom 后继，但如果 cur 同时还有 top→bottom 到一个不在 spine 上的业务节点，也是分叉。
    for sid in spine:
        nxts = [
            e["toNode"]
            for e in edges
            if e["fromNode"] == sid
            and edge_pair(e) == DIR_SPINE_CHAIN
            and e["toNode"] in biz_ids
        ]
        if len(nxts) > 1:
            extras = [n for n in nxts if n not in spine_set]
            for extra in extras:
                p0.append(f"spine fork: {sid} has extra top→bottom successor {extra} not on linear spine")

    # Spine y monotonic: 开始 y 最大、结束 y 最小（i+1 在 i 上方）
    if len(spine) >= 2:
        x_root, y_root = node_center(by_id[spine[0]])
        last_y = y_root
        for nid in spine[1:]:
            x, y = node_center(by_id[nid])
            if abs(x - x_root) > ALIGN_TOLERANCE:
                p0.append(f"spine node {nid} x-center not aligned with root {spine[0]}")
            # spine 链 i+1 在 i 上方：y 应该小于上一个节点
            # root → 开始 是从根外圈跳到最下方开始：开始 y > root y
            last_y = y

        # 检查 段 1: 开始 y 必须大于 root y
        x_start, y_start = node_center(by_id[spine[1]])
        if y_start <= y_root + MIN_SPINE_Y_GAP:
            p0.append(f"spine 开始 {spine[1]} should be below root {spine[0]} (y greater)")
        # 检查 段 2: 链内 y 单调递减
        for i in range(2, len(spine)):
            _, prev_y = node_center(by_id[spine[i - 1]])
            _, cur_y = node_center(by_id[spine[i]])
            if cur_y >= prev_y - MIN_SPINE_Y_GAP:
                p0.append(f"spine node {spine[i]} should be above {spine[i - 1]} (y smaller)")

    # All edges between spine nodes must use one of three slots.
    for e in edges:
        f, t = e["fromNode"], e["toNode"]
        if f in spine_set and t in spine_set:
            pair = edge_pair(e)
            slot = None
            if f == root_id:
                if pair == DIR_SPINE_ROOT_TO_START:
                    slot = "root_to_start"
            if t == root_id:
                if pair == DIR_SPINE_END_TO_ROOT:
                    slot = "end_to_root"
            if f != root_id and t != root_id:
                if pair == DIR_SPINE_CHAIN:
                    slot = "chain"
            if slot is None:
                p0.append(f"spine edge {e['id']} ({f}→{t}) wrong direction {pair}")

    # End → root closure must exist if spine has ≥ 2 nodes.
    if len(spine) >= 2:
        end_id = spine[-1]
        end_to_root = [
            e for e in edges
            if e["fromNode"] == end_id
            and e["toNode"] == root_id
            and edge_pair(e) == DIR_SPINE_END_TO_ROOT
        ]
        if not end_to_root:
            p0.append(f"spine 结束 {end_id} has no closure edge back to root {root_id}")

    # ---- 5. Group rules ------------------------------------------------- #
    # 5a. Group nesting: any two groups must be either fully contained or fully disjoint.
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            if rects_partial_intersect(groups[i], groups[j]):
                p0.append(f"group partial intersect {groups[i]['id']} <-> {groups[j]['id']}")

    # 5b. Workblock groups: spine nodes 黄/红/绿 must be inside a 工作块: group
    #     whose owner_id matches AND geometrically contains P.
    spine_workblock_groups: dict[str, dict] = {}
    for nid in spine:
        if nid == root_id:
            continue
        n = by_id.get(nid)
        if not n:
            continue
        col = node_color(n)
        if col not in (YELLOW, RED, GREEN):
            # Grey spine node must NOT have a workblock group pointing at it.
            for g in groups:
                gl = parse_group_label(g.get("label"))
                if gl.kind == GROUP_KIND_WORKBLOCK and gl.owner_id == nid:
                    p0.append(f"grey spine node {nid} should not have workblock group {g['id']}")
            continue
        owners = []
        for g in groups:
            gl = parse_group_label(g.get("label"))
            if gl.kind == GROUP_KIND_WORKBLOCK and gl.owner_id == nid:
                owners.append((g, gl))
        if not owners:
            p0.append(f"colored spine node {nid} (color={col}) missing 工作块: group")
            continue
        if len(owners) > 1:
            p1.append(f"spine node {nid} has multiple workblock groups: {[g['id'] for g, _ in owners]}")
        g, gl = owners[0]
        spine_workblock_groups[nid] = g

        # Group must geometrically contain P.
        if not rect_contains(g, n):
            p0.append(f"workblock group {g['id']} does not contain its spine node {nid}")

        # Status suffix must match P.color.
        expected_status = GROUP_STATUS_BY_NODE_COLOR.get(col)
        if gl.status != expected_status:
            p0.append(
                f"workblock group {g['id']} status {gl.status!r} mismatches spine node "
                f"{nid} color {col!r} (expected status {expected_status!r})"
            )

        # group color must mirror P.
        expected_group_color = GROUP_COLOR_BY_STATUS.get(col)
        if node_color(g) != expected_group_color:
            p0.append(
                f"workblock group {g['id']} color {node_color(g)!r} mismatches spine node "
                f"{nid} color {col!r} (expected group color {expected_group_color!r})"
            )

    # 5c. Gate groups + Gate nodes
    gate_groups = [g for g in groups if parse_group_label(g.get("label")).kind == GROUP_KIND_GATE]
    for g in gate_groups:
        if node_color(g) != GATE_GROUP_COLOR:
            p1.append(f"gate group {g['id']} color {node_color(g)!r} should be {GATE_GROUP_COLOR!r}")

    # Gate group must NOT overlap any workblock group.
    for gg in gate_groups:
        for wg in groups:
            if wg is gg:
                continue
            wgl = parse_group_label(wg.get("label"))
            if wgl.kind != GROUP_KIND_WORKBLOCK:
                continue
            if rects_overlap(gg, wg):
                p0.append(f"gate group {gg['id']} overlaps workblock group {wg['id']}")

    # Any gate node (text starts with KP- or contains 'Gate:') must be inside a Gate: group.
    for n in nodes:
        if is_group(n):
            continue
        if not looks_like_gate_node(n):
            continue
        gid = innermost.get(n["id"])
        in_gate_group = False
        if gid:
            gl = parse_group_label(by_id[gid].get("label"))
            if gl.kind == GROUP_KIND_GATE:
                in_gate_group = True
        if not in_gate_group:
            p0.append(f"gate node {n['id']} not inside any Gate: group")
        if n["id"] not in spine_set:
            p0.append(f"gate node {n['id']} is not inline on the spine")
        gate_in = [
            e for e in edges
            if e.get("toNode") == n["id"]
            and e.get("fromNode") in by_id
            and not is_group(by_id[e["fromNode"]])
        ]
        gate_out = [
            e for e in edges
            if e.get("fromNode") == n["id"]
            and e.get("toNode") in by_id
            and not is_group(by_id[e["toNode"]])
        ]
        if not gate_in or not gate_out:
            p0.append(f"gate node {n['id']} must connect predecessor -> gate -> successor")

    # ---- 6. Runtime rings: closure + 1B direction + color propagation --- #
    # Each spine non-root node may have at most one runtime entry edge (right→left)
    # to a node inside its workblock group.
    for nid in spine:
        if nid == root_id:
            continue
        n = by_id.get(nid)
        if not n:
            continue
        wb_group = spine_workblock_groups.get(nid)
        runtime_starts = [
            e["toNode"]
            for e in edges
            if e["fromNode"] == nid
            and edge_pair(e) == DIR_RUNTIME_PARENT_TO_START
            and e["toNode"] in by_id
            and is_business_node(by_id[e["toNode"]])
        ]
        if not runtime_starts:
            if node_color(n) == YELLOW:
                p0.append(f"yellow spine node {nid} has no runtime entry edge (rule 3)")
            continue

        if len(runtime_starts) > 1:
            p1.append(f"spine node {nid} has multiple runtime entries: {runtime_starts}")

        start_id = runtime_starts[0]
        # Runtime start must live inside the workblock group of nid.
        if wb_group and innermost.get(start_id) != wb_group["id"]:
            p0.append(f"runtime start {start_id} not inside workblock group of {nid}")

        group_id = wb_group["id"] if wb_group else innermost.get(start_id)
        path, end_id, err = find_runtime_ring(nid, start_id, group_id, edges, by_id, innermost)
        if end_id is None:
            p0.append(f"runtime ring for {nid} not closed: {err}")
            continue

        # All nodes on the runtime path must be inside the same workblock group.
        if wb_group:
            for rnid in path:
                if not rect_contains(wb_group, by_id[rnid]):
                    p0.append(f"runtime node {rnid} outside workblock group {wb_group['id']}")

        # Color propagation: ring colors → expected parent color
        ring_colors = [node_color(by_id[rnid]) for rnid in path]
        expected = derive_parent_color(ring_colors)
        actual = node_color(n)
        if actual is None:
            p0.append(f"grey spine node {nid} has runtime ring (rule 6 violation)")
        elif expected != actual:
            p0.append(
                f"spine node {nid} color {actual!r} mismatches ring propagation "
                f"(expected {expected!r}; ring colors={ring_colors})"
            )

        # Runtime geometry: x must be strictly monotonic left→right; y must be
        # within LANE_Y_TOLERANCE of the spine node center (same lane).
        spine_cx, spine_cy = node_center(n)
        last_x = None
        for rnid in path:
            rx, ry = node_center(by_id[rnid])
            if last_x is not None and rx <= last_x:
                p0.append(
                    f"runtime ring node {rnid} x={rx} not strictly right of previous {last_x} "
                    f"(rule 1B horizontal chain)"
                )
            last_x = rx
            if abs(ry - spine_cy) > LANE_Y_TOLERANCE:
                p0.append(
                    f"runtime ring node {rnid} y_center {ry} off-lane from parent {nid} "
                    f"y_center {spine_cy} (>{LANE_Y_TOLERANCE} tolerance, rule 1B)"
                )

        # Recursive inner runtime rings (rule 1C). Each node R on the primary
        # ring may itself派生 inner ring inside the same workblock group.
        primary_ring_set = set(path)
        primary_ring_set.add(nid)
        check_inner_rings(
            R_chain=path,
            exclusion=primary_ring_set,
            group_id=group_id,
            edges=edges,
            by_id=by_id,
            innermost=innermost,
            p0=p0,
            p1=p1,
        )

        # Inner-ring lane geometry: each inner chain's nodes must sit BELOW
        # their parent runtime node by at least one lane offset.
        for R in path:
            inner_starts = [
                e["toNode"]
                for e in edges
                if e["fromNode"] == R
                and edge_pair(e) == DIR_RUNTIME_INNER_PARENT_TO_START
                and e["toNode"] in by_id
                and is_business_node(by_id[e["toNode"]])
                and innermost.get(e["toNode"]) == group_id
                and e["toNode"] not in primary_ring_set
            ]
            if not inner_starts:
                continue
            R_cy = node_center(by_id[R])[1]
            for I0 in inner_starts:
                inner_path, inner_end, _err = find_inner_ring(
                    R, I0, group_id, edges, by_id, innermost
                )
                if inner_end is None:
                    continue  # closure error already reported elsewhere
                last_inner_x = None
                for inid in inner_path:
                    ix, iy = node_center(by_id[inid])
                    if iy <= R_cy + (LANE_Y_TOLERANCE / 2):
                        p0.append(
                            f"inner runtime node {inid} y_center {iy} not below parent {R} "
                            f"y_center {R_cy} by lane offset (rule 1C)"
                        )
                    if last_inner_x is not None and ix <= last_inner_x:
                        p0.append(
                            f"inner runtime node {inid} x={ix} not strictly right of previous "
                            f"{last_inner_x} (rule 1C horizontal sub-chain)"
                        )
                    last_inner_x = ix

    # ---- 7. Edge color = toNode color ----------------------------------- #
    color_of = {n["id"]: node_color(n) for n in nodes}
    for e in edges:
        if e.get("id") in material_edge_ids:
            continue
        t = e["toNode"]
        if t in material_ids:
            continue
        t_color = color_of.get(t)
        e_color = e.get("color")
        if t_color in PROPAGATING_COLORS and e_color != t_color:
            p1.append(f"edge {e['id']} color {e_color!r} != toNode {t} color {t_color!r}")

    # ---- 8. Edge direction whitelist (catch-all for non-spine non-runtime) #
    for e in edges:
        if e.get("id") in material_edge_ids:
            continue
        pair = edge_pair(e)
        if pair not in ALL_LEGAL_DIR_PAIRS:
            p2.append(f"edge {e['id']} irregular direction {pair}")

    # ---- 9. Cross-group edges ------------------------------------------- #
    # innermost now skips decoration groups (build_group_index v2), so genuine
    # nested decoration cannot create false cross-group reports. We do NOT
    # blanket-allow edges between two semantic groups in nesting relation —
    # that was over-permissive (decoration was the right place to fix this).
    for e in edges:
        if e.get("id") in material_edge_ids:
            continue
        f, t = e["fromNode"], e["toNode"]
        if f not in by_id or t not in by_id:
            continue
        # Spine edges naturally span the whole canvas / cross workblock groups
        # (root → 开始, 链内 i → i+1, 结束 → root). They are not violations.
        if f in spine_set and t in spine_set:
            continue
        gf = innermost.get(f)
        gt = innermost.get(t)
        if gf == gt:
            continue
        if gf and gt and gf != gt:
            p0.append(f"edge {e['id']} crosses runtime groups {gf} -> {gt}")
            continue
        # One side is in a group, the other is outside. This is fine only if
        # the outside endpoint is the workblock owner of the group.
        outside = t if gf else f
        group_id = gf or gt
        if group_id and group_id in group_ids:
            gl = parse_group_label(by_id[group_id].get("label"))
            if gl.kind == GROUP_KIND_WORKBLOCK and gl.owner_id == outside:
                continue
            if gl.kind == GROUP_KIND_GATE:
                # Gate group: only spine→gate-node-in-group is implicit; treat as warning
                p1.append(f"edge {e['id']} crosses gate group {group_id} boundary")
                continue
            p1.append(f"edge {e['id']} crosses group {group_id} boundary without ownership")

    # ---- 10. Red node Exception reminder -------------------------------- #
    for n in biz:
        if node_color(n) == RED:
            p1.append(f"red node {n['id']} needs exception.md entry (verify manually)")

    return {
        "root_id": root_id,
        "spine": spine,
        "biz_nodes": len(biz),
        "groups": len(groups),
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "reached": len(reached),
        "unreached": sorted(unreached),
        "p0": p0,
        "p1": p1,
        "p2": p2,
    }


def main():
    if len(sys.argv) < 2:
        print("usage: audit.py <canvas.json> [--root <root_id>] [--strict]", file=sys.stderr)
        sys.exit(3)
    path = Path(sys.argv[1])
    root_id = None
    strict = False
    if "--root" in sys.argv:
        idx = sys.argv.index("--root")
        if idx + 1 >= len(sys.argv) or sys.argv[idx + 1].startswith("--"):
            print("error: --root requires a node id value", file=sys.stderr)
            sys.exit(3)
        root_id = sys.argv[idx + 1]
    if "--strict" in sys.argv:
        strict = True

    try:
        canvas = load_canvas(path)
    except Exception as exc:
        print(f"load failed: {exc}", file=sys.stderr)
        sys.exit(3)

    report = audit(canvas, root_id=root_id)

    print(f"root          : {report['root_id']}")
    print(f"spine nodes   : {len(report['spine'])} {report['spine']}")
    print(f"groups        : {report['groups']}")
    print(f"biz nodes     : {report['biz_nodes']} / {report['total_nodes']}")
    print(f"edges         : {report['total_edges']}")
    print(f"reached       : {report['reached']} / {report['biz_nodes']}")
    if report["unreached"]:
        print(f"unreached     : {report['unreached'][:10]}")
    print()
    print(f"P0 violations : {len(report['p0'])}")
    for msg in report["p0"]:
        print(f"  [P0] {msg}")
    print(f"P1 violations : {len(report['p1'])}")
    for msg in report["p1"]:
        print(f"  [P1] {msg}")
    print(f"P2 notices    : {len(report['p2'])}")
    for msg in report["p2"][:20]:
        print(f"  [P2] {msg}")

    if report["p0"]:
        sys.exit(1)
    if strict and report["p1"]:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
