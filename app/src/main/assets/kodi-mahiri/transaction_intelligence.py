"""Uchambuzi wa miamala ya MAJARIBIO. Hakuna data ya benki/TRA/mitandao inayovutwa."""
import random


def make_demo_transactions(seed, business_number, count=16):
    """Tengeneza rekodi bandia za Till/Paybill ya biashara na akaunti ya biashara."""
    rng = random.Random(str(seed) + "|tx-demo")
    rows = []
    till_types = ["MALIPO_TILL", "MALIPO_PAYBILL", "REFUND", "REVERSAL"]
    account_types = ["MKopo_ULIOPOKELEWA", "UHamisho_WA_MMILIKI", "COMMISSION"]
    for i in range(count):
        is_till = rng.random() < .78
        kind = rng.choices(till_types if is_till else account_types,
                           weights=[62, 20, 10, 8] if is_till else [35, 40, 25])[0]
        amount = rng.randrange(5, 150) * 1000
        if kind in ("REFUND", "REVERSAL"):
            amount = -amount
        rows.append({
            "id": f"TX-DEMO-{i+1:03d}",
            "source": "LIPA_NAMBA_TILL_PAYBILL" if is_till else "AKAUNTI_BIASHARA_DEMO",
            "business_number": business_number if is_till else None,
            "raw_type": kind,
            "amount_tzs": amount,
            "currency": "TZS",
            "demo": True,
        })
    return rows


def classify_demo_transactions(rows):
    """Kanuni zinazoelezeka kwa demo; si machine learning wala ushahidi wa kodi."""
    labels = {
        "MALIPO_TILL": ("MAUZO_YA_BIASHARA", "Malipo yameingia kupitia Till ya biashara."),
        "MALIPO_PAYBILL": ("MAUZO_YA_BIASHARA", "Malipo yameingia kupitia Paybill ya biashara."),
        "REFUND": ("REJESHO", "Rejesho limepunguza mapokezi halisi."),
        "REVERSAL": ("MUAMALA_ULIOBATILISHWA", "Muamala umebatilishwa; usihesabiwe kama mauzo halisi."),
        "MKopo_ULIOPOKELEWA": ("MKopo_SIO_MAUZO", "Mkoponi si mauzo ya bidhaa/huduma."),
        "UHamisho_WA_MMILIKI": ("UHamisho_SIO_MAUZO", "Uhamisho wa fedha za mmiliki si lazima uwe mauzo."),
        "COMMISSION": ("KAMISHENI", "Kamisheni ndiyo mapato ya huduma ya uwakala; si jumla ya fedha zilizopitishwa."),
    }
    out = []
    for row in rows:
        label, reason = labels.get(row.get("raw_type"), ("HAIJAJULIKANA", "Inahitaji uhakiki wa binadamu."))
        out.append({**row, "category": label, "reason": reason,
                    "confidence": 0.99 if label != "HAIJAJULIKANA" else 0.0})
    return out


def summarize_demo_transactions(rows):
    classified = classify_demo_transactions(rows)
    totals = {}
    for row in classified:
        totals[row["category"]] = totals.get(row["category"], 0) + row["amount_tzs"]
    return {"source": "SIMULATED_DEMO", "count": len(classified),
            "totals_tzs": totals, "transactions": classified}
