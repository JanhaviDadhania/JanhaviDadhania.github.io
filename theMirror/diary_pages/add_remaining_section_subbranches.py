#!/usr/bin/env python3

from __future__ import annotations

import json
import urllib.parse
import urllib.request

API_ROOT = "http://127.0.0.1:8000"
WORKSPACE_ID = 3
TOKEN = "qo9BQc50y9dM7W5myCbrMEl2a8Ym_EpQ"
EDGE_TYPE = "part_of"

SECTIONS = {
    "deploying AI": [
        ("AI-native consumer apps", "consumer products built directly on top of frontier models"),
        ("coding tools", "AI systems assisting or automating software development"),
        ("enterprise AI", "copilots and assistants embedded into mainstream enterprise software"),
        ("vertical SaaS", "domain-specific AI companies built around a single profession or workflow"),
        ("agent frameworks", "orchestration systems for autonomous pipelines and workflow automation"),
        ("API layer", "middleware and inference platforms between labs and builders"),
        ("edge AI compute", "running models on-device for latency, privacy, and offline use"),
    ],
    "using AI": [
        ("software engineering", "AI used directly in software development"),
        ("creative writing & journalism", "AI used in writing, reporting, summarizing, and research"),
        ("visual art & design", "AI used in image creation, layout, and creative ideation"),
        ("music & audio", "AI used in sound generation, editing, and voice production"),
        ("film & video", "AI used in video generation, editing, and production workflows"),
        ("medicine", "AI used in diagnosis, drug discovery, genomics, and radiology"),
        ("mathematics", "AI used in theorem proving, problem solving, and research assistance"),
        ("science", "AI used across physics, chemistry, biology, and materials science"),
        ("robotics & physical AI", "AI used in embodied systems interacting with the physical world"),
        ("autonomous driving", "AI used in driving autonomy and navigation"),
        ("space exploration", "AI used in autonomy, planning, and remote sensing for space"),
        ("education", "AI used in tutoring, learning, and educational workflows"),
        ("law", "AI used in legal research, drafting, and case workflows"),
        ("finance & trading", "AI used in market intelligence, forecasting, and trading systems"),
        ("agriculture", "AI used in precision farming, crop management, and agricultural robotics"),
        ("manufacturing", "AI used in industrial engineering, inspection, and process automation"),
        ("language & translation", "AI used for translation and multilingual communication"),
        ("defence & cyber war", "AI used in autonomous weapons, cyber operations, and battlefield intelligence"),
        ("gaming & interactive media", "AI used for NPCs, procedural worlds, and interactive storytelling"),
    ],
    "governing AI": [
        ("national policy", "country-level laws, directives, and state institutions shaping AI"),
        ("supranational", "cross-border and multinational governance frameworks"),
        ("standards bodies", "institutions writing technical and procedural AI standards"),
        ("policy think tanks", "research organizations shaping AI policy discourse"),
        ("international coordination", "summits, declarations, and diplomatic coordination around AI"),
        ("corporate governance", "internal governance systems inside AI companies and large enterprises"),
    ],
    "resisting AI": [
        ("labour & unions", "organized labor resisting harmful AI uses or bargaining over AI adoption"),
        ("artists & copyright", "creative industries resisting unlicensed training and substitution"),
        ("religious & ethical voices", "faith-based and moral critiques of AI development"),
        ("academic critics", "public intellectual and scholarly criticism of AI systems and narratives"),
        ("pause & slowdown movements", "groups explicitly calling to slow or pause frontier AI progress"),
        ("anti-surveillance", "movements resisting facial recognition, biometrics, and monitoring systems"),
        ("environmental", "resistance centered on AI energy, water, and ecological costs"),
    ],
    "second order AI impact": [
        ("psychology", "how AI affects attention, cognition, and mental habits"),
        ("identity", "how AI changes ideas of authorship, personhood, and being human"),
        ("relationships", "AI companions, attachment, and parasocial bonds with systems"),
        ("work & meaning", "how AI reshapes labor, purpose, and daily life"),
        ("culture", "how AI changes authenticity, ownership, and shared creative norms"),
        ("education & childhood", "how growing up with AI changes development and learning"),
        ("inequality", "how AI amplifies gaps in access, skill, and power"),
        ("political", "how AI affects propaganda, trust, and institutions"),
        ("spiritual", "how AI raises questions about consciousness, soul, and meaning"),
    ],
}


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

    created_nodes = 0
    created_edges = 0

    for main_name, subbranches in SECTIONS.items():
        main_node = find_node(nodes, main_name)
        if main_node is None:
            raise RuntimeError(f"Missing main node: {main_name}")
        main_id = node_id(main_node)
        if main_id is None:
            raise RuntimeError(f"Main node missing id: {main_name}")

        for sub_name, note in subbranches:
            tags = [slug(main_name), "sub-branch", slug(sub_name)]
            node = find_node(nodes, sub_name, tags)
            if node is None:
                node = request_json(
                    "POST",
                    api_url("/nodes"),
                    {
                        "workspace_id": WORKSPACE_ID,
                        "type": "idea",
                        "raw_text": f"{sub_name}\n{note}",
                        "time_label": "1960",
                        "source": "manual",
                        "tags": tags,
                    },
                )
                nodes.append(node)
                created_nodes += 1

            sub_id = node_id(node)
            if sub_id is None:
                raise RuntimeError(f"Node has no id: {sub_name}")
            sig = (sub_id, main_id, EDGE_TYPE)
            if sig not in edge_set:
                request_json(
                    "POST",
                    api_url("/edges"),
                    {
                        "workspace_id": WORKSPACE_ID,
                        "from_node_id": sub_id,
                        "to_node_id": main_id,
                        "type": EDGE_TYPE,
                        "weight": 0.9,
                        "confidence": 0.9,
                        "created_by": "manual",
                        "evidence": f"{sub_name} is part of the {main_name} branch.",
                    },
                )
                edge_set.add(sig)
                created_edges += 1

    print(json.dumps({"created_nodes": created_nodes, "created_edges": created_edges}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
