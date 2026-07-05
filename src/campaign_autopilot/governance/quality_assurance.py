"""Quality Assurance — output validation, benchmarks, validation pipeline.

Valida a qualidade dos outputs do sistema (conteúdo, imagens, vídeos)
contra benchmarks e critérios de qualidade predefinidos.
"""

from __future__ import annotations

import re
from typing import Any


class QualityCheck:
    def __init__(self, name: str, category: str, criteria: list[dict]):
        self.name = name
        self.category = category  # content, image, video, code
        self.criteria = criteria
        self.results: list[dict] = []

    def run(self, target: Any) -> dict[str, Any]:
        self.results = []
        passed = 0
        for criterion in self.criteria:
            check_type = criterion.get("type", "exists")
            field = criterion.get("field", "")
            min_val = criterion.get("min", 0)
            max_val = criterion.get("max", float("inf"))
            result = self._check(check_type, target, field, min_val, max_val, criterion)
            self.results.append(result)
            if result["passed"]:
                passed += 1
        total = len(self.criteria)
        return {
            "check": self.name,
            "category": self.category,
            "passed": passed,
            "total": total,
            "score": round(passed / max(total, 1) * 100, 1),
            "details": self.results,
        }

    def _check(
        self,
        check_type: str,
        target: Any,
        field: str,
        min_val: float,
        max_val: float,
        criterion: dict | None = None,
    ) -> dict:
        try:
            if check_type == "exists":
                value = (
                    target.get(field)
                    if isinstance(target, dict)
                    else getattr(target, field, None)
                )
                return {"field": field, "type": "exists", "passed": value is not None}
            elif check_type == "length":
                value = (
                    target.get(field, "")
                    if isinstance(target, dict)
                    else getattr(target, field, "")
                )
                val = len(value) if isinstance(value, str) else value
                return {
                    "field": field,
                    "type": "length",
                    "value": val,
                    "min": min_val,
                    "passed": val >= min_val,
                }
            elif check_type == "range":
                value = (
                    target.get(field, 0)
                    if isinstance(target, dict)
                    else getattr(target, field, 0)
                )
                return {
                    "field": field,
                    "type": "range",
                    "value": value,
                    "min": min_val,
                    "max": max_val,
                    "passed": min_val <= value <= max_val,
                }
            elif check_type == "regex":
                value = (
                    target.get(field, "")
                    if isinstance(target, dict)
                    else getattr(target, field, "")
                )
                pattern = (criterion or {}).get("pattern", "")
                match = bool(re.match(pattern, str(value)))
                return {"field": field, "type": "regex", "passed": match}
        except Exception as e:
            return {
                "field": field,
                "type": check_type,
                "passed": False,
                "error": str(e),
            }
        return {"field": field, "type": check_type, "passed": False}

    def to_dict(self) -> dict:
        return {"name": self.name, "category": self.category, "criteria": self.criteria}


class Benchmark:
    def __init__(self, name: str, category: str, targets: dict[str, float]):
        self.name = name
        self.category = category
        self.targets = targets  # metric -> target value

    def evaluate(self, metrics: dict[str, float]) -> dict[str, Any]:
        results = {}
        passed = 0
        for metric, target in self.targets.items():
            actual = metrics.get(metric, 0)
            met = actual >= target
            results[metric] = {"target": target, "actual": actual, "met": met}
            if met:
                passed += 1
        score = round(passed / max(len(self.targets), 1) * 100, 1)
        return {
            "benchmark": self.name,
            "category": self.category,
            "score": score,
            "passed": passed,
            "total": len(self.targets),
            "results": results,
        }


class QualityAssurance:
    @staticmethod
    def create_check(name: str, category: str, criteria: list[dict]) -> QualityCheck:
        return QualityCheck(name, category, criteria)

    @staticmethod
    def create_benchmark(
        name: str, category: str, targets: dict[str, float]
    ) -> Benchmark:
        return Benchmark(name, category, targets)

    @staticmethod
    def get_content_benchmarks() -> dict[str, Benchmark]:
        return {
            "article_quality": Benchmark(
                "Article Quality",
                "content",
                {
                    "min_words": 800,
                    "has_title": 1,
                    "has_sections": 3,
                    "keyword_density_min": 0.5,
                    "keyword_density_max": 3.0,
                },
            ),
            "image_quality": Benchmark(
                "Image Quality",
                "image",
                {
                    "min_width": 1080,
                    "min_height": 630,
                    "has_text": 1,
                },
            ),
            "video_quality": Benchmark(
                "Video Quality",
                "video",
                {
                    "min_duration_sec": 10,
                    "has_transitions": 1,
                    "has_audio": 1,
                },
            ),
            "seo_quality": Benchmark(
                "SEO Quality",
                "seo",
                {
                    "has_meta_description": 1,
                    "has_headings": 1,
                    "keyword_in_title": 1,
                    "has_internal_links": 0,
                    "has_external_links": 0,
                },
            ),
        }

    @staticmethod
    def validate_output(output_type: str, output: dict) -> dict[str, Any]:
        checks = {
            "article": [
                {"type": "length", "field": "title", "min": 10},
                {"type": "length", "field": "content", "min": 300},
                {"type": "exists", "field": "slug"},
            ],
            "image": [
                {"type": "range", "field": "width", "min": 400, "max": 4000},
                {"type": "range", "field": "height", "min": 300, "max": 4000},
            ],
            "video": [
                {"type": "range", "field": "duration_sec", "min": 5, "max": 600},
                {"type": "exists", "field": "path"},
            ],
        }
        criteria = checks.get(output_type, [{"type": "exists", "field": "status"}])
        check = QualityCheck(f"validate_{output_type}", output_type, criteria)
        return check.run(output)
