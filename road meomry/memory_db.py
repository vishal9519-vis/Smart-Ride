import json
import os
from datetime import datetime

# Resolve data directory relative to this file so it works from any cwd
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_DB_PATH = os.path.join(_MODULE_DIR, "..", "data", "road_memory.json")


class RoadMemoryDB:

    def __init__(self, path=None):
        self.path = os.path.abspath(path or _DEFAULT_DB_PATH)
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        return {"segments": []}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def add(self, ts, roughness, potholes, comfort):
        if roughness < 50 and potholes == 0:
            return
        seg = {
            "id":        len(self.data["segments"]) + 1,
            "ts":        round(float(ts), 2),
            "lat":       round(17.385 + float(ts) * 0.0001, 6),
            "lon":       round(78.486 + float(ts) * 0.0001, 6),
            "roughness": int(roughness),
            "potholes":  int(potholes),
            "comfort":   round(float(comfort), 1),
            "severity":  "CRITICAL" if roughness > 80 else "WARNING" if roughness > 55 else "CAUTION",
            "at":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.data["segments"].append(seg)
        self._save()

    def stats(self):
        s = self.data["segments"]
        if not s:
            return {}
        return {
            "total":     len(s),
            "critical":  sum(1 for x in s if x["severity"] == "CRITICAL"),
            "warning":   sum(1 for x in s if x["severity"] == "WARNING"),
            "avg_rough": round(sum(x["roughness"] for x in s) / len(s), 1),
        }
