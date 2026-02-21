#!/usr/bin/env python3
"""
customer.py

Customer entity and validation helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Customer:
    """Represents a customer in the reservation system."""

    customer_id: str
    name: str
    email: str

    def __post_init__(self) -> None:
        if not self.customer_id.strip():
            raise ValueError("customer_id cannot be empty.")
        if not self.name.strip():
            raise ValueError("name cannot be empty.")
        if "@" not in self.email or not self.email.strip():
            raise ValueError("email must be a valid email-like string (must contain '@').")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-ready dict."""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Customer":
        """Deserialize from a dict, raising ValueError if required fields are missing."""
        return Customer(
            customer_id=str(data["customer_id"]),
            name=str(data["name"]),
            email=str(data["email"]),
        )