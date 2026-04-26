#!/usr/bin/env python3

from __future__ import annotations

import json
import urllib.parse
import urllib.request


API_ROOT = "http://127.0.0.1:8000"
WORKSPACE_ID = 3
TOKEN = "qo9BQc50y9dM7W5myCbrMEl2a8Ym_EpQ"
EDGE_TYPE = "part_of"

SUBBRANCHES = [
    (
        "energy",
        "data centre power demands, nuclear revival, solar farms for compute",
    ),
    (
        "water",
        "cooling infrastructure, water consumption of large training runs",
    ),
    (
        "real estate",
        "hyperscale data centre construction, land acquisition",
    ),
    (
        "annotation manpower",
        "the human labellers behind every model. Scale AI, Remotasks",
    ),
    (
        "RLHF workforce",
        "contractors in Kenya, Philippines, India doing feedback work",
    ),
    (
        "rare earth & supply chain",
        "minerals for chips, geopolitics of hardware",
    ),
]


def api_url(path: str, **query: object) -> str:
    params = {k: v for k, v in query.items() if v is not None}
    params["token"] = TOKEN
    return f"{API_ROOT}{path}?{urllib.parse.urlencode(params)}"


def request_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body) if body else {}


def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def slug(text: str) -> str:
    return normalize(text).replace("&", "and").replace("/", "-").replace(" ", "-")


def node_id(node: dict) -> int | None:
    return node.get("id") or node.get("node_id")


def first_line(node: dict) -> str:
    raw = node.get("raw_text") or ""
    return raw.splitlines()[0] if raw else ""


def has_tag(node: dict, target: str) -> bool:
    return target in (node.get("tags") or [])


def find_node(nodes: list[dict], name: str, required_tags: list[str] | None = None) -> dict | None:
    wanted = normalize(name)
    for node in nodes:
        if normalize(first_line(node)) != wanted:
            continue
        if required_tags and not all(has_tag(node, tag) for tag in required_tags):
            continue
        return node
    return None


def edge_sig(edge: dict) -> tuple[int, int, str] | None:
    if edge.get("from_node_id") is None or edge.get("to_node_id") is None or edge.get("type") is None:
        return None
    return edge["from_node_id"], edge["to_node_id"], edge["type"]


def main() -> int:
    graph = request_json("GET", api_url("/graph-data", workspace_id=WORKSPACE_ID))
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    edge_set = {sig for edge in edges if (sig := edge_sig(edge))}

    fueling = find_node(nodes, "fueling AI")
    if fueling is None:
        raise RuntimeError('Could not find existing "fueling AI" node.')
    fueling_id = node_id(fueling)
    if fueling_id is None:
        raise RuntimeError('"fueling AI" node has no id.')

    created_nodes = 0
    created_edges = 0

    for name, note in SUBBRANCHES:
        tags = ["fueling-ai", "sub-branch", slug(name)]
        node = find_node(nodes, name, tags)
        if node is None:
            node = request_json(
                "POST",
                api_url("/nodes"),
                {
                    "workspace_id": WORKSPACE_ID,
                    "type": "idea",
                    "raw_text": f"{name}\n{note}",
                    "time_label": "1960",
                    "source": "manual",
                    "tags": tags,
                },
            )
            nodes.append(node)
            created_nodes += 1

        sub_id = node_id(node)
        if sub_id is None:
            raise RuntimeError(f'Node "{name}" has no id.')

        sig = (sub_id, fueling_id, EDGE_TYPE)
        if sig not in edge_set:
            request_json(
                "POST",
                api_url("/edges"),
                {
                    "workspace_id": WORKSPACE_ID,
                    "from_node_id": sub_id,
                    "to_node_id": fueling_id,
                    "type": EDGE_TYPE,
                    "weight": 0.9,
                    "confidence": 0.9,
                    "created_by": "manual",
                    "evidence": f'{name} is part of the fueling AI branch.',
                },
            )
            edge_set.add(sig)
            created_edges += 1

    print(json.dumps({"created_nodes": created_nodes, "created_edges": created_edges}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
