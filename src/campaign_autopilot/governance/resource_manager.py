"""Resource Manager — budget, queue, rate limiting, priority scheduling.

Gerenciamento de recursos computacionais e operacionais para evitar
sobrecarga, garantir priorização correta e otimizar custo-benefício.
"""

from __future__ import annotations

from collections import deque
from enum import Enum


class ResourceType(Enum):
    API_CALLS = "api_calls"
    TOKENS = "tokens"
    STORAGE = "storage"
    TIME = "time"
    MONEY = "money"


class ResourceBudget:
    def __init__(self, name: str, limits: dict[str, float]):
        self.name = name
        self.limits = limits
        self.usage: dict[str, float] = {}
        self.spent: dict[str, float] = {}
        self.history: list[dict] = []

    def check(self, resource: str, amount: float = 1.0) -> dict:
        daily_used = self.usage.get(resource, 0)
        daily_limit = self.limits.get(resource, float("inf"))
        remaining = max(0, daily_limit - daily_used)
        return {
            "resource": resource,
            "requested": amount,
            "remaining": remaining,
            "available": remaining >= amount,
            "usage_pct": round((daily_used / daily_limit) * 100, 1)
            if daily_limit > 0
            else 0,
        }

    def consume(self, resource: str, amount: float = 1.0) -> dict:
        check = self.check(resource, amount)
        if check["available"]:
            self.usage[resource] = self.usage.get(resource, 0) + amount
            self.spent[resource] = self.spent.get(resource, 0) + amount
            check["consumed"] = True
        else:
            check["consumed"] = False
        self.history.append(check)
        return check

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "limits": self.limits,
            "usage": self.usage,
            "remaining": {
                k: max(0, self.limits.get(k, 0) - self.usage.get(k, 0))
                for k in self.limits
            },
        }


class QueueManager:
    def __init__(self, max_concurrent: int = 5):
        self.queues: dict[str, deque] = {}
        self.max_concurrent = max_concurrent
        self.running: dict[str, int] = {}
        self.priorities = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    def enqueue(self, item: dict, queue_name: str = "default"):
        if queue_name not in self.queues:
            self.queues[queue_name] = deque()
        priority = self.priorities.get(item.get("priority", "medium"), 2)
        self.queues[queue_name].append((priority, item))
        # Sort by priority
        self.queues[queue_name] = deque(
            sorted(self.queues[queue_name], key=lambda x: x[0])
        )
        return {"position": len(self.queues[queue_name]), "queue": queue_name}

    def dequeue(self, queue_name: str = "default") -> dict | None:
        if queue_name not in self.queues or not self.queues[queue_name]:
            return None
        running = self.running.get(queue_name, 0)
        if running >= self.max_concurrent:
            return None
        _, item = self.queues[queue_name].popleft()
        self.running[queue_name] = running + 1
        return item

    def complete(self, queue_name: str = "default"):
        self.running[queue_name] = max(0, self.running.get(queue_name, 0) - 1)

    def get_status(self) -> dict:
        return {
            "queues": {
                q: {
                    "waiting": len(self.queues[q]),
                    "running": self.running.get(q, 0),
                    "priorities": [item[0] for item in self.queues[q]],
                }
                for q in self.queues
            },
            "max_concurrent": self.max_concurrent,
        }


class ResourceManager:
    @staticmethod
    def create_budget(name: str, limits: dict[str, float]) -> ResourceBudget:
        return ResourceBudget(name, limits)

    @staticmethod
    def create_queue_manager(max_concurrent: int = 5) -> QueueManager:
        return QueueManager(max_concurrent)

    @staticmethod
    def estimate_cost(action: str, params: dict) -> dict:
        costs = {
            "generate_image": {"tokens": 0, "time_sec": 5, "money": 0},
            "generate_video": {"tokens": 0, "time_sec": 120, "money": 0},
            "generate_article": {"tokens": 1000, "time_sec": 2, "money": 0},
            "api_call": {"tokens": 0, "time_sec": 1, "money": 0},
            "seo_scrape": {"tokens": 0, "time_sec": 30, "money": 0},
        }
        return costs.get(action, {"tokens": 100, "time_sec": 10, "money": 0})
