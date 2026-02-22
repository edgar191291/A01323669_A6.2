#!/usr/bin/env python3
"""
hotel.py

Hotel entity and validation helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Hotel:
    """Represents a hotel in the reservation system."""

    hotel_id: str
    name: str
    rooms_total: int

    def __post_init__(self) -> None:
        if not self.hotel_id.strip():
            raise ValueError("hotel_id cannot be empty.")
        if not self.name.strip():
            raise ValueError("name cannot be empty.")
        if not isinstance(self.rooms_total, int) or self.rooms_total <= 0:
            raise ValueError("rooms_total must be a positive integer.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-ready dict."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "rooms_total": self.rooms_total,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Hotel":
        """
        Deserialize from a dict,
        raising ValueError if required fields are missing.
        """
        return Hotel(
            hotel_id=str(data["hotel_id"]),
            name=str(data["name"]),
            rooms_total=int(data["rooms_total"]),
        )
