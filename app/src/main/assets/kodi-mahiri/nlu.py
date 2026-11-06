"""Kuelewa Kiswahili huru: LLM (Claude) kama inapatikana, vinginevyo kanuni za ndani. Matokeo yote yanathibitishwa dhidi ya orodha rasmi."""
import re, os, json, difflib, urllib.request
from geo import REGIONS, ALIASES
from engine import SECTORS

DIG = {"sifuri":0,"zero":0,"moja":1,"mbili":2,"tatu":3,"nne":4,"tano":5,"sita":6,"saba":7,"nane":8,"tisa":9}
TENS = {"kumi":10,"ishirini":20,"thelathini":30,"arobaini":40,"hamsini":50,"sitini":60,"sabini":70,"themanini":80,"tisini":90}
YES = {"ndiyo","ndio","sahihi","kweli","sawa","ok","naam","yes","ndiyo.","nakubali","kubali"}
NO = {"hapana","siyo","sio","la","hapana.","kataa","sikubali"}

def toks(t): return [x.replace(",", "").replace(".", "") if x[0].isdigit() else x for x in re.findall(r"\d[\d.,]*|[a-z']+", t.lower())]

def small(t, i):
    v, j, got = 0, i, False
    if j < len(t) and t[j] == "mia":
        j += 1; d = 1
        if j < len(t) and t[j] in DIG and DIG[t[j]] > 0: d = DIG[t[j]]; j += 1
        v += 100 * d; got = True
        if j + 1 < len(t) and t[j] == "na" and (t[j+1] in TENS or t[j+1] in DIG): j += 1
    if j < len(t) and t[j] in TENS:
        v += TENS[t[j]]; j += 1; got = True
        if j + 1 < len(t) and t[j] == "na" and t[j+1] in DIG and DIG[t[j+1]] > 0: v += DIG[t[j+1]]; j += 2
    elif not got and j < len(t) and t[j] in DIG and DIG[t[j]] > 0:
        v = DIG[t[j]]; j += 1; got = True
    return (v if got else None), j

def numbers(t):
    out, i = [], 0
    while i < len(t):
        k = t[i]
        if k.isdigit():
            n, j = int(k), i + 1
            if j < len(t) and t[j] in ("elfu", "k"): n *= 1000; j += 1
            elif j < len(t) and t[j] == "laki": n *= 100000; j += 1
            elif j < len(t) and t[j] in ("milioni", "m"): n *= 10**6; j += 1
            out.append((n, i)); i = j; continue
        if k in ("elfu", "laki", "milioni"):
            j = i + 1
            if j < len(t) and t[j].isdigit(): v, j = int(t[j]), j + 1
            else: v, j = small(t, j)
            unit = {"elfu": 1000, "laki": 100000, "milioni": 10**6}[k]; n = unit * (v or 1)
            if j + 1 < len(t) and t[j] == "na" and t[j+1] == "nusu": n += unit // 2; j += 2
            elif k == "elfu" and j < len(t) and t[j] == "na":
                v2, j2 = small(t, j + 1)
                if v2: n += v2; j = j2
            out.append((n, i)); i = j; continue
        if k in TENS or k == "mia" or (k in DIG and DIG[k] > 0):
            v, j = small(t, i)
            if v: out.append((v, i)); i = j; continue
        i += 1
    return out

def find_tin(text, t):
    m = re.search(r"\d[\d\s-]{7,}\d", text)
    if m and len(re.sub(r"\D", "", m.group())) == 9: return re.sub(r"\D", "", m.group()), set()
    run = []
    for i, k in enumerate(t + ["#"]):
        if k in DIG: run.append(i)
        else:
            if len(run) >= 9: return "".join(str(DIG[t[x]]) for x in run[:9]), set(run)
            run = []
    return None, set()

def amount(t, text):
    nums = [n for n, _ in numbers(t) if n >= 1000]
    if not nums: return None
    n = nums[0]
    if "mwezi" in t: n = round(n / 26)
    elif "wiki" in t: n = round(n / 6)
    return n if 1000 <= n <= 50_000_000 else None

def _fuzzy_in(word, toklist):
    return word in toklist or any(len(x) >= 5 and difflib.SequenceMatcher(None, word, x).ratio() >= .86 for x in toklist)

def geo(t):
    tl = set(t); reg = dis = None
    for name in REGIONS:                       # mkoa
        if all(_fuzzy_in(w, tl) for w in name.lower().split()) and name not in ("Songwe",): reg = reg or name
    for a, name in ALIASES.items():
        if a in " ".join(t): reg = reg or name
    best = 0
    for r, ds in REGIONS.items():              # wilaya (neno refu zaidi hushinda)
        for d in ds:
            ws = d.lower().split()
            if all(_fuzzy_in(w, tl) for w in ws) and len(ws) > best and not (len(ws) == 1 and d.lower() == r.lower() and r != "Songwe"):
                dis, best = (r, d), len(ws)
    if dis and (reg is None or dis[1] not in REGIONS[reg]): reg = dis[0]   # wilaya inashinda ikigongana na mkoa
    return reg, (dis[1] if dis else None)

def sector(text):
    tl, best, bid = text.lower(), 0, None
    for s in SECTORS:
        for k in s["kw"]:
            if re.search(r"(?<![a-z])" + re.escape(k), tl) and len(k) > best: best, bid = len(k), s["id"]
    return bid

def rules(text, ctx=None):
    t = toks(text); sl = {}
    tin, mask = find_tin(text, t)
    if tin: sl["tin"] = tin
    elif re.search(r"sina tin|sijui tin|sina namba|bila tin|sijasajiliwa", text.lower()): sl["tin"] = "NONE"
    t2 = [x for i, x in enumerate(t) if i not in mask and not (len(x) >= 9 and x.isdigit())]
    r, d = geo(t)
    if r: sl["region"] = r
    if d: sl["district"] = d
    s = sector(text)
    if s: sl["sector"] = s
    a = amount(t2, text)
    if a: sl["daily_sales"] = a
    words = set(t)
    sl["_yes"] = bool(words & YES) and not (words & NO); sl["_no"] = bool(words & NO)
    return sl

def valid(sl):
    out = {}
    r = sl.get("region")
    if isinstance(r, str):
        for n in REGIONS:
            if n.lower() == r.lower(): out["region"] = n
    d = sl.get("district")
    if isinstance(d, str):
        for rr, ds in REGIONS.items():
            for x in ds:
                if x.lower() == d.lower(): out.setdefault("region", rr); out["district"] = x
    if out.get("district") and out["district"] not in REGIONS[out["region"]]: out.pop("district")
    if sl.get("sector") in {s["id"] for s in SECTORS}: out["sector"] = sl["sector"]
    try:
        v = int(sl.get("daily_sales") or 0)
        if 1000 <= v <= 50_000_000: out["daily_sales"] = v
    except (ValueError, TypeError): pass
    tin = re.sub(r"\D", "", str(sl.get("tin") or ""))
    if len(tin) == 9: out["tin"] = tin
    elif sl.get("tin") == "NONE": out["tin"] = "NONE"
    return out

SYSTEM = """Wewe ni msaidizi wa sauti wa TRA 'Kodi Mahiri' unayeongea na mfanyabiashara mdogo kwa Kiswahili rahisi na cha heshima.
Kazi: toa taarifa kutoka kwa maneno ya mtumiaji. Rudisha JSON TU: {"slots":{"region":..,"district":..,"sector":..,"daily_sales":..,"tin":..},"reply":".."}.
- region: mojawapo ya mikoa ya Tanzania; district: wilaya yake; sector: moja ya id hizi: %s;
- daily_sales: namba ya shilingi kwa SIKU (badilisha 'elfu themanini'=80000, 'laki moja na nusu'=150000; ukitajiwa kwa mwezi gawanya 26);
- tin: tarakimu 9, au "NONE" akisema hana TIN. Acha null kwa kisichotajwa. Usibuni.
- reply: sentensi 1-2 fupi za Kiswahili zinazoomba TU taarifa zilizobaki (zilizobaki: %s), bila kurudia kila kitu, kama mazungumzo ya simu."""

def llm(text, known, missing, history):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: return None
    try:
        # TIN huchakatwa na kanuni za ndani; usiitume kwa mtoa huduma wa AI wa nje.
        safe_known = {k: v for k, v in known.items() if k != "tin"}
        safe_text = re.sub(r"(?<!\d)(?:\d[\s-]?){8}\d(?!\d)", "[TIN IMEFICHWA]", text)
        safe_history = [{"role": m["role"], "content": re.sub(r"(?<!\d)(?:\d[\s-]?){8}\d(?!\d)", "[TIN IMEFICHWA]", m["content"])} for m in history[-6:]]
        body = {"model": os.environ.get("KODI_MODEL", "claude-sonnet-5-5"), "max_tokens": 400,
                "system": SYSTEM % (", ".join(s["id"] + "=" + s["name"] for s in SECTORS), ", ".join(k for k in missing if k != "tin")),
                "messages": safe_history + [{"role": "user", "content": f"Taarifa zinazojulikana: {json.dumps(safe_known, ensure_ascii=False)}\nMtumiaji: {safe_text}"}]}
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
              {"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
        raw = json.load(urllib.request.urlopen(req, timeout=20))["content"][0]["text"]
        return json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except Exception as e:
        print("LLM haikupatikana, natumia kanuni za ndani:", e); return None
