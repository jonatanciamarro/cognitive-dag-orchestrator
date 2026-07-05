"""Rollback Manager — automatic rollback of changes with versioning.

Garante que mudanças no sistema podem ser revertidas automaticamente
caso causem degradação de performance. Mantém histórico de versões.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ChangeRecord:
    def __init__(
        self,
        target: str,
        change_type: str,
        old_state: dict,
        new_state: dict,
        reason: str,
    ):
        self.timestamp = datetime.now().isoformat()
        self.target = target
        self.change_type = change_type
        self.old_state = old_state
        self.new_state = new_state
        self.reason = reason
        self.rolled_back: bool = False
        self.id = f"change_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "target": self.target,
            "type": self.change_type,
            "reason": self.reason,
            "rolled_back": self.rolled_back,
        }


class RollbackManager:
    def __init__(self, state_dir: str = ".state/rollbacks"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        self.db_file = self.state_dir / "changes.json"
        if self.db_file.exists():
            with open(self.db_file) as f:
                self.history: list = json.load(f)
        else:
            self.history = []
            self._save()

    def _save(self):
        with open(self.db_file, "w") as f:
            json.dump(self.history, f, indent=2, default=str)

    def record_change(
        self,
        target: str,
        change_type: str,
        old_state: dict,
        new_state: dict,
        reason: str,
    ) -> ChangeRecord:
        record = ChangeRecord(target, change_type, old_state, new_state, reason)
        self.history.append(record.to_dict())
        self._save()
        # Save old state as backup
        backup_dir = self.state_dir / record.id
        backup_dir.mkdir(exist_ok=True)
        with open(backup_dir / "old_state.json", "w") as f:
            json.dump(old_state, f, indent=2, default=str)
        return record

    def rollback(self, change_id: str) -> dict:
        for record in self.history:
            if record["id"] == change_id and not record["rolled_back"]:
                record["rolled_back"] = True
                record["rolled_back_at"] = datetime.now().isoformat()
                self._save()
                return {
                    "status": "success",
                    "change_id": change_id,
                    "target": record["target"],
                    "restored_state": record["old_state"],
                }
        return {"status": "failed", "reason": "Change not found or already rolled back"}

    def rollback_last(self, n: int = 1) -> list[dict]:
        results = []
        for record in reversed(self.history):
            if n <= 0:
                break
            if not record["rolled_back"]:
                results.append(self.rollback(record["id"]))
                n -= 1
        return results

    def get_history(self, limit: int = 10) -> list[dict]:
        return self.history[-limit:]

    def health_check(self) -> dict:
        total = len(self.history)
        rolled_back = sum(1 for r in self.history if r.get("rolled_back"))
        return {
            "total_changes": total,
            "rolled_back": rolled_back,
            "rollback_rate": round(rolled_back / max(total, 1) * 100, 1),
        }
