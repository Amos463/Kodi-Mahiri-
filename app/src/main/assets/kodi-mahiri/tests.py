"""Majaribio ya kiotomatiki: python3 tests.py"""
import os, tempfile, datetime as dt
os.environ.pop("ANTHROPIC_API_KEY", None)
import engine, nlu, server
from transaction_intelligence import make_demo_transactions, summarize_demo_transactions
from ledger import Ledger

def t_numbers():
    c = {"elfu themanini": 80000, "laki moja na nusu": 150000, "elfu hamsini na mia tano": 50500, "milioni mbili": 2000000, "80 elfu": 80000, "80,000": 80000, "laki mbili": 200000}
    for k, v in c.items(): assert nlu.amount(nlu.toks(k), k) == v, (k, nlu.amount(nlu.toks(k), k))
def t_tax():
    p = engine.presumptive
    assert p(3e6) == 0 and p(5e6) == 100000 and p(5e6, True) == 30000 and p(9e6) == 250000 and p(9e6, True) == 150000 and p(20e6) == 800000 and p(250e6) is None
def t_ledger():
    L = Ledger(tempfile.mktemp()); L.add({"tax_annual": 100000}); L.add({"tax_annual": 200000})
    assert L.verify() == (True, None); L.tamper(); assert L.verify() == (False, 1)
def t_underdeclare():
    sl = dict(sector="duka", region="Iringa", district="Mafinga", daily_sales=20000, tin="116606488")
    r = engine.assess(sl, True, dt.date(2026, 11, 6)); assert r["status"] == "HATARI" and r["tax_annual"] == engine.presumptive(r["declared_annual"]) and r["assessed_annual"] == r["declared_annual"]
    r2 = engine.assess(sl, False, dt.date(2026, 11, 6)); assert r2["status"] == "SAWA" and r2["ratio"] is None
def t_chat_free_speech():
    server.LEDGER = Ledger(tempfile.mktemp()); sid = "t1"
    r = server.chat(sid, "")
    assert "Karibu" in r["reply"]
    r = server.chat(sid, "Niko Mafinga Iringa, nauza duka la vyakula kama elfu thelathini kwa siku"); assert r["stage"] == "collect" and "TIN" in r["reply"], r
    r = server.chat(sid, "TIN yangu ni 116606488"); assert r["stage"] == "confirm", r
    r = server.chat(sid, "ndiyo"); assert r["stage"] == "consent"
    r = server.chat(sid, "ndiyo naruhusu"); assert r["stage"] == "done" and r["result"]["status"] in ("KAGUA", "HATARI") and r["result"]["control"].startswith("KM-DEMO-"), r
def t_demo_data():
    sl = dict(sector="duka", region="Iringa", district="Mafinga", daily_sales=80000, tin="116606488")
    r = engine.assess(sl, True, dt.date(2026, 11, 6))
    assert r["data_mode"] == "SIMULATED_DEMO"
    assert r["evidence"]["source"] == "SIMULATED_DEMO"
    assert r["evidence"]["business_lipa_namba"].startswith("LIPA-DEMO-")
    assert r["assessed_annual"] == r["declared_annual"]
def t_demo_appeal():
    server.APPEALS_FILE = tempfile.mktemp()
    item = server.add_demo_appeal("KM-DEMO-123", "Taarifa ya mauzo haijajumuisha rejesho.")
    assert item["data_mode"] == "SIMULATED_DEMO" and item["status"] == "IMEPOKELEWA_DEMO"
    assert server.read_appeals()[0]["id"] == item["id"]
def t_transaction_intelligence():
    rows = make_demo_transactions("test", "LIPA-DEMO-123456", 30)
    result = summarize_demo_transactions(rows)
    assert result["source"] == "SIMULATED_DEMO" and result["count"] == 30
    assert all(x["business_number"] == "LIPA-DEMO-123456" for x in rows if x["source"] == "LIPA_NAMBA_TILL_PAYBILL")
    assert all(x["demo"] for x in result["transactions"])
def t_ussd():
    server.LEDGER = Ledger(tempfile.mktemp()); sid = "u1"; r = server.ussd(sid, "")
    assert "Arusha" in r["msg"]
    for x, key in [("4", "Wilaya"), ("5", "Aina"), ("1", "Mauzo"), ("80000", "TIN"), ("116606488", "HAKIKI")]: r = server.ussd(sid, x); assert key in r["msg"], (x, r)
    r = server.ussd(sid, "1"); assert r.get("end") and "Rejea DEMO" in r["msg"] and "KM-DEMO-" in r["msg"]

def t_reconciliation_is_review_only():
    sl = dict(sector="duka", region="Iringa", district="Mafinga", daily_sales=20000, tin="116606488")
    r = engine.assess(sl, True, dt.date(2026, 11, 6))
    assert r["evidence_annual"] == r["lipa_annual"]  # TIN purchases are corroborative, not turnover
    if r["ratio"] > 1.3:
        assert r["review_required"] and r["proposed_assessed_annual"] == r["evidence_annual"]
        assert r["assessed_annual"] == r["declared_annual"]
        assert r["tax_annual"] == engine.presumptive(r["declared_annual"])

def t_officer_dashboard_and_decisions():
    from officer import dashboard, decide
    old = __import__('officer').DECISIONS_FILE
    __import__('officer').DECISIONS_FILE = tempfile.mktemp()
    rec = {"id": "R1", "body": {"declared_annual": 100, "evidence_annual": 200, "tax_annual": 0,
           "review_required": True, "proposed_assessed_annual": 200, "proposed_tax_annual": 0, "status": "KAGUA"}}
    d = dashboard([rec], [])
    assert d["paid"] == 0 and d["unverified"] == 1 and d["review"] == 1
    item = decide("R1", "REQUEST_INFO", "Eleza tofauti")
    assert item["legal_effect"] == "NONE" and item["data_mode"] == "SIMULATED_DEMO"
    __import__('officer').DECISIONS_FILE = old

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("t_"): f(); print("OK ", n)
