#!/usr/bin/env python3
"""Shared constants and pure helpers for the roadmap v2 layout.

audit.py and layout.py MUST import everything from here. **Do NOT redefine
these constants locally** — the whole point of this module is to keep one
single source of truth so the two scripts cannot drift.

Coordinate system: JSON Canvas uses screen coordinates (x grows right, y grows
down). v2 fixes "spine 开始在下、结束在上" semantics: spine node i=1 is the
"开始" (largest y, visually at bottom) and i=N is the "结束" (smallest y,
visually at top).
"""

from __future__ import annotations

from typing import NamedTuple


# --------------------------------------------------------------------------- #
# Colors                                                                       #
# --------------------------------------------------------------------------- #

RED = "1"
YELLOW = "3"
GREEN = "4"
CYAN = "5"
PURPLE = "6"

LEGAL_COLORS = {None, "1", "3", "4", "5", "6"}
PROPAGATING_COLORS = {None, "1", "3", "4"}

# Group color mirrors the spine node it wraps. The CYAN/PURPLE entries below
# are intentionally used for groups so that group nodes never participate in
# spine color propagation (only PROPAGATING_COLORS do).
GROUP_COLOR_BY_STATUS = {
    YELLOW: CYAN,    # 处理中 → 青（不参与传播）
    GREEN: GREEN,    # 已完成 → 绿
    RED: RED,        # 阻塞 → 红
}
GATE_GROUP_COLOR = PURPLE


# --------------------------------------------------------------------------- #
# Spacing & sizing                                                             #
# --------------------------------------------------------------------------- #

GAP_VERTICAL_SPINE = 220        # 首环节点之间 y 距离
GAP_HORIZONTAL_RUNTIME = 200    # runtime 节点之间 x 距离
GAP_VERTICAL_LANE = 200         # 同 group 内多泳道 y 偏移
GROUP_PADDING = 50              # group 矩形相对内部节点的 padding
GAP_RING_REGION_MARGIN = 100    # 相邻 spine 节点的 region 包围盒最小空隙
OFFSET_SPINE_TO_RUNTIME = 280   # 首环节点中心 → 它的 runtime 第一个节点中心
OFFSET_GATE_GROUP_X = -700      # gate group 相对主干的 x 偏移（主干左侧独立列）

SIZE_SPINE = (280, 110)         # (width, height)
SIZE_RUNTIME = (240, 100)
SIZE_MATERIAL = (260, 90)
GAP_MATERIAL = 24


# --------------------------------------------------------------------------- #
# Layout audit tolerances                                                      #
# --------------------------------------------------------------------------- #

ALIGN_TOLERANCE = 80            # spine x 对齐容差
LANE_Y_TOLERANCE = 120          # runtime 同泳道 y 容差
MIN_SPINE_Y_GAP = 40            # spine 相邻节点最小 y 距离
MIN_RUNTIME_X_GAP = 20          # runtime 节点最小 x 距离
CONTAINMENT_MARGIN = 8          # group 包含子节点时允许的边距宽容


# --------------------------------------------------------------------------- #
# Edge direction slots (rule 1A spine + 1B runtime)                            #
# --------------------------------------------------------------------------- #

# Rule 1A: spine 三槽位精确化
DIR_SPINE_ROOT_TO_START = ("top", "bottom")   # 根→开始：根 top 出，开始 bottom 进，开始在根下方
DIR_SPINE_CHAIN = ("top", "bottom")           # 链内 i→i+1：i 的 top 出，i+1 的 bottom 进，i+1 在 i 上方
DIR_SPINE_END_TO_ROOT = ("left", "left")      # 结束→根：结束 left 出，沿左侧外圈回根 left，避开主干节点

# Rule 1B: runtime 横向闭合
DIR_RUNTIME_PARENT_TO_START = ("right", "left")
DIR_RUNTIME_CHAIN = ("right", "left")
DIR_RUNTIME_END_TO_PARENT = ("bottom", "bottom")

# Rule 1C: runtime 内部子链与一级 runtime 同向（不交替）；只在 y 上多偏一行另起泳道
DIR_RUNTIME_INNER_PARENT_TO_START = ("bottom", "top")
DIR_RUNTIME_INNER_CHAIN = ("right", "left")
DIR_RUNTIME_INNER_END_TO_PARENT = ("top", "top")  # 子链结束 top 出回 Q 的 top


# --------------------------------------------------------------------------- #
# Group label conventions                                                      #
# --------------------------------------------------------------------------- #

GROUP_KIND_WORKBLOCK = "工作块"
GROUP_KIND_GATE = "Gate"
GROUP_LABEL_PREFIXES = (f"{GROUP_KIND_WORKBLOCK}:", f"{GROUP_KIND_GATE}:")

GROUP_STATUS_RUNNING = "处理中"
GROUP_STATUS_DONE = "已完成"
GROUP_STATUS_BLOCKED = "阻塞"
GROUP_STATUS_BY_NODE_COLOR = {
    YELLOW: GROUP_STATUS_RUNNING,
    GREEN: GROUP_STATUS_DONE,
    RED: GROUP_STATUS_BLOCKED,
}
GROUP_STATUS_SUFFIXES = (
    f"[{GROUP_STATUS_RUNNING}]",
    f"[{GROUP_STATUS_DONE}]",
    f"[{GROUP_STATUS_BLOCKED}]",
)


def workblock_label(parent_id: str, status: str) -> str:
    """Build a canonical workblock-group label: '工作块:<id>:[处理中|已完成|阻塞]'."""
    return f"{GROUP_KIND_WORKBLOCK}:{parent_id}:[{status}]"


def gate_label(gate_id: str, name: str) -> str:
    """Build a canonical Gate-group label: 'Gate:<gate_id>:<name>'."""
    return f"{GROUP_KIND_GATE}:{gate_id}:{name}"


class GroupLabel(NamedTuple):
    kind: str | None       # "工作块" / "Gate" / None
    owner_id: str | None   # parent_id for workblock, gate_id for gate
    status: str | None     # "处理中"/"已完成"/"阻塞" for workblock, name for gate


def parse_group_label(label: str | None) -> GroupLabel:
    """Parse a group label into (kind, owner_id, status).

    Examples:
        '工作块:p1:[处理中]' → ('工作块', 'p1', '处理中')
        'Gate:KP-00:Domain Locked' → ('Gate', 'KP-00', 'Domain Locked')
        anything else → (None, None, None)
    """
    if not label:
        return GroupLabel(None, None, None)
    parts = label.split(":", 2)
    if len(parts) < 3:
        return GroupLabel(None, None, None)
    kind, owner, rest = parts[0], parts[1], parts[2]
    if kind == GROUP_KIND_WORKBLOCK:
        if rest.startswith("[") and rest.endswith("]"):
            return GroupLabel(kind, owner, rest[1:-1])
        return GroupLabel(kind, owner, None)
    if kind == GROUP_KIND_GATE:
        return GroupLabel(kind, owner, rest)
    return GroupLabel(None, None, None)


# --------------------------------------------------------------------------- #
# Node helpers                                                                 #
# --------------------------------------------------------------------------- #

def node_color(n: dict) -> str | None:
    return n.get("color")


def is_group(n: dict) -> bool:
    return n.get("type") == "group"


def is_gate_like_node(n: dict) -> bool:
    nid = n.get("id") or ""
    text = (n.get("text") or "") + (n.get("label") or "")
    return nid.startswith("KP-") or "Gate:" in text or text.strip().startswith("KP-")


MATERIAL_ROLE_VALUES = {"material", "note", "annotation"}
MATERIAL_TEXT_PREFIXES = (
    "说明:",
    "说明：",
    "图例:",
    "图例：",
    "护栏:",
    "护栏：",
    "材料池:",
    "材料池：",
    "材料:",
    "材料：",
    "删除项:",
    "删除项：",
    "证据索引:",
    "证据索引：",
)


def is_material_node(n: dict) -> bool:
    """True iff n is a visual-only material/note node.

    Material nodes are allowed inside workblock groups as context, evidence,
    UI drift notes, decision points, or deletion notes. They never participate
    in business topology or color propagation.
    """
    if is_group(n):
        return False
    for key in ("roadmapRole", "role", "kind"):
        value = n.get(key)
        if isinstance(value, str) and value.strip().lower() in MATERIAL_ROLE_VALUES:
            return True
    text = ((n.get("text") or "") + (n.get("label") or "")).strip()
    return text.startswith(MATERIAL_TEXT_PREFIXES)


def is_business_node(n: dict) -> bool:
    """True iff n is a business node (participates in spine / runtime topology
    and color propagation). Excludes:
    - group containers (type=group)
    - cyan/purple nodes (legend / guard)
    - text nodes whose body marks them as legend/guard
    """
    if is_group(n):
        return False
    if is_material_node(n):
        return False
    c = node_color(n)
    if c == CYAN:
        return False
    if c == PURPLE and not is_gate_like_node(n):
        return False
    text = (n.get("text") or "") + (n.get("label") or "")
    if any(tag in text for tag in ("说明", "图例", "护栏", "说明节点")):
        return False
    return True


def node_rect(n: dict) -> tuple[float, float, float, float]:
    """Return (x1, y1, x2, y2) in screen coordinates."""
    x = float(n.get("x", 0))
    y = float(n.get("y", 0))
    w = float(n.get("width", 0))
    h = float(n.get("height", 0))
    return (x, y, x + w, y + h)


def node_center(n: dict) -> tuple[float, float]:
    x1, y1, x2, y2 = node_rect(n)
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def side_anchor(n: dict, side: str | None) -> tuple[float, float]:
    """Return the anchor point for a node side."""
    x1, y1, x2, y2 = node_rect(n)
    cx, cy = node_center(n)
    if side == "top":
        return (cx, y1)
    if side == "right":
        return (x2, cy)
    if side == "bottom":
        return (cx, y2)
    if side == "left":
        return (x1, cy)
    return (cx, cy)


# --------------------------------------------------------------------------- #
# Rectangle predicates                                                         #
# --------------------------------------------------------------------------- #

def rect_contains(outer: dict, inner: dict, margin: float = CONTAINMENT_MARGIN) -> bool:
    """outer fully contains inner, allowing `margin` slack on every side."""
    ox1, oy1, ox2, oy2 = node_rect(outer)
    ix1, iy1, ix2, iy2 = node_rect(inner)
    return (
        ix1 >= ox1 - margin
        and iy1 >= oy1 - margin
        and ix2 <= ox2 + margin
        and iy2 <= oy2 + margin
    )


def rects_overlap(a: dict, b: dict) -> bool:
    """Any geometric overlap (including full containment)."""
    ax1, ay1, ax2, ay2 = node_rect(a)
    bx1, by1, bx2, by2 = node_rect(b)
    return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)


def rects_partial_intersect(a: dict, b: dict, margin: float = CONTAINMENT_MARGIN) -> bool:
    """True iff a and b overlap but neither fully contains the other.

    This is THE predicate for "嵌套 group 部分相交" (rule 0K) — partial
    intersection is illegal, but full containment is allowed.
    """
    if not rects_overlap(a, b):
        return False
    if rect_contains(a, b, margin) or rect_contains(b, a, margin):
        return False
    return True


# --------------------------------------------------------------------------- #
# Edge / rectangle predicates                                                  #
# --------------------------------------------------------------------------- #

EDGE_ROUTE_CLEARANCE = 50


def _segment_bbox_intersects_rect(a: tuple[float, float], b: tuple[float, float],
                                  rect: tuple[float, float, float, float]) -> bool:
    x1, y1, x2, y2 = rect
    return not (
        max(a[0], b[0]) <= x1
        or min(a[0], b[0]) >= x2
        or max(a[1], b[1]) <= y1
        or min(a[1], b[1]) >= y2
    )


def segment_intersects_rect(a: tuple[float, float], b: tuple[float, float], n: dict) -> bool:
    """True iff segment a-b crosses the open interior of n's rectangle.

    Touching a node border is allowed so bottom/top return channels can run
    along the outside of a node without being reported as a visual overlap.
    """
    x1, y1, x2, y2 = node_rect(n)
    if not _segment_bbox_intersects_rect(a, b, (x1, y1, x2, y2)):
        return False

    ax, ay = a
    bx, by = b
    if ax == bx:
        if not (x1 < ax < x2):
            return False
        return max(ay, by) > y1 and min(ay, by) < y2
    if ay == by:
        if not (y1 < ay < y2):
            return False
        return max(ax, bx) > x1 and min(ax, bx) < x2

    # Fallback for diagonal/curved approximations: sample enough points to
    # catch practical canvas overlaps without pulling in geometry deps.
    steps = max(8, int(max(abs(ax - bx), abs(ay - by)) // 20))
    for i in range(1, steps):
        t = i / steps
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t
        if x1 < x < x2 and y1 < y < y2:
            return True
    return False


def edge_segments(e: dict, by_id: dict[str, dict]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Return an auditable Manhattan route for a JSON Canvas edge."""
    f = by_id.get(e.get("fromNode"))
    t = by_id.get(e.get("toNode"))
    if not f or not t:
        return []
    pair = edge_pair(e)
    start = side_anchor(f, pair[0])
    end = side_anchor(t, pair[1])

    if pair == DIR_RUNTIME_END_TO_PARENT:
        y = max(start[1], end[1]) + EDGE_ROUTE_CLEARANCE
        points = [start, (start[0], y), (end[0], y), end]
    elif pair == DIR_RUNTIME_INNER_END_TO_PARENT:
        y = min(start[1], end[1]) - EDGE_ROUTE_CLEARANCE
        points = [start, (start[0], y), (end[0], y), end]
    elif pair == DIR_SPINE_ROOT_TO_START:
        x = min(node_rect(f)[0], node_rect(t)[0]) - EDGE_ROUTE_CLEARANCE
        points = [start, (x, start[1]), (x, end[1]), end]
    elif pair == DIR_SPINE_END_TO_ROOT:
        x = min(node_rect(f)[0], node_rect(t)[0]) - EDGE_ROUTE_CLEARANCE
        points = [start, (x, start[1]), (x, end[1]), end]
    elif start[0] == end[0] or start[1] == end[1]:
        points = [start, end]
    else:
        mid_x = (start[0] + end[0]) / 2
        points = [start, (mid_x, start[1]), (mid_x, end[1]), end]
    return list(zip(points, points[1:]))


# --------------------------------------------------------------------------- #
# Edge helpers                                                                 #
# --------------------------------------------------------------------------- #

def edge_pair(e: dict) -> tuple[str | None, str | None]:
    return (e.get("fromSide"), e.get("toSide"))


SPINE_DIR_PAIRS = {DIR_SPINE_ROOT_TO_START, DIR_SPINE_CHAIN, DIR_SPINE_END_TO_ROOT}
RUNTIME_DIR_PAIRS = {
    DIR_RUNTIME_PARENT_TO_START,
    DIR_RUNTIME_CHAIN,
    DIR_RUNTIME_END_TO_PARENT,
    DIR_RUNTIME_INNER_PARENT_TO_START,
    DIR_RUNTIME_INNER_END_TO_PARENT,
}
ALL_LEGAL_DIR_PAIRS = SPINE_DIR_PAIRS | RUNTIME_DIR_PAIRS


# --------------------------------------------------------------------------- #
# Color propagation                                                            #
# --------------------------------------------------------------------------- #

def derive_parent_color(child_colors):
    """Derive the color a parent should have given its ring members' colors.

    全绿 → 绿 / 全红 → 红 / 其他（含全灰）→ 黄。
    "全灰" 是父节点刚 灰→黄、还没人开始处理 runtime 子节点的合法初始态。
    """
    has_red = RED in child_colors
    has_yellow = YELLOW in child_colors
    has_green = GREEN in child_colors
    has_grey = None in child_colors
    if has_green and not has_red and not has_yellow and not has_grey:
        return GREEN
    if has_red and not has_yellow and not has_green and not has_grey:
        return RED
    return YELLOW
