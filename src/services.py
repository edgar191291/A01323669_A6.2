#!/usr/bin/env python3
"""
services.py

Business logic (CRUD + reservation/cancel) for the Reservation System.

All persistence is done through JSON files in /data.
If invalid data is found, print an error and continue execution.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from src.customer import Customer
from src.hotel import Hotel
from src.reservation import Reservation
from src.storage import read_json_list, write_json_list


def _print_error(message: str) -> None:
    """Print an error message to stderr (non-fatal)."""
    print(f"[ERROR] {message}", file=sys.stderr)


# ----- Data file locations (relative to repo root) -----
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATA_DIR = _REPO_ROOT / "data"
_HOTELS_PATH = _DATA_DIR / "hotels.json"
_CUSTOMERS_PATH = _DATA_DIR / "customers.json"
_RESERVATIONS_PATH = _DATA_DIR / "reservations.json"


# ----- Load / Save helpers (skip invalid entries but continue) -----
def load_hotels() -> list[Hotel]:
    """Load hotels from JSON; invalid entries are skipped."""
    raw = read_json_list(_HOTELS_PATH)
    hotels: list[Hotel] = []
    for idx, item in enumerate(raw):
        try:
            hotels.append(Hotel.from_dict(item))
        except (KeyError, ValueError, TypeError) as exc:
            _print_error(f"Invalid hotel at index {idx} in '{_HOTELS_PATH}': {exc}. Skipping.")
    return hotels


def save_hotels(hotels: list[Hotel]) -> None:
    """Save hotels to JSON."""
    payload = [h.to_dict() for h in hotels]
    write_json_list(_HOTELS_PATH, payload)


def load_customers() -> list[Customer]:
    """Load customers from JSON; invalid entries are skipped."""
    raw = read_json_list(_CUSTOMERS_PATH)
    customers: list[Customer] = []
    for idx, item in enumerate(raw):
        try:
            customers.append(Customer.from_dict(item))
        except (KeyError, ValueError, TypeError) as exc:
            _print_error(
                f"Invalid customer at index {idx} in '{_CUSTOMERS_PATH}': {exc}. Skipping."
            )
    return customers


def save_customers(customers: list[Customer]) -> None:
    """Save customers to JSON."""
    payload = [c.to_dict() for c in customers]
    write_json_list(_CUSTOMERS_PATH, payload)


def load_reservations() -> list[Reservation]:
    """Load reservations from JSON; invalid entries are skipped."""
    raw = read_json_list(_RESERVATIONS_PATH)
    reservations: list[Reservation] = []
    for idx, item in enumerate(raw):
        try:
            reservations.append(Reservation.from_dict(item))
        except (KeyError, ValueError, TypeError) as exc:
            _print_error(
                f"Invalid reservation at index {idx} in '{_RESERVATIONS_PATH}': {exc}. Skipping."
            )
    return reservations


def save_reservations(reservations: list[Reservation]) -> None:
    """Save reservations to JSON."""
    payload = [r.to_dict() for r in reservations]
    write_json_list(_RESERVATIONS_PATH, payload)


# ----- Generic find helpers -----
def _find_hotel(hotels: list[Hotel], hotel_id: str) -> Hotel | None:
    return next((h for h in hotels if h.hotel_id == hotel_id), None)


def _find_customer(customers: list[Customer], customer_id: str) -> Customer | None:
    return next((c for c in customers if c.customer_id == customer_id), None)


def _find_reservation(reservations: list[Reservation], reservation_id: str) -> Reservation | None:
    return next((r for r in reservations if r.reservation_id == reservation_id), None)


# ----- CRUD: Hotels -----
def create_hotel(hotel_id: str, name: str, rooms_total: int) -> bool:
    """
    Create a hotel. Returns True if created, False otherwise (non-fatal errors).
    """
    hotels = load_hotels()
    if _find_hotel(hotels, hotel_id) is not None:
        _print_error(f"Hotel '{hotel_id}' already exists.")
        return False

    try:
        hotel = Hotel(hotel_id=hotel_id, name=name, rooms_total=rooms_total)
    except ValueError as exc:
        _print_error(str(exc))
        return False

    hotels.append(hotel)
    save_hotels(hotels)
    return True


def delete_hotel(hotel_id: str) -> bool:
    """Delete a hotel by id. Returns True if deleted."""
    hotels = load_hotels()
    before = len(hotels)
    hotels = [h for h in hotels if h.hotel_id != hotel_id]

    if len(hotels) == before:
        _print_error(f"Hotel '{hotel_id}' not found.")
        return False

    save_hotels(hotels)
    return True


def display_hotel(hotel_id: str) -> dict[str, Any] | None:
    """Return a hotel's data as dict, or None if not found."""
    hotels = load_hotels()
    hotel = _find_hotel(hotels, hotel_id)
    if hotel is None:
        _print_error(f"Hotel '{hotel_id}' not found.")
        return None
    return hotel.to_dict()


def modify_hotel(hotel_id: str, name: str | None = None, rooms_total: int | None = None) -> bool:
    """Modify a hotel fields. Returns True if modified."""
    hotels = load_hotels()
    hotel = _find_hotel(hotels, hotel_id)
    if hotel is None:
        _print_error(f"Hotel '{hotel_id}' not found.")
        return False

    new_name = hotel.name if name is None else name
    new_rooms = hotel.rooms_total if rooms_total is None else rooms_total

    try:
        updated = Hotel(hotel_id=hotel.hotel_id, name=new_name, rooms_total=new_rooms)
    except ValueError as exc:
        _print_error(str(exc))
        return False

    hotels = [updated if h.hotel_id == hotel_id else h for h in hotels]
    save_hotels(hotels)
    return True


# ----- CRUD: Customers -----
def create_customer(customer_id: str, name: str, email: str) -> bool:
    """Create a customer. Returns True if created."""
    customers = load_customers()
    if _find_customer(customers, customer_id) is not None:
        _print_error(f"Customer '{customer_id}' already exists.")
        return False

    try:
        customer = Customer(customer_id=customer_id, name=name, email=email)
    except ValueError as exc:
        _print_error(str(exc))
        return False

    customers.append(customer)
    save_customers(customers)
    return True


def delete_customer(customer_id: str) -> bool:
    """Delete a customer by id. Returns True if deleted."""
    customers = load_customers()
    before = len(customers)
    customers = [c for c in customers if c.customer_id != customer_id]

    if len(customers) == before:
        _print_error(f"Customer '{customer_id}' not found.")
        return False

    save_customers(customers)
    return True


def display_customer(customer_id: str) -> dict[str, Any] | None:
    """Return a customer's data as dict, or None if not found."""
    customers = load_customers()
    customer = _find_customer(customers, customer_id)
    if customer is None:
        _print_error(f"Customer '{customer_id}' not found.")
        return None
    return customer.to_dict()


def modify_customer(
    customer_id: str,
    name: str | None = None,
    email: str | None = None,
) -> bool:
    """Modify a customer fields. Returns True if modified."""
    customers = load_customers()
    customer = _find_customer(customers, customer_id)
    if customer is None:
        _print_error(f"Customer '{customer_id}' not found.")
        return False

    new_name = customer.name if name is None else name
    new_email = customer.email if email is None else email

    try:
        updated = Customer(customer_id=customer.customer_id, name=new_name, email=new_email)
    except ValueError as exc:
        _print_error(str(exc))
        return False

    customers = [updated if c.customer_id == customer_id else c for c in customers]
    save_customers(customers)
    return True


# ----- Reservations logic -----
def _overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    """
    Two date ranges [start, end) overlap if start < other_end and other_start < end.
    End is exclusive to avoid double-counting check-out day.
    """
    return a_start < b_end and b_start < a_end


def _rooms_booked_for_hotel(
    reservations: list[Reservation],
    hotel_id: str,
    check_in: date,
    check_out: date,
) -> int:
    """Sum rooms booked for a hotel that overlap the given date range."""
    total = 0
    for res in reservations:
        if res.hotel_id != hotel_id:
            continue
        if _overlaps(res.check_in, res.check_out, check_in, check_out):
            total += res.rooms
    return total


def create_reservation(
    reservation_id: str,
    hotel_id: str,
    customer_id: str,
    check_in: date,
    check_out: date,
    rooms: int,
) -> bool:
    """
    Create a reservation if:
    - hotel exists
    - customer exists
    - reservation_id unique
    - enough rooms are available for the date range

    Returns True if created.
    """
    hotels = load_hotels()
    customers = load_customers()
    reservations = load_reservations()

    if _find_reservation(reservations, reservation_id) is not None:
        _print_error(f"Reservation '{reservation_id}' already exists.")
        return False

    hotel = _find_hotel(hotels, hotel_id)
    if hotel is None:
        _print_error(f"Hotel '{hotel_id}' not found.")
        return False

    customer = _find_customer(customers, customer_id)
    if customer is None:
        _print_error(f"Customer '{customer_id}' not found.")
        return False

    try:
        reservation = Reservation(
            reservation_id=reservation_id,
            hotel_id=hotel_id,
            customer_id=customer_id,
            check_in=check_in,
            check_out=check_out,
            rooms=rooms,
        )
    except ValueError as exc:
        _print_error(str(exc))
        return False

    already_booked = _rooms_booked_for_hotel(reservations, hotel_id, check_in, check_out)
    available = hotel.rooms_total - already_booked
    if reservation.rooms > available:
        _print_error(
            f"Not enough rooms available for hotel '{hotel_id}'. "
            f"Requested={reservation.rooms}, Available={available}."
        )
        return False

    reservations.append(reservation)
    save_reservations(reservations)
    return True


def cancel_reservation(reservation_id: str) -> bool:
    """Cancel (delete) a reservation. Returns True if deleted."""
    reservations = load_reservations()
    before = len(reservations)
    reservations = [r for r in reservations if r.reservation_id != reservation_id]

    if len(reservations) == before:
        _print_error(f"Reservation '{reservation_id}' not found.")
        return False

    save_reservations(reservations)
    return True