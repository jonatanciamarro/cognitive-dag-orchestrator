from __future__ import annotations

from dataclasses import dataclass, field, asdict, fields
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _filter_payload(cls, payload: dict[str, Any]) -> dict[str, Any]:
    valid_keys = {item.name for item in fields(cls)}
    return {key: value for key, value in payload.items() if key in valid_keys}


@dataclass(slots=True)
class Campaign:
    campaign_id: str
    name: str = ""
    status: str = "active"
    budget: float = 0.0
    spend: float = 0.0
    revenue: float = 0.0
    target_cpa: float = 0.0
    target_roas: float = 0.0
    opt_in: bool = False
    compliance_ok: bool = True
    compliance_notes: str = ""
    updated_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Campaign":
        data = dict(payload)
        if "updated_at" in data:
            data["updated_at"] = _parse_datetime(data["updated_at"])
        return cls(**_filter_payload(cls, data))


@dataclass(slots=True)
class Event:
    event_id: str
    campaign_id: str
    kind: str
    occurred_at: datetime
    value: float = 0.0
    count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["occurred_at"] = self.occurred_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Event":
        data = dict(payload)
        data["occurred_at"] = _parse_datetime(data["occurred_at"])
        data.setdefault("value", 0.0)
        data.setdefault("count", 1)
        data.setdefault("metadata", {})
        return cls(**_filter_payload(cls, data))


@dataclass(slots=True)
class Metrics:
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0
    ctr: float = 0.0
    cvr: float = 0.0
    cpa: float | None = None
    roas: float | None = None
    anomaly_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "impressions": self.impressions,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "spend": round(self.spend, 6),
            "revenue": round(self.revenue, 6),
            "ctr": round(self.ctr, 6),
            "cvr": round(self.cvr, 6),
            "cpa": None if self.cpa is None else round(self.cpa, 6),
            "roas": None if self.roas is None else round(self.roas, 6),
            "anomaly_flags": list(self.anomaly_flags),
        }


@dataclass(slots=True)
class Decision:
    action: str
    campaign_id: str
    reason: str
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_review: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "campaign_id": self.campaign_id,
            "reason": self.reason,
            "parameters": self.parameters,
            "confidence": round(self.confidence, 6),
            "requires_review": self.requires_review,
        }


@dataclass(slots=True)
class Policy:
    name: str = "default"
    opt_in_required: bool = True
    min_impressions: int = 100
    min_clicks: int = 25
    min_conversions: int = 3
    pause_cpa_multiplier: float = 1.5
    scale_roas_multiplier: float = 1.2
    scale_cpa_multiplier: float = 0.8
    scale_min_ctr: float = 0.02
    scale_min_cvr: float = 0.02
    create_test_min_clicks: int = 30
    create_test_max_conversions: int = 2
    scale_budget_fraction: float = 0.15
    test_variant_count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Policy":
        return cls(**_filter_payload(cls, dict(payload)))
