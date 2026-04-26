#!/usr/bin/env python3
"""Import venture capital timeline rows into the local graph API.

Behavior:
- Reads data/venture_capital_timeline.csv
- Ensures region nodes exist at year 1960 and are connected to "investing in AI"
- Creates VC firm nodes using:
  raw_text = "<firm name>\\n<notes>"
  time_label = inception year, except:
    if inception year < 1960, time_label becomes 1960 and the note is appended
    with the original inception year
- Connects each VC firm node to its region node

This script is idempotent enough for repeated runs:
- It reuses existing region nodes if found
- It reuses existing VC nodes if their raw_text starts with the firm name
- It avoids creating duplicate edges when the same from/to/type already exists
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_CSV = Path("data/venture_capital_timeline.csv")
API_ROOT = "http://127.0.0.1:8000"
REGION_YEAR = 1960
REGION_EDGE_TYPE = "part_of"
VC_EDGE_TYPE = "part_of"
EDGE_WEIGHT = 0.9
EDGE_CONFIDENCE = 0.9
SOURCE = "manual"


def api_url(path: str, token: str | None = None, **query: object) -> str:
    params = {k: v for k, v in query.items() if v is not None}
    if token:
        params["token"] = token
    encoded = urllib.parse.urlencode(params)
    return f"{API_ROOT}{path}" + (f"?{encoded}" if encoded else "")


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


def get_graph_data(workspace_id: int, token: str | None) -> dict:
    url = api_url("/graph-data", token=token, workspace_id=workspace_id)
    return request_json("GET", url)


def post_node(workspace_id: int, token: str | None, raw_text: str, time_label: str, tags: list[str]) -> dict:
    payload = {
        "workspace_id": workspace_id,
        "type": "idea",
        "raw_text": raw_text,
        "time_label": time_label,
        "source": SOURCE,
        "tags": tags,
    }
    url = api_url("/nodes", token=token)
    return request_json("POST", url, payload)


def post_edge(
    workspace_id: int,
    token: str | None,
    from_node_id: int,
    to_node_id: int,
    edge_type: str,
    evidence: str,
) -> dict:
    payload = {
        "workspace_id": workspace_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "type": edge_type,
        "weight": EDGE_WEIGHT,
        "confidence": EDGE_CONFIDENCE,
        "created_by": SOURCE,
        "evidence": evidence,
    }
    url = api_url("/edges", token=token)
    return request_json("POST", url, payload)


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def slug(text: str) -> str:
    return normalize(text).replace("/", "-").replace(" ", "-")


def load_csv_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def node_id(node: dict) -> int | None:
    for key in ("id", "node_id"):
        if key in node:
            return node[key]
    return None


def edge_signature(edge: dict) -> tuple[int, int, str] | None:
    from_id = edge.get("from_node_id")
    to_id = edge.get("to_node_id")
    edge_type = edge.get("type")
    if from_id is None or to_id is None or edge_type is None:
        return None
    return from_id, to_id, edge_type


def find_investing_node(nodes: list[dict]) -> dict:
    candidates = []
    for node in nodes:
        raw_text = node.get("raw_text", "")
        text = normalize(raw_text.splitlines()[0] if raw_text else "")
        if text == "investing in ai":
            return node
        if "investing in ai" in text:
            candidates.append(node)
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError('Could not uniquely find existing node "investing in AI".')


def find_region_node(nodes: list[dict], region: str) -> dict | None:
    target = normalize(region)
    for node in nodes:
        raw_text = node.get("raw_text", "")
        first_line = raw_text.splitlines()[0] if raw_text else ""
        if normalize(first_line) == target:
            return node
    return None


def find_vc_node(nodes: list[dict], firm: str) -> dict | None:
    target = normalize(firm)
    for node in nodes:
        raw_text = node.get("raw_text", "")
        first_line = raw_text.splitlines()[0] if raw_text else ""
        if normalize(first_line) == target:
            return node
    return None


def ensure_edge(
    existing_edges: set[tuple[int, int, str]],
    workspace_id: int,
    token: str | None,
    from_node_id: int,
    to_node_id: int,
    edge_type: str,
    evidence: str,
) -> None:
    signature = (from_node_id, to_node_id, edge_type)
    if signature in existing_edges:
        return
    post_edge(workspace_id, token, from_node_id, to_node_id, edge_type, evidence)
    existing_edges.add(signature)


def build_vc_raw_text(firm: str, note: str, inception_year: int) -> tuple[str, str]:
    time_label = str(inception_year)
    note_text = (note or "").strip()
    if inception_year < REGION_YEAR:
        time_label = str(REGION_YEAR)
        extra = f"Original inception year: {inception_year}."
        note_text = f"{note_text} {extra}".strip() if note_text else extra
    raw_text = f"{firm}\n{note_text}" if note_text else firm
    return raw_text, time_label


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-id", type=int, default=3)
    parser.add_argument("--token", default="qo9BQc50y9dM7W5myCbrMEl2a8Ym_EpQ")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()

    rows = load_csv_rows(args.csv)
    firm_rows = [row for row in rows if row.get("event_type") == "firm_inception"]
    if not firm_rows:
        raise RuntimeError("No firm_inception rows found in CSV.")

    try:
        graph = get_graph_data(args.workspace_id, args.token)
    except urllib.error.URLError as exc:
        print(f"Could not reach graph API at {API_ROOT}: {exc}", file=sys.stderr)
        return 1

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    existing_edges = {sig for edge in edges if (sig := edge_signature(edge))}

    investing_node = find_investing_node(nodes)
    investing_node_id = node_id(investing_node)
    if investing_node_id is None:
        raise RuntimeError('The existing "investing in AI" node is missing an id.')

    region_ids: dict[str, int] = {}
    created_regions = 0
    created_vcs = 0
    created_edges = 0

    for region in sorted({row["region"] for row in firm_rows}):
        region_node = find_region_node(nodes, region)
        if region_node is None:
            created = post_node(
                args.workspace_id,
                args.token,
                raw_text=region,
                time_label=str(REGION_YEAR),
                tags=["investing-in-ai", "venture-capital", "region", slug(region)],
            )
            nodes.append(created)
            region_node = created
            created_regions += 1

        region_node_id = node_id(region_node)
        if region_node_id is None:
            raise RuntimeError(f"Region node for {region} is missing an id.")
        region_ids[region] = region_node_id

        before = len(existing_edges)
        ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            region_node_id,
            investing_node_id,
            REGION_EDGE_TYPE,
            f'Region "{region}" is part of the investing in AI branch.',
        )
        created_edges += len(existing_edges) - before

    for row in firm_rows:
        firm = row["firm"].strip()
        region = row["region"].strip()
        notes = row.get("notes", "").strip()
        inception_year = int(row["firm_inception_year"])

        vc_node = find_vc_node(nodes, firm)
        if vc_node is None:
            raw_text, time_label = build_vc_raw_text(firm, notes, inception_year)
            created = post_node(
                args.workspace_id,
                args.token,
                raw_text=raw_text,
                time_label=time_label,
                tags=["investing-in-ai", "venture-capital", "vc-firm", slug(region), slug(firm)],
            )
            nodes.append(created)
            vc_node = created
            created_vcs += 1

        vc_node_id = node_id(vc_node)
        if vc_node_id is None:
            raise RuntimeError(f"VC node for {firm} is missing an id.")

        before = len(existing_edges)
        ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            vc_node_id,
            region_ids[region],
            VC_EDGE_TYPE,
            f'{firm} is part of the {region} venture capital region.',
        )
        created_edges += len(existing_edges) - before

    print(
        json.dumps(
            {
                "workspace_id": args.workspace_id,
                "regions_created": created_regions,
                "vc_nodes_created": created_vcs,
                "edges_created": created_edges,
                "region_count": len(region_ids),
                "vc_firm_count": len(firm_rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
