"""Small JSON-backed rule registry for a local portfolio demonstration."""
import json
from pathlib import Path
from datetime import datetime, timezone

class RuleRegistry:
    def __init__(self, config_path="config/rules.json", history_path="data/rule_change_history.json"):
        self.config_path = Path(config_path)
        self.history_path = Path(history_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.config_path.write_text(json.dumps({"rules":[],"decision_thresholds":{"review":25,"decline":60}}, indent=2))
        if not self.history_path.exists():
            self.history_path.write_text("[]")

    def get(self):
        return json.loads(self.config_path.read_text())

    def update_rule(self, rule_id: str, updates: dict, changed_by: str, rationale: str):
        config = self.get()
        target = next((r for r in config["rules"] if r["id"] == rule_id), None)
        if target is None:
            raise KeyError(rule_id)
        before = dict(target)
        target.update(updates)
        target["version"] = int(before.get("version", 1)) + 1
        config["rules"] = config["rules"]
        self.config_path.write_text(json.dumps(config, indent=2))
        history = json.loads(self.history_path.read_text())
        history.append({"rule_id":rule_id,"version":target["version"],"changed_at":datetime.now(timezone.utc).isoformat(),
                        "changed_by":changed_by,"rationale":rationale,"before":before,"after":target})
        self.history_path.write_text(json.dumps(history, indent=2))
        return target

    def history(self):
        return json.loads(self.history_path.read_text())
