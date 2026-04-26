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
EDGE_TYPE = "part_of"
STACK_YEAR = 1960

CSV_PATHS = [
    Path("data/mu_foundation_model_labs.csv"),
    Path("data/mu_hardware_chips.csv"),
    Path("data/mu_cloud_infrastructure.csv"),
    Path("data/mu_data.csv"),
    Path("data/mu_tooling_frameworks.csv"),
    Path("data/mu_open_source_models.csv"),
    Path("data/mu_interpretability.csv"),
    Path("data/mu_alignment_safety.csv"),
    Path("data/mu_benchmarking_evaluation.csv"),
    Path("data/mu_ml_theory.csv"),
    Path("data/mu_science_communication.csv"),
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


def unique_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["sub_branch"], row["region"], row["entity"])].append(row)

    out: list[dict] = []
    for key in sorted(grouped):
        variants = grouped[key]
        out.append(sorted(variants, key=lambda r: int(r["year"]))[0].copy())
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
    existing = find_node(nodes, raw_text.splitlines()[0], tags)
    if existing is not None:
        return existing
    node = request_json(
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
    nodes.append(node)
    return node


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
    year = inception_year if inception_year is not None else STACK_YEAR
    if year < STACK_YEAR:
        extra = f"Original inception year: {year}."
        note_text = f"{note_text} {extra}".strip() if note_text else extra
        year = STACK_YEAR
    return (f"{entity}\n{note_text}" if note_text else entity, str(year))


def main() -> int:
    graph = request_json("GET", api_url("/graph-data", workspace_id=WORKSPACE_ID))
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    edge_set = {sig for edge in edges if (sig := edge_sig(edge))}
    rows = unique_rows(load_rows())

    created_regions = 0
    created_entities = 0
    created_edges = 0

    subbranch_ids: dict[str, int] = {}
    region_ids: dict[str, int] = {}

    for subbranch in sorted({row["sub_branch"] for row in rows}):
        node = find_node(nodes, subbranch)
        if node is None:
            raise RuntimeError(f'Missing sub-branch node: {subbranch}')
        sub_id = node_id(node)
        if sub_id is None:
            raise RuntimeError(f'Sub-branch node missing id: {subbranch}')
        subbranch_ids[subbranch] = sub_id

    for region in sorted({row["region"] for row in rows}):
        node = find_node(nodes, region)
        if node is None:
            node = ensure_node(nodes, region, str(STACK_YEAR), ["region", slug(region)])
            created_regions += 1
        rid = node_id(node)
        if rid is None:
            raise RuntimeError(f'Region missing id: {region}')
        region_ids[region] = rid

    for row in rows:
        subbranch = row["sub_branch"]
        region = row["region"]
        entity = row["entity"]
        notes = row.get("notes", "")
        inception = int(row["entity_inception_year"]) if row.get("entity_inception_year") else None

        sub_id = subbranch_ids[subbranch]
        region_id = region_ids[region]

        if ensure_edge(edge_set, region_id, sub_id, f"{region} is part of the {subbranch} branch."):
            created_edges += 1

        tags = ["making-understanding-ai", "entity", slug(subbranch), slug(region), slug(entity)]
        node = find_node(nodes, entity, tags)
        if node is None:
            raw_text, time_label = build_raw_text(entity, notes, inception)
            node = ensure_node(nodes, raw_text, time_label, tags)
            created_entities += 1

        entity_id = node_id(node)
        if entity_id is None:
            raise RuntimeError(f'Entity missing id: {entity}')
        if ensure_edge(edge_set, entity_id, region_id, f"{entity} belongs to {region} within {subbranch}."):
            created_edges += 1

    print(json.dumps({
        "created_regions": created_regions,
        "created_entities": created_entities,
        "created_edges": created_edges,
        "region_count": len(region_ids),
        "entity_count": len(rows),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
