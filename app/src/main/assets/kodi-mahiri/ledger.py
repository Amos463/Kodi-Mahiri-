import json, hashlib, os, threading, time

class Ledger:
    """Daftari lisilobadilika: kila rekodi ina hash ya iliyotangulia (SHA-256)."""
    def __init__(self, path):
        self.path, self.lock = path, threading.Lock()
        self.recs = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    @staticmethod
    def _h(prev, core):
        return hashlib.sha256((prev + json.dumps(core, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()
    def _save(self):
        json.dump(self.recs, open(self.path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    def add(self, body):
        with self.lock:
            prev = self.recs[-1]["hash"] if self.recs else "0" * 64
            core = {"id": len(self.recs) + 1, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "body": body}
            rec = dict(core, prev=prev, hash=self._h(prev, core))
            self.recs.append(rec); self._save(); return rec
    def verify(self):
        prev = "0" * 64
        for r in self.recs:
            core = {k: r[k] for k in ("id", "time", "body")}
            if r["prev"] != prev or self._h(prev, core) != r["hash"]:
                return False, r["id"]
            prev = r["hash"]
        return True, None
    def tamper(self):
        with self.lock:
            if not self.recs: return False
            self.recs[0]["body"]["tax_annual"] = max(0, self.recs[0]["body"]["tax_annual"] - 5000)
            self._save(); return True
    def reset(self):
        with self.lock: self.recs = []; self._save()
