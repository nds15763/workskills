#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("roadmap_format.py")
SPEC = importlib.util.spec_from_file_location("roadmap_format", SCRIPT_PATH)
roadmap_format = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(roadmap_format)


def make_node(node_id, text, x, y, width=120, height=60, color=None):
    node = {
        "id": node_id,
        "type": "text",
        "text": text,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }
    if color is not None:
        node["color"] = color
    return node


def make_edge(edge_id, from_node, to_node, from_side, to_side):
    return {
        "id": edge_id,
        "fromNode": from_node,
        "fromSide": from_side,
        "toNode": to_node,
        "toSide": to_side,
    }


class RoadmapFormatTests(unittest.TestCase):
    def setUp(self):
        self.canvas = {
            "nodes": [
                make_node("root", "Root", 400, 0, width=180, height=80, color="3"),
                make_node("top-start", "开始 Top", 0, 200, width=150, height=70),
                make_node("g2", "Gate 2", 240, 200, width=150, height=70, color="3"),
                make_node("top-end", "结束 Top", 520, 200, width=150, height=70),
                make_node("g2-start", "开始 Gate 2", 200, 380, width=150, height=60),
                make_node("g2-mid", "实现 Gate 2", 420, 380, width=170, height=60),
                make_node("g2-end", "结束 Gate 2", 660, 380, width=150, height=60),
                make_node("note", "说明", 900, 100, width=220, height=120, color="6"),
            ],
            "edges": [
                make_edge("root-start", "root", "top-start", "bottom", "top"),
                make_edge("root-mid", "top-start", "g2", "right", "left"),
                make_edge("root-end", "g2", "top-end", "right", "left"),
                make_edge("root-close", "top-end", "root", "top", "bottom"),
                make_edge("g2-loop-start", "g2", "g2-start", "bottom", "top"),
                make_edge("g2-loop-mid", "g2-start", "g2-mid", "right", "left"),
                make_edge("g2-loop-end", "g2-mid", "g2-end", "right", "left"),
                make_edge("g2-loop-close", "g2-end", "g2", "top", "bottom"),
            ],
        }

    def test_formats_closure_tree_with_nested_loop_spacing(self):
        formatted = roadmap_format.format_canvas_layout(copy.deepcopy(self.canvas))
        nodes = {node["id"]: node for node in formatted["nodes"]}

        row_y = nodes["root"]["y"] + nodes["root"]["height"] + roadmap_format.VERTICAL_GAP
        self.assertEqual(nodes["top-start"]["y"], row_y)
        self.assertEqual(nodes["g2"]["y"], row_y)
        self.assertEqual(nodes["top-end"]["y"], row_y)

        g1_right = nodes["top-start"]["x"] + nodes["top-start"]["width"]
        g2_right = nodes["g2"]["x"] + nodes["g2"]["width"]
        self.assertGreaterEqual(nodes["g2"]["x"] - g1_right, roadmap_format.HORIZONTAL_GAP)
        self.assertGreaterEqual(nodes["top-end"]["x"] - g2_right, roadmap_format.HORIZONTAL_GAP)

        child_row_y = nodes["g2"]["y"] + nodes["g2"]["height"] + roadmap_format.VERTICAL_GAP
        self.assertEqual(nodes["g2-start"]["y"], child_row_y)
        self.assertEqual(nodes["g2-mid"]["y"], child_row_y)
        self.assertEqual(nodes["g2-end"]["y"], child_row_y)

        start_right = nodes["g2-start"]["x"] + nodes["g2-start"]["width"]
        mid_right = nodes["g2-mid"]["x"] + nodes["g2-mid"]["width"]
        self.assertGreaterEqual(nodes["g2-mid"]["x"] - start_right, roadmap_format.HORIZONTAL_GAP)
        self.assertGreaterEqual(nodes["g2-end"]["x"] - mid_right, roadmap_format.HORIZONTAL_GAP)

    def test_only_positions_change_for_loop_nodes(self):
        original = copy.deepcopy(self.canvas)
        formatted = roadmap_format.format_canvas_layout(copy.deepcopy(self.canvas))

        original_nodes = {node["id"]: node for node in original["nodes"]}
        formatted_nodes = {node["id"]: node for node in formatted["nodes"]}

        for node_id, original_node in original_nodes.items():
            formatted_node = formatted_nodes[node_id]
            for key in ("text", "type", "width", "height", "color"):
                self.assertEqual(
                    formatted_node.get(key),
                    original_node.get(key),
                    msg=f"{node_id} changed field {key}",
                )

        self.assertEqual(formatted["edges"], original["edges"])


if __name__ == "__main__":
    unittest.main()
