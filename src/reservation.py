#!/usr/bin/env python3
"""
reservation.py

Reservation entity and validation helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True, slots=True)
class Reservation:
    """Represents a reservation made by a customer for a hotel."""

    reservation_id: str
    hotel_id: str
    customer_id: str
    check_in: date
    check_out: date
    rooms: int

    def __post_init__(self) -> None:
        if not self.reservation_id.strip():
            raise ValueError("reservation_id cannot be empty.")
        if not self.hotel_id.strip():
            raise ValueError("hotel_id cannot be empty.")
        if not self.customer_id.strip():
            raise ValueError("customer_id cannot be empty.")
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in.")
        if not isinstance(self.rooms, int) or self.rooms <= 0:
            raise ValueError("rooms must be a positive integer.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-ready dict."""
        return {
            "reservation_id": self.reservation_id,
            "hotel_id": self.hotel_id,
            "customer_id": self.customer_id,
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "rooms": self.rooms,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Reservation":
        """
        Deserialize from a dict,
        raising ValueError if required fields are missing.
        """
        return Reservation(
            reservation_id=str(data["reservation_id"]),
            hotel_id=str(data["hotel_id"]),
            customer_id=str(data["customer_id"]),
            check_in=date.fromisoformat(str(data["check_in"])),
            check_out=date.fromisoformat(str(data["check_out"])),
            rooms=int(data["rooms"]),
        )
