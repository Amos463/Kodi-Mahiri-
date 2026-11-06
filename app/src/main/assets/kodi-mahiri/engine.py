"""Injini ya majaribio: sekta, msimu, data bandia za Lipa Namba za biashara/TIN, upatanisho na mfano wa kodi. Si injini rasmi ya TRA."""
import random, statistics, datetime as dt
from geo import URBAN
from transaction_intelligence import make_demo_transactions, summarize_demo_transactions

# Viwango vya mfano vya prototype; lazima vihakikiwe na mtaalamu dhidi ya sheria rasmi kabla ya matumizi.
PRESUMPTIVE_CEILING = 200_000_000
RATE_TOP = 0.04   # kwa mauzo TZS milioni 11 hadi 200 (rasimu ya bajeti ilipendekeza 4.5%; sheria ya mwisho: 4%)

SEASONS = {
 "general":[1.1,.95,.95,.95,1,1,1.05,1.05,1.05,1,1.1,1.3],
 "agri":[.7,.7,.8,.9,1.1,1.4,1.5,1.4,1.2,1,.8,.8],
 "festive":[.95,.9,.95,1,.95,1,1,1,1,1,1.05,1.5]}
for _k, _v in SEASONS.items():
    _m = sum(_v) / 12; SEASONS[_k] = [x / _m for x in _v]

# margin = faida ya jumla (kukokotoa mauzo kutoka manunuzi); digital = sehemu ya mauzo kupitia Lipa Namba
S = lambda i,n,kw,mg,dg,se,lo,hi,**k: dict(id=i,name=n,kw=kw,margin=mg,digital=dg,season=se,base=(lo,hi),days=k.get("days",26),
        purch=k.get("purch",True),excluded=k.get("ex",False),note=k.get("note",""))
SECTORS = [
 S("duka","Duka la rejareja (vyakula, mahitaji)",["duka","rejareja","kioski","genge"],.15,.45,"general",40e3,180e3),
 S("jumla","Duka la jumla",["jumla","wholesale"],.08,.6,"general",300e3,1.5e6),
 S("chakula","Mamalishe / mgahawa / chakula",["mamalishe","mama lishe","mgahawa","chips","chakula","mama ntilie"],.35,.35,"festive",30e3,150e3,days=27),
 S("machinga","Machinga / mchuuzi",["machinga","mchuuzi","kuuza barabarani","mwenye meza"],.2,.25,"general",15e3,80e3),
 S("bodaboda","Bodaboda (pikipiki ya abiria)",["bodaboda","boda","pikipiki"],.55,.2,"general",15e3,45e3,days=28,purch=False,
   note="Usafirishaji una viwango maalum vya presumptive kwenye First Schedule; thibitisha na TRA."),
 S("bajaji","Bajaji / teksi / daladala",["bajaji","bajaj","teksi","taxi","daladala","kirikuu"],.5,.25,"general",30e3,120e3,days=28,purch=False,
   note="Usafirishaji una viwango maalum vya presumptive kwenye First Schedule; thibitisha na TRA."),
 S("mazao","Mazao / bidhaa za shambani",["mazao","mahindi","mpunga","mboga","matunda","nyanya","kahawa","viazi","mawinga","wakala wa mazao"],.12,.4,"agri",50e3,400e3),
 S("wakala","Wakala wa pesa mtandao / benki",["wakala","mpesa","m-pesa","tigo pesa","airtel money","halopesa","wakala wa benki"],0,.9,"general",20e3,120e3,purch=False),
 S("saluni","Saluni / kinyozi / urembo",["saluni","kinyozi","nywele","urembo","kusuka"],.5,.3,"festive",20e3,100e3),
 S("fundi","Fundi (gereji, welding, useremala)",["fundi","mekanika","gereji","garage","welding","seremala","useremala","cherehani","ushonaji","mshonaji"],.4,.3,"general",30e3,200e3),
 S("dawa","Duka la dawa / famasi",["dawa","famasi","pharmacy","adui"],.25,.5,"general",100e3,600e3,note="Inahitaji leseni ya TMDA/Baraza la Famasia."),
 S("hardware","Vifaa vya ujenzi (hardware)",["hardware","saruji","mabati","vifaa vya ujenzi","nondo","rangi"],.12,.5,"general",150e3,900e3),
 S("nguo","Nguo, viatu na mitumba",["nguo","viatu","mitumba","boutique","kitenge"],.3,.35,"festive",40e3,250e3),
 S("elektroniki","Simu na elektroniki",["elektroniki","kompyuta","spea za simu","duka la simu","simu"],.15,.55,"general",100e3,700e3),
 S("baa","Baa / nyumba ya wageni / hoteli",["baa","bar","gesti","nyumba ya wageni","lodge","hoteli","grocery"],.4,.5,"festive",80e3,500e3),
 S("uvuvi","Uvuvi / ufugaji / mifugo",["samaki","uvuvi","ufugaji","kuku","ng'ombe","mifugo","dagaa"],.25,.35,"agri",40e3,300e3),
 S("kitaalamu","Huduma za kitaalamu / ushauri / ujenzi / mafunzo",["kitaalamu","ushauri","mhasibu","wakili","daktari","mkandarasi","ukandarasi","mafunzo","tuition","mhandisi"],.0,.5,"general",100e3,500e3,purch=False,ex=True,
   note="Hazipo kwenye presumptive tax: zinatozwa kwa mfumo wa self-assessment."),
]
SECTOR = {s["id"]: s for s in SECTORS}

def presumptive(turnover, records=False):
    """Kodi ya mwaka kwa mauzo ya mwaka (watu binafsi). None = juu ya kikomo."""
    if turnover <= 4_000_000: return 0
    if turnover <= 7_000_000: return round(0.03 * (turnover - 4e6)) if records else 100_000
    if turnover <= 11_000_000: return round(90_000 + 0.03 * (turnover - 7e6)) if records else 250_000
    if turnover <= PRESUMPTIVE_CEILING: return round(RATE_TOP * turnover)
    return None

def synth_evidence(tin, sec, region, month):
    """DATA ZA MFANO tu: miamala ya Lipa Namba ya biashara (Till/Paybill) na manunuzi ya mfano. Hakuna API au data halisi ya TRA/benki/mitandao iliyounganishwa."""
    rng = random.Random(f"{tin}|{sec['id']}")
    lo, hi = sec["base"]; true_daily = rng.uniform(lo, hi) * URBAN.get(region, 1.0)
    se = SEASONS[sec["season"]]; monthly, daily = [0.0] * 3, []
    for d in range(90):
        k = d // 30; mm = (month - k) % 12
        v = true_daily * sec["days"] / 30 * se[mm] * sec["digital"] * rng.lognormvariate(0, .25)
        if rng.random() < .02: v *= 3
        daily.append(v); monthly[k] += v
    purch, sup = None, []
    if sec["purch"]:
        purch = [true_daily * sec["days"] * se[(month - k) % 12] * (1 - sec["margin"]) * rng.uniform(.85, 1.12) for k in range(3)]
        names = ["Mohamed Traders","Said Wholesalers","Mufindi Supplies","Kilimanjaro Agro","Bakhresa Distribution","Mwanga Distributors"]
        sup = [{"supplier": rng.choice(names), "invoices": rng.randint(2, 5)} for _ in range(2)]
    business_no = "LIPA-DEMO-" + str(rng.randint(100000, 999999))
    tx = summarize_demo_transactions(make_demo_transactions(tin, business_no))
    return {"source": "SIMULATED_DEMO", "business_lipa_namba": business_no, "lipa_monthly": monthly, "lipa_daily": daily, "purchases_monthly": purch, "suppliers": sup, "transaction_intelligence": tx}

def assess(sl, consent=True, today=None):
    sec = SECTOR[sl["sector"]]; today = today or dt.date.today(); m = today.month - 1
    se = SEASONS[sec["season"]]; out = {"sector": sec["name"], "sector_id": sec["id"], "region": sl["region"], "district": sl["district"],
        "declared_daily": sl["daily_sales"], "season_mult": round(se[m], 2), "notes": []}
    if sec["note"]: out["notes"].append(sec["note"])
    declared = sl["daily_sales"] / se[m] * sec["days"] * 12      # mauzo ya mwaka baada ya kuondoa athari ya msimu
    out.update(declared_annual=round(declared), lipa_annual=None, purchases_annual=None, evidence_annual=None, ratio=None,
               proposed_assessed_annual=None, proposed_tax_annual=None, review_required=False, officer_decision="NOT_REVIEWED",
               spikes=0, confidence=.35, status="SAWA", evidence=None)
    if sec["excluded"]:
        out.update(status="SELF-ASSESSMENT", assessed_annual=round(declared), tax_annual=0, tax_quarter=0, tax_with_records=0, risk=0)
        out["notes"].append("Kodi haikokotolewi hapa; wasiliana na TRA kwa self-assessment."); return out
    have = consent and sl.get("tin") not in (None, "NONE")
    if have:
        ev = synth_evidence(sl["tin"], sec, sl["region"], m); out["evidence"] = ev; out["data_mode"] = "SIMULATED_DEMO"
        lm = [ev["lipa_monthly"][k] / se[(m - k) % 12] for k in range(3)]
        out["lipa_annual"] = round(statistics.mean(lm) * 12 / sec["digital"]); parts = [out["lipa_annual"]]; out["confidence"] += .25
        if ev["purchases_monthly"]:
            pm = [ev["purchases_monthly"][k] / se[(m - k) % 12] for k in range(3)]
            out["purchases_annual"] = round(statistics.mean(pm) * 12 / (1 - sec["margin"])); parts.append(out["purchases_annual"]); out["confidence"] += .25
        out["evidence_annual"] = out["lipa_annual"]  # manunuzi ni ushahidi saidizi, si mauzo wala sehemu ya wastani wa mauzo
        out["ratio"] = round(out["evidence_annual"] / declared, 2)
        d = ev["lipa_daily"]; mu, sd = statistics.mean(d), statistics.pstdev(d) or 1
        out["spikes"] = sum(1 for x in d if (x - mu) / sd > 3)
    else:
        out["notes"].append("Hakuna ulinganisho wa mfano: tathmini hii imetumia mauzo uliyotaja pekee.")
    r = out["ratio"] or 1
    assessed = declared
    if r > 1.3:
        out["review_required"] = True
        out["proposed_assessed_annual"] = round(out["evidence_annual"])
        out["proposed_tax_annual"] = presumptive(out["proposed_assessed_annual"])
        out["status"] = "HATARI" if r > 2 else "KAGUA"
        out["notes"].append("DATA ZA MFANO zinaonyesha tofauti na mauzo uliyotaja. Mfumo unaweka tahadhari kwa ukaguzi wa binadamu; haujabadilisha mauzo wala kodi kwa kutumia data bandia.")
    elif r < .7:
        out["notes"].append("Mauzo uliyotaja ni makubwa kuliko ushahidi wa miamala; tumetumia uliyotaja.")
    out["assessed_annual"] = round(declared); tax = presumptive(declared)
    out["notes"].append("Kodi ya awali imehesabiwa kwa mauzo aliyotaja mlipakodi. Ikiwa ushahidi wa Lipa Namba unazidi mara 1.3, mfumo huandaa pendekezo la ukaguzi tu; afisa lazima athibitishe ushahidi na kumpa mlipakodi nafasi ya kujibu kabla ya uamuzi. Manunuzi ya TIN ni ushahidi saidizi, si mauzo.")
    if tax is None:
        out.update(status="JUU YA KIKOMO", tax_annual=0, tax_quarter=0, tax_with_records=0); out["notes"].append("Mauzo yanazidi TZS milioni 200: hamia self-assessment/hesabu zilizokaguliwa.")
    else:
        out.update(tax_annual=tax, tax_quarter=round(tax / 4), tax_with_records=presumptive(assessed, True))
        if tax == 0: out["notes"].append("Mauzo ya mwaka hayazidi TZS milioni 4: hakuna kodi, lakini jisajili kupata TIN.")
    out["risk"] = max(0, min(100, round((r - 1) * 60))) if r > 1 else 0
    out["confidence"] = round(min(out["confidence"], .95), 2)
    return out
