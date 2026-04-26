#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path


API_ROOT = "http://127.0.0.1:8000"
WORKSPACE_ID = 3
TOKEN = "qo9BQc50y9dM7W5myCbrMEl2a8Ym_EpQ"
STACK_YEAR = 1960
EDGE_TYPE = "part_of"

CSV_PATHS = [
    Path("data/fueling_energy.csv"),
    Path("data/fueling_water.csv"),
    Path("data/fueling_real_estate.csv"),
    Path("data/fueling_annotation_manpower.csv"),
    Path("data/fueling_rlhf_workforce.csv"),
    Path("data/fueling_rare_earth_supply_chain.csv"),
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
    return " ".join((text or "").strip().lower().split())


def slug(text: str) -> str:
    return normalize(text).replace("&", "and").replace("/", "-").replace(" ", "-")


def first_line(node: dict) -> str:
    raw = node.get("raw_text") or ""
    return raw.splitlines()[0] if raw else ""


def node_id(node: dict) -> int | None:
    return node.get("id") or node.get("node_id")


def has_tag(node: dict, target: str) -> bool:
    return target in (node.get("tags") or [])


def edge_sig(edge: dict) -> tuple[int, int, str] | None:
    if edge.get("from_node_id") is None or edge.get("to_node_id") is None or edge.get("type") is None:
        return None
    return edge["from_node_id"], edge["to_node_id"], edge["type"]


def load_rows() -> list[dict]:
    rows: list[dict] = []
    for path in CSV_PATHS:
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def unique_entity_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["sub_branch"], row["region"], row["entity"])
        grouped[key].append(row)

    out: list[dict] = []
    for key in sorted(grouped):
        variants = grouped[key]

        def priority(row: dict) -> tuple[int, int]:
            event = row.get("event_type", "")
            year = int(row["year"])
            return (0 if event == "entity_inception" else 1, year)

        out.append(sorted(variants, key=priority)[0].copy())
    return out


def find_node(nodes: list[dict], name: str, required_tags: list[str] | None = None) -> dict | None:
    wanted = normalize(name)
    for node in nodes:
        if normalize(first_line(node)) != wanted:
            continue
        if required_tags and not all(has_tag(node, tag) for tag in required_tags):
            continue
        return node
    return None


def ensure_node(nodes: list[dict], raw_text: str, time_label: str, tags: list[str]) -> dict:
    name = raw_text.splitlines()[0]
    existing = find_node(nodes, name, tags)
    if existing is not None:
        return existing
    created = request_json(
        "POST",
        api_url("/nodes"),
        {
            "workspace_id": WORKSPACE_ID,
            "type": "idea",
            "raw_text": raw_text,
            "time_label": time_label,
            "source": "manual",
            "tags": tags,
        },
    )
    nodes.append(created)
    return created


def ensure_edge(edge_set: set[tuple[int, int, str]], from_id: int, to_id: int, evidence: str) -> bool:
    sig = (from_id, to_id, EDGE_TYPE)
    if sig in edge_set:
        return False
    request_json(
        "POST",
        api_url("/edges"),
        {
            "workspace_id": WORKSPACE_ID,
            "from_node_id": from_id,
            "to_node_id": to_id,
            "type": EDGE_TYPE,
            "weight": 0.9,
            "confidence": 0.9,
            "created_by": "manual",
            "evidence": evidence,
        },
    )
    edge_set.add(sig)
    return True


def build_raw_text(entity: str, notes: str, inception_year: int | None) -> tuple[str, str]:
    note_text = (notes or "").strip()
    if inception_year is None:
        year = STACK_YEAR
    else:
        year = inception_year
    if year < STACK_YEAR:
        extra = f"Original inception year: {year}."
        note_text = f"{note_text} {extra}".strip() if note_text else extra
        year = STACK_YEAR
    raw_text = f"{entity}\n{note_text}" if note_text else entity
    return raw_text, str(year)


def main() -> int:
    graph = request_json("GET", api_url("/graph-data", workspace_id=WORKSPACE_ID))
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    edge_set = {sig for edge in edges if (sig := edge_sig(edge))}

    fueling_node = find_node(nodes, "fueling AI")
    if fueling_node is None:
        raise RuntimeError('Could not find existing "fueling AI" node.')
    fueling_id = node_id(fueling_node)
    if fueling_id is None:
        raise RuntimeError('"fueling AI" node missing id.')

    rows = unique_entity_rows(load_rows())

    created_regions = 0
    created_entities = 0
    created_edges = 0

    region_ids: dict[str, int] = {}
    subbranch_ids: dict[str, int] = {}

    for subbranch in sorted({row["sub_branch"] for row in rows}):
        node = find_node(nodes, subbranch)
        if node is None:
            raise RuntimeError(f'Expected existing sub-branch node "{subbranch}" not found.')
        subbranch_id = node_id(node)
        if subbranch_id is None:
            raise RuntimeError(f'Sub-branch "{subbranch}" missing id.')
        subbranch_ids[subbranch] = subbranch_id
        if ensure_edge(edge_set, subbranch_id, fueling_id, f"{subbranch} is part of fueling AI."):
            created_edges += 1

    for region in sorted({row["region"] for row in rows}):
        node = find_node(nodes, region)
        if node is None:
            node = ensure_node(
                nodes,
                raw_text=region,
                time_label=str(STACK_YEAR),
                tags=["region", slug(region)],
            )
            created_regions += 1
        region_id = node_id(node)
        if region_id is None:
            raise RuntimeError(f'Region "{region}" missing id.')
        region_ids[region] = region_id

    for row in rows:
        subbranch = row["sub_branch"]
        region = row["region"]
        entity = row["entity"]
        notes = row.get("notes", "")
        inception_year = int(row["entity_inception_year"]) if row.get("entity_inception_year") else None

        subbranch_id = subbranch_ids[subbranch]
        region_id = region_ids[region]

        if ensure_edge(edge_set, region_id, subbranch_id, f"{region} is part of the {subbranch} branch."):
            created_edges += 1

        tags = ["fueling-ai", "entity", slug(subbranch), slug(region), slug(entity)]
        node = find_node(nodes, entity, tags)
        if node is None:
            raw_text, time_label = build_raw_text(entity, notes, inception_year)
            node = ensure_node(nodes, raw_text=raw_text, time_label=time_label, tags=tags)
            created_entities += 1

        entity_id = node_id(node)
        if entity_id is None:
            raise RuntimeError(f'Entity "{entity}" missing id.')
        if ensure_edge(edge_set, entity_id, region_id, f"{entity} belongs to {region} within {subbranch}."):
            created_edges += 1

    print(
        json.dumps(
            {
                "created_regions": created_regions,
                "created_entities": created_entities,
                "created_edges": created_edges,
                "region_count": len(region_ids),
                "entity_count": len(rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
