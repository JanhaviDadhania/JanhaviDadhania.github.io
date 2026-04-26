#!/usr/bin/env python3
"""Import investing-in-AI branch CSVs into the local graph API.

Hierarchy created:
- sub_branch -> investing in AI
- region -> sub_branch
- category -> region       (only when entity_category == "category")
- entity -> region         (default)
- entity -> category       (for Wall Street non-category entities)

Rules:
- Reuse existing region nodes by name across branches
- Keep branch/entity nodes separate by tags, so names like NVIDIA can exist in
  both `corporate bets` and `Wall Street`
- For nodes where time is not meaningfully applicable, use 1960
- If an inception year is earlier than 1960, clamp the node time to 1960 and
  append the original inception year into the note
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path


API_ROOT = "http://127.0.0.1:8000"
SOURCE = "manual"
EDGE_TYPE = "part_of"
EDGE_WEIGHT = 0.9
EDGE_CONFIDENCE = 0.9
STACK_YEAR = 1960

DEFAULT_CSVS = [
    Path("data/corporate_bets.csv"),
    Path("data/sovereign_wealth.csv"),
    Path("data/wall_street.csv"),
    Path("data/government_funding.csv"),
    Path("data/startup_ecosystem.csv"),
]


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def slug(text: str) -> str:
    return normalize(text).replace("/", "-").replace("&", "and").replace(" ", "-")


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
    return request_json("GET", api_url("/graph-data", token=token, workspace_id=workspace_id))


def post_node(workspace_id: int, token: str | None, raw_text: str, time_label: str, tags: list[str]) -> dict:
    payload = {
        "workspace_id": workspace_id,
        "type": "idea",
        "raw_text": raw_text,
        "time_label": time_label,
        "source": SOURCE,
        "tags": tags,
    }
    return request_json("POST", api_url("/nodes", token=token), payload)


def post_edge(
    workspace_id: int,
    token: str | None,
    from_node_id: int,
    to_node_id: int,
    evidence: str,
) -> dict:
    payload = {
        "workspace_id": workspace_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "type": EDGE_TYPE,
        "weight": EDGE_WEIGHT,
        "confidence": EDGE_CONFIDENCE,
        "created_by": SOURCE,
        "evidence": evidence,
    }
    return request_json("POST", api_url("/edges", token=token), payload)


def load_rows(csv_paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in csv_paths:
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def node_id(node: dict) -> int | None:
    return node.get("id") or node.get("node_id")


def edge_signature(edge: dict) -> tuple[int, int, str] | None:
    if edge.get("from_node_id") is None or edge.get("to_node_id") is None or edge.get("type") is None:
        return None
    return edge["from_node_id"], edge["to_node_id"], edge["type"]


def first_line(node: dict) -> str:
    return (node.get("raw_text") or "").splitlines()[0] if node.get("raw_text") else ""


def has_tag(node: dict, target: str) -> bool:
    return target in (node.get("tags") or [])


def find_investing_node(nodes: list[dict]) -> dict:
    for node in nodes:
        if normalize(first_line(node)) == "investing in ai":
            return node
    raise RuntimeError('Could not find the existing "investing in AI" node.')


def find_region_node(nodes: list[dict], region: str) -> dict | None:
    wanted = normalize(region)
    for node in nodes:
        if normalize(first_line(node)) == wanted:
            return node
    return None


def find_tagged_node(nodes: list[dict], name: str, required_tags: list[str]) -> dict | None:
    wanted = normalize(name)
    for node in nodes:
        if normalize(first_line(node)) != wanted:
            continue
        if all(has_tag(node, tag) for tag in required_tags):
            return node
    return None


def build_raw_text(name: str, note: str, inception_year: int | None, stack_if_old: bool = True) -> tuple[str, str]:
    note_text = (note or "").strip()
    if inception_year is None:
        year = STACK_YEAR
    else:
        year = inception_year
    if stack_if_old and year < STACK_YEAR:
        extra = f"Original inception year: {year}."
        note_text = f"{note_text} {extra}".strip() if note_text else extra
        year = STACK_YEAR
    raw_text = f"{name}\n{note_text}" if note_text else name
    return raw_text, str(year)


def ensure_edge(
    existing_edges: set[tuple[int, int, str]],
    workspace_id: int,
    token: str | None,
    from_node_id: int,
    to_node_id: int,
    evidence: str,
) -> bool:
    signature = (from_node_id, to_node_id, EDGE_TYPE)
    if signature in existing_edges:
        return False
    post_edge(workspace_id, token, from_node_id, to_node_id, evidence)
    existing_edges.add(signature)
    return True


def unique_entity_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["sub_branch"], row["region"], row["entity_category"], row["entity"])
        grouped[key].append(row)

    output: list[dict] = []
    for key in sorted(grouped):
        variants = grouped[key]

        def priority(row: dict) -> tuple[int, int]:
            event = row.get("event_type", "")
            year = int(row["year"])
            if event in {"entity_inception", "category_inception"}:
                return (0, year)
            return (1, year)

        chosen = sorted(variants, key=priority)[0].copy()
        output.append(chosen)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-id", type=int, default=3)
    parser.add_argument("--token", default="qo9BQc50y9dM7W5myCbrMEl2a8Ym_EpQ")
    parser.add_argument("--csv", action="append", type=Path, dest="csvs")
    args = parser.parse_args()

    csv_paths = args.csvs or DEFAULT_CSVS
    rows = load_rows(csv_paths)
    entity_rows = unique_entity_rows(rows)

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
        raise RuntimeError('"investing in AI" node is missing an id.')

    created_sub_branches = 0
    created_regions = 0
    created_categories = 0
    created_entities = 0
    created_edges = 0

    sub_branch_ids: dict[str, int] = {}
    region_ids: dict[str, int] = {}
    category_ids: dict[tuple[str, str, str], int] = {}

    sub_branches = sorted({row["sub_branch"] for row in entity_rows})
    for sub_branch in sub_branches:
        required_tags = ["investing-in-ai", "sub-branch", slug(sub_branch)]
        node = find_tagged_node(nodes, sub_branch, required_tags)
        if node is None:
            created = post_node(
                args.workspace_id,
                args.token,
                raw_text=sub_branch,
                time_label=str(STACK_YEAR),
                tags=required_tags,
            )
            nodes.append(created)
            node = created
            created_sub_branches += 1
        sub_branch_id = node_id(node)
        if sub_branch_id is None:
            raise RuntimeError(f"Sub-branch node for {sub_branch} is missing an id.")
        sub_branch_ids[sub_branch] = sub_branch_id
        if ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            sub_branch_id,
            investing_node_id,
            f'{sub_branch} is part of the investing in AI branch.',
        ):
            created_edges += 1

    for region in sorted({row["region"] for row in entity_rows}):
        node = find_region_node(nodes, region)
        if node is None:
            created = post_node(
                args.workspace_id,
                args.token,
                raw_text=region,
                time_label=str(STACK_YEAR),
                tags=["investing-in-ai", "region", slug(region)],
            )
            nodes.append(created)
            node = created
            created_regions += 1
        region_id = node_id(node)
        if region_id is None:
            raise RuntimeError(f"Region node for {region} is missing an id.")
        region_ids[region] = region_id

    category_rows = [row for row in entity_rows if row["entity_category"] == "category"]
    non_category_rows = [row for row in entity_rows if row["entity_category"] != "category"]

    for row in category_rows:
        sub_branch = row["sub_branch"]
        region = row["region"]
        entity_category = row["entity_category"]
        entity = row["entity"]
        notes = row.get("notes", "")
        inception_year = int(row["entity_inception_year"]) if row.get("entity_inception_year") else None

        sub_branch_id = sub_branch_ids[sub_branch]
        region_id = region_ids[region]

        if ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            region_id,
            sub_branch_id,
            f'{region} is part of the {sub_branch} branch.',
        ):
            created_edges += 1

        required_tags = ["investing-in-ai", "category", slug(sub_branch), slug(region), slug(entity)]
        node = find_tagged_node(nodes, entity, required_tags)
        if node is None:
            raw_text, time_label = build_raw_text(entity, notes, inception_year, stack_if_old=False)
            created = post_node(
                args.workspace_id,
                args.token,
                raw_text=raw_text,
                time_label=time_label,
                tags=required_tags,
            )
            nodes.append(created)
            node = created
            created_categories += 1
        category_id = node_id(node)
        if category_id is None:
            raise RuntimeError(f"Category node for {entity} is missing an id.")
        category_ids[(sub_branch, region, entity)] = category_id
        if ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            category_id,
            region_id,
            f'{entity} is a category within {region} for the {sub_branch} branch.',
        ):
            created_edges += 1

    for row in non_category_rows:
        sub_branch = row["sub_branch"]
        region = row["region"]
        entity_category = row["entity_category"]
        entity = row["entity"]
        notes = row.get("notes", "")
        inception_year = int(row["entity_inception_year"]) if row.get("entity_inception_year") else None

        sub_branch_id = sub_branch_ids[sub_branch]
        region_id = region_ids[region]

        if ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            region_id,
            sub_branch_id,
            f'{region} is part of the {sub_branch} branch.',
        ):
            created_edges += 1

        required_tags = ["investing-in-ai", "entity", slug(sub_branch), slug(region), slug(entity)]
        node = find_tagged_node(nodes, entity, required_tags)
        if node is None:
            raw_text, time_label = build_raw_text(entity, notes, inception_year, stack_if_old=True)
            created = post_node(
                args.workspace_id,
                args.token,
                raw_text=raw_text,
                time_label=time_label,
                tags=required_tags,
            )
            nodes.append(created)
            node = created
            created_entities += 1
        entity_id = node_id(node)
        if entity_id is None:
            raise RuntimeError(f"Entity node for {entity} is missing an id.")

        if sub_branch == "Wall Street":
            parent_name = {
                "public_equity": "Public equities",
                "ai_etf": "AI ETFs",
                "analyst_house": "Analyst houses",
                "theme_trade": "Theme trades",
            }.get(entity_category)
            if not parent_name:
                raise RuntimeError(f"Unknown Wall Street category mapping for {entity_category}")
            category_id = category_ids[(sub_branch, region, parent_name)]
            evidence = f'{entity} belongs to the {parent_name} category within {region} for Wall Street.'
            parent_id = category_id
        else:
            evidence = f'{entity} belongs to {region} within the {sub_branch} branch.'
            parent_id = region_id

        if ensure_edge(
            existing_edges,
            args.workspace_id,
            args.token,
            entity_id,
            parent_id,
            evidence,
        ):
            created_edges += 1

    print(
        json.dumps(
            {
                "workspace_id": args.workspace_id,
                "csv_count": len(csv_paths),
                "sub_branches_created": created_sub_branches,
                "regions_created": created_regions,
                "categories_created": created_categories,
                "entities_created": created_entities,
                "edges_created": created_edges,
                "sub_branch_count": len(sub_branch_ids),
                "region_count": len(region_ids),
                "entity_count": len(entity_rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
