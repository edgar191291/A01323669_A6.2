#!/usr/bin/env python3
"""
smoke_test.py

Quick manual test to verify JSON persistence and basic operations.
"""

from __future__ import annotations

from datetime import date

from src.services import (
    cancel_reservation,
    create_customer,
    create_hotel,
    create_reservation,
    display_customer,
    display_hotel,
)


def main() -> None:
    print("Creating hotel and customer...")
    print("create_hotel:", create_hotel("H1", "Hotel Uno", 10))
    print("create_customer:", create_customer("C1", "Edgar Rosas", "edgar@example.com"))

    print("\nDisplaying...")
    print("display_hotel:", display_hotel("H1"))
    print("display_customer:", display_customer("C1"))

    print("\nCreating reservation...")
    ok = create_reservation(
        reservation_id="R1",
        hotel_id="H1",
        customer_id="C1",
        check_in=date(2026, 3, 1),
        check_out=date(2026, 3, 5),
        rooms=3,
    )
    print("create_reservation:", ok)

    print("\nCancel reservation...")
    print("cancel_reservation:", cancel_reservation("R1"))


if __name__ == "__main__":
    main()