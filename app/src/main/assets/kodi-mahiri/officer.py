"""Huduma za dashibodi ya afisa kwa prototype. Hakuna mamlaka ya kisheria ya kubadili kodi."""
import json, os, datetime as dt, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
DECISIONS_FILE = os.path.join(HERE, "data", "officer_decisions.json")

def _read():
    try:
        with open(DECISIONS_FILE, encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError): return []

def decide(record_id, decision, note=""):
    if decision not in ("CONFIRM_DECLARED", "PROPOSE_REVIEW", "REQUEST_INFO", "CLOSE_NO_CHANGE"):
        raise ValueError("Uamuzi haujatambuliwa")
    rows = _read()
    item = {"id": "OFF-DEMO-" + uuid.uuid4().hex[:8].upper(), "record_id": str(record_id),
            "decision": decision, "note": str(note)[:1000], "created_at": dt.datetime.now().isoformat(timespec="seconds"),
            "data_mode": "SIMULATED_DEMO", "legal_effect": "NONE"}
    rows.insert(0, item)
    os.makedirs(os.path.dirname(DECISIONS_FILE), exist_ok=True)
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f: json.dump(rows[:2000], f, ensure_ascii=False, indent=2)
    return item

def dashboard(records, appeals):
    rows = []
    for rec in records:
        b = rec.get("body", {})
        rows.append({"record_id": rec.get("id"), "area": f"{b.get('district','')}, {b.get('region','')}",
          "sector": b.get("sector"), "declared_annual": b.get("declared_annual"), "evidence_annual": b.get("evidence_annual"),
          "tax_annual": b.get("tax_annual"), "risk": b.get("risk", 0), "review_required": b.get("review_required", False),
          "payment_status": "HAIJATHIBITISHWA", "tax_status": b.get("status", "SAWA"),
          "proposed_assessed_annual": b.get("proposed_assessed_annual"), "proposed_tax_annual": b.get("proposed_tax_annual")})
    return {"items": rows, "paid": 0, "unverified": len(rows),
            "review": sum(1 for x in rows if x["review_required"]), "appeals": len(appeals),
            "decisions": _read(), "data_mode": "SIMULATED_DEMO",
            "notice": "Hakuna malipo yaliyothibitishwa. Hali ya malipo haitabuniwa; uthibitisho utahitaji callback rasmi ya payment provider."}
