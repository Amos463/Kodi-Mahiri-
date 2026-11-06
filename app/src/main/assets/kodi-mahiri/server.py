"""Kodi Mahiri: seva ya majaribio (Python stdlib, haihitaji kusakinisha chochote). Run: python3 server.py"""
import json, os, re, hashlib, uuid, datetime as dt
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import engine, nlu, officer
from geo import REGIONS
from ledger import Ledger

HERE = os.environ.get("KODI_MAHIRI_HOME", os.path.dirname(os.path.abspath(__file__)))
LEDGER = Ledger(os.path.join(HERE, "data", "ledger.json"))
APPEALS_FILE = os.path.join(HERE, "data", "appeals.json")
os.makedirs(os.path.dirname(APPEALS_FILE), exist_ok=True)
if not os.path.exists(APPEALS_FILE):
    with open(APPEALS_FILE, "w", encoding="utf-8") as _f: json.dump([], _f)

def read_appeals():
    try:
        with open(APPEALS_FILE, encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError): return []

def add_demo_appeal(reference, message):
    rows = read_appeals()
    item = {"id": "AP-DEMO-" + uuid.uuid4().hex[:8].upper(),
            "reference": reference[:40], "message": message[:1000],
            "status": "IMEPOKELEWA_DEMO", "created_at": dt.datetime.now().isoformat(timespec="seconds"),
            "data_mode": "SIMULATED_DEMO"}
    rows.insert(0, item)
    with open(APPEALS_FILE, "w", encoding="utf-8") as f: json.dump(rows[:1000], f, ensure_ascii=False, indent=2)
    return item
SESS = {}
ORDER = ["region", "district", "sector", "daily_sales", "tin"]
ASK = {"region": "uko mkoa gani", "district": "wilaya gani", "sector": "unafanya biashara gani", "daily_sales": "mauzo yako ni shilingi ngapi kwa siku",
       "tin": "namba yako ya TIN ni ipi, tarakimu tisa, au sema sina TIN"}
fmt = lambda n: f"{int(n):,}"

def summary(sl):
    s = engine.SECTOR[sl["sector"]]["name"]; tin = "bila TIN" if sl["tin"] == "NONE" else "TIN " + sl["tin"]
    return f"{sl['district']}, {sl['region']}; {s}; mauzo TZS {fmt(sl['daily_sales'])} kwa siku; {tin}"

def ask_text(sl, got):
    miss = [k for k in ORDER if k not in sl]
    pre = ("Nimekupata. " if got else "Samahani, sijaelewa vizuri. ") if sl or got else ""
    if miss == ["district"] or (miss and miss[0] == "district" and "region" in sl):
        ds = REGIONS[sl["region"]]; return pre + f"{sl['region']} ina wilaya hizi: {', '.join(ds)}. Uko wilaya ipi?"
    want = miss[:2]
    return pre + "Niambie " + " na ".join(ASK[k] for k in want) + "?"

def finalize(sess, consent):
    sl = sess["slots"]; res = engine.assess(sl, consent)
    tin_m = "----" if sl["tin"] == "NONE" else "*****" + sl["tin"][-4:]
    body = {"tin": tin_m, "region": sl["region"], "district": sl["district"], "sector": res["sector"], "declared_annual": res["declared_annual"],
            "evidence_annual": res["evidence_annual"], "assessed_annual": res["assessed_annual"], "tax_annual": res["tax_annual"], "status": res["status"], "risk": res.get("risk", 0), "review_required": res.get("review_required", False), "proposed_assessed_annual": res.get("proposed_assessed_annual"), "proposed_tax_annual": res.get("proposed_tax_annual"), "payment_status": "HAIJATHIBITISHWA"}
    rec = LEDGER.add(body); ctrl = "KM-DEMO-" + hashlib.sha256(rec["hash"].encode()).hexdigest()[:8].upper()
    res.update(control=ctrl, record_id=rec["id"], hash=rec["hash"])
    if res["status"] == "SELF-ASSESSMENT":
        say = "Biashara yako ya kitaalamu haiko kwenye kodi ya makadirio. Tafadhali wasiliana na TRA kwa self-assessment."
    else:
        say = f"Kodi yako ya makadirio ni shilingi {fmt(res['tax_annual'])} kwa mwaka, sawa na {fmt(res['tax_quarter'])} kwa robo mwaka. Rejea ya majaribio (si Control Number ya TRA): {ctrl}. Ujumbe wa SMS wa mfano umeandaliwa."
        if res["status"] in ("KAGUA", "HATARI"): say += " Data za mfano zimeonyesha tofauti na mauzo uliyotaja. Hii si ushahidi halisi wala uamuzi wa kodi."
        if res["tax_annual"] == 0: say = "Mauzo yako ya mwaka hayazidi shilingi milioni nne, kwa hiyo huna kodi. Jisajili upate TIN. Asante."
    res["sms"] = f"KODI MAHIRI DEMO: mfano wa hesabu TZS {fmt(res['tax_annual'])}/mwaka. Rejea ya demo: {ctrl}. Si Control Number ya TRA."
    return say, res

def chat(sid, text):
    sess = SESS.setdefault(sid, {"slots": {}, "stage": "collect", "hist": []}); text = (text or "").strip()
    sl = sess["slots"]
    if not text and not sl:
        return {"reply": "Karibu KODI MAHIRI (prototype ya majaribio). Niambie kwa kifupi: uko mkoa na wilaya gani, unafanya biashara gani, na mauzo yako ni shilingi ngapi kwa siku? Unaweza kujibu yote kwa pamoja.", "stage": "collect", "slots": sl}
    r = nlu.rules(text); st = sess["stage"]
    if st == "confirm":
        if r["_yes"]: sess["stage"] = "consent"; return {"reply": "Asante. Je, unakubali tuonyeshe UIGAJI WA DATA ZA MFANO za miamala ya Lipa Namba ya biashara (Till/Paybill) na manunuzi kwa ajili ya onyesho? Sema ndiyo au hapana.", "stage": "consent", "slots": sl}
        sess["stage"] = "collect"; st = "collect"
    elif st == "consent":
        if r["_yes"] or r["_no"]:
            say, res = finalize(sess, r["_yes"]); sess["stage"] = "done"
            return {"reply": say, "stage": "done", "slots": sl, "result": res, "sms": res["sms"]}
        return {"reply": "Naomba ujibu ndiyo au hapana: unakubali ulinganisho wa DATA ZA MFANO za Lipa Namba ya biashara na manunuzi?", "stage": "consent", "slots": sl}
    if st == "done": sess.update(slots={}, stage="collect", hist=[]); sl = sess["slots"]
    found = nlu.valid(r); missing = [k for k in ORDER if k not in sl]
    L = nlu.llm(text, sl, missing, sess["hist"]); lrep = None
    if L:
        lv = nlu.valid(L.get("slots") or {}); lrep = L.get("reply")
        for k, v in lv.items(): found.setdefault(k, v)
    if "region" in found and found["region"] != sl.get("region") and "district" not in found: sl.pop("district", None)
    sl.update(found)
    sess["hist"] += [{"role": "user", "content": text}]
    miss = [k for k in ORDER if k not in sl]
    if not miss:
        sess["stage"] = "confirm"; rep = "Nimepata: " + summary(sl) + ". Je, ni sahihi? Sema ndiyo au hapana."
    else:
        rep = lrep if (lrep and L and found) else ask_text(sl, found)
    sess["hist"] += [{"role": "assistant", "content": rep}]
    return {"reply": rep, "stage": sess["stage"], "slots": sl, "engine": "llm" if L else "rules"}

# ---------- USSD (*150#): menyu zenye kurasa; hatua zinatunzwa kwenye seva ----------
SECT = [(s["id"], s["name"]) for s in engine.SECTORS]
def page(items, p, title):
    n = 5; chunk = items[p * n:(p + 1) * n]; t = title + "\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(chunk))
    return t + ("\n9. Mbele" if (p + 1) * n < len(items) else "") + ("\n8. Nyuma" if p else "")

def ussd(sid, text):
    u = SESS.setdefault("u" + sid, {"step": "region", "p": 0, "sl": {}}); text = (text or "").strip(); sl = u["sl"]
    def pick(items):
        if text == "9": u["p"] += 1; return "more"
        if text == "8": u["p"] = max(0, u["p"] - 1); return "more"
        if text.isdigit() and 1 <= int(text) <= 5 and u["p"] * 5 + int(text) <= len(items): return items[u["p"] * 5 + int(text) - 1]
        return None
    s = u["step"]
    if s == "region":
        items = list(REGIONS)
        if text:
            c = pick(items)
            if c and c != "more": sl["region"] = c; u.update(step="district", p=0); return {"msg": page(REGIONS[c], 0, f"Wilaya ya {c}:")}
        return {"msg": page(items, u["p"], "KODI MAHIRI\nChagua MKOA:")}
    if s == "district":
        items = REGIONS[sl["region"]]; c = pick(items)
        if c and c != "more": sl["district"] = c; u.update(step="sector", p=0); return {"msg": page([n for _, n in SECT], 0, "Aina ya biashara:")}
        return {"msg": page(items, u["p"], f"Wilaya ya {sl['region']}:")}
    if s == "sector":
        names = [n for _, n in SECT]; c = pick(names)
        if c and c != "more": sl["sector"] = SECT[names.index(c)][0]; u["step"] = "sales"; return {"msg": "Mauzo yako kwa SIKU ni TSh ngapi?\n(andika namba, mfano 80000)"}
        return {"msg": page(names, u["p"], "Aina ya biashara:")}
    if s == "sales":
        if text.isdigit() and 1000 <= int(text) <= 50_000_000: sl["daily_sales"] = int(text); u["step"] = "tin"; return {"msg": "Namba ya TIN (tarakimu 9)\nau andika 0 kama huna."}
        return {"msg": "Namba si sahihi. Andika mauzo ya siku, mfano 80000"}
    if s == "tin":
        if text == "0": sl["tin"] = "NONE"
        elif re.fullmatch(r"\d{9}", text): sl["tin"] = text
        else: return {"msg": "TIN lazima iwe tarakimu 9, au 0 kama huna."}
        u["step"] = "confirm"; return {"msg": "HAKIKI:\n" + summary(sl) + "\n1. Ndiyo, nakubali ulinganisho na Lipa Namba\n2. Hapana, anza upya"}
    if s == "confirm":
        if text == "1":
            sess = {"slots": sl}; say, res = finalize(sess, True); u["step"] = "done"
            return {"msg": f"IMEKAMILIKA (DEMO)\nKodi ya mfano: TSh {fmt(res['tax_annual'])}/mwaka\nRejea DEMO: {res['control']}\nHii si Control Number ya TRA. SMS ya mfano imeandaliwa.", "end": True, "sms": res["sms"], "result": res}
        if text == "2":
            sess = {"slots": sl}; say, res = finalize(sess, False); u["step"] = "done"
            return {"msg": f"IMEKAMILIKA (DEMO)\nKodi ya mfano: TSh {fmt(res['tax_annual'])}/mwaka\nRejea DEMO: {res['control']}\nHii si Control Number ya TRA.", "end": True, "sms": res["sms"], "result": res}
        return {"msg": "Chagua 1 au 2."}
    return {"msg": "Mwisho.", "end": True}

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj, ctype="application/json"):
        b = obj if isinstance(obj, bytes) else json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/api/geo": return self._send(200, REGIONS)
        if p == "/api/sectors": return self._send(200, [{k: s[k] for k in ("id", "name", "margin", "digital", "season", "days", "purch", "excluded", "note")} for s in engine.SECTORS])
        if p == "/api/ledger": ok, bad = LEDGER.verify(); return self._send(200, {"records": LEDGER.recs, "valid": ok, "bad": bad})
        if p == "/api/appeals": return self._send(200, {"items": read_appeals(), "data_mode": "SIMULATED_DEMO"})
        if p == "/api/officer/dashboard": return self._send(200, officer.dashboard(LEDGER.recs, read_appeals()))
        if p == "/api/ledger/verify": ok, bad = LEDGER.verify(); return self._send(200, {"valid": ok, "bad": bad, "count": len(LEDGER.recs)})
        if p == "/api/status": return self._send(200, {"llm": bool(os.environ.get("ANTHROPIC_API_KEY")), "rate_top": engine.RATE_TOP})
        f = os.path.join(HERE, "static", "index.html" if p == "/" else p.lstrip("/"))
        if os.path.isfile(f) and os.path.abspath(f).startswith(os.path.join(HERE, "static")):
            return self._send(200, open(f, "rb").read(), "text/html" if f.endswith(".html") else "application/octet-stream")
        self._send(404, {"error": "haipo"})
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 65536: return self._send(413, {"error": "Ombi ni kubwa mno."})
        try: d = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, UnicodeDecodeError): return self._send(400, {"error": "JSON si sahihi."})
        p = self.path
        try:
            if p == "/api/chat": return self._send(200, chat(d.get("sid") or uuid.uuid4().hex, d.get("text")))
            if p == "/api/appeal":
                ref = str(d.get("reference") or "").strip()
                msg = str(d.get("message") or "").strip()
                if len(msg) < 8: return self._send(400, {"error": "Eleza sababu kwa angalau herufi 8."})
                return self._send(201, {"item": add_demo_appeal(ref, msg), "notice": "Ombi limehifadhiwa kwenye demo pekee; halijatumwa TRA."})
            if p == "/api/sms":
                sid = "sms-" + (d.get("sid") or uuid.uuid4().hex)
                result = chat(sid, d.get("text", ""))
                return self._send(200, {"channel": "SMS_DEMO", "reply": result.get("reply"), "stage": result.get("stage"), "result": result.get("result"), "sms": result.get("sms")})
            if p == "/api/ussd":
                if d.get("reset"): SESS.pop("u" + d["sid"], None)
                return self._send(200, ussd(d["sid"], d.get("text")))
            if p == "/api/officer/decision":
                item = officer.decide(d.get("record_id", ""), d.get("decision", ""), d.get("note", ""))
                return self._send(201, {"item": item, "notice": "Uamuzi wa mfano umehifadhiwa; hauna athari ya kisheria wala haujabadilisha kodi."})
            if p in ("/api/ledger/tamper", "/api/ledger/reset"):
                if os.environ.get("KODI_MAHIRI_DEMO_ADMIN") != "1": return self._send(403, {"error": "Kitendo cha majaribio kimezimwa. Weka KODI_MAHIRI_DEMO_ADMIN=1 kwa majaribio ya ndani pekee."})
                if p.endswith("tamper"): return self._send(200, {"ok": LEDGER.tamper()})
                LEDGER.reset(); return self._send(200, {"ok": True})
        except Exception as e:
            import traceback; traceback.print_exc(); return self._send(500, {"error": str(e)})
        self._send(404, {"error": "haipo"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Kodi Mahiri DEMO iko tayari: http://127.0.0.1:{port}   (AI ya nje: {'imewashwa kwa hiari' if os.environ.get('ANTHROPIC_API_KEY') else 'haijaunganishwa; kanuni za ndani zinatumika'})")
    host = os.environ.get("HOST", "127.0.0.1")
    ThreadingHTTPServer((host, port), H).serve_forever()
