from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Schedule:
    raw: str

    def __post_init__(self) -> None:
        if not self.raw or not self.raw.strip():
            raise ValueError("Schedule cannot be empty")

        kind = self._kind()

        if kind in {"daily", "weekly", "monthly"}:
            # simple, fixed schedules
            return

        if kind == "times_per_week":
            _ = self.times_per_week  # triggers validation
            return

        raise ValueError(f"Unknown schedule kind in: {self.raw!r}")

    # --- Helpers ---------------------------------------------------------

    def _kind(self) -> str:
        if self.raw in {"daily", "weekly", "monthly"}:
            return self.raw

        if self.raw.startswith("times_per_week:"):
            return "times_per_week"

        return "unknown"

    def _after_prefix(self, prefix: str) -> str:
        if not self.raw.startswith(prefix):
            return ""
        return self.raw[len(prefix) :].strip()

    @property
    def times_per_week(self) -> int:
        """Return N for 'times_per_week:N' schedules, or raise if invalid."""
        value_str = self._after_prefix("times_per_week:")
        if not value_str:
            raise ValueError("times_per_week schedule must be like 'times_per_week:3'")
        try:
            value = int(value_str)
        except ValueError as exc:
            raise ValueError(f"Invalid times_per_week value: {value_str!r}") from exc
        if value <= 0:
            raise ValueError("times_per_week must be positive")
        return value

    @property
    def is_daily(self) -> bool:
        return self.raw == "daily"

    @property
    def is_weekly(self) -> bool:
        return self.raw == "weekly"

    @property
    def is_monthly(self) -> bool:
        return self.raw == "monthly"
