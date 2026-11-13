"""n8n exports: valid connections and local-only backend interactions."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = list((ROOT / "n8n").glob("wbbl-*.json"))

def test_all_workflows_wired_and_local():
    assert len(WORKFLOWS) >= 4
    for path in WORKFLOWS:
        wf = json.loads(path.read_text(encoding="utf-8"))
        names = [n["name"] for n in wf["nodes"]]
        assert len(names) == len(set(names)), path
        assert wf["active"] is False
        for origin, wiring in wf["connections"].items():
            assert origin in names, (path, origin)
            for groups in wiring.values():
                for group in groups:
                    for edge in group:
                        assert edge["node"] in names, (path, edge)
        for n in wf["nodes"]:
            assert n["type"].startswith("n8n-nodes-base")
            if n["type"] == "n8n-nodes-base.httpRequest":
                assert "http://strike-os:8000/api/" in n["parameters"]["url"]
                if n["parameters"].get("method") == "POST":
                    headers = n["parameters"]["headerParameters"]["parameters"]
                    assert any(h["name"] == "Authorization" for h in headers)

def test_automatic_job_generates_and_saves():
    document=json.loads((ROOT/"n8n"/"wbbl-auto-recommendations.json").read_text())
    assert "/generate?teams=3" in json.dumps(document)
    assert "/free/watchlist" in json.dumps(document)
