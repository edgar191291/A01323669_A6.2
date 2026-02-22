# pylint: disable=missing-function-docstring,too-many-public-methods,consider-using-with
# !/usr/bin/env python3
"""
test_services.py

Unit tests for services.py using temporary JSON files.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from src import services


class ServicesTestCase(unittest.TestCase):
    """Tests for core CRUD and reservation logic."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp_dir.name)

        self.hotels = self.data_dir / "hotels.json"
        self.customers = self.data_dir / "customers.json"
        self.reservations = self.data_dir / "reservations.json"

        self.hotels.write_text("[]", encoding="utf-8")
        self.customers.write_text("[]", encoding="utf-8")
        self.reservations.write_text("[]", encoding="utf-8")

        # Patch services module paths to point to temp files
        self.patches = [
            patch.object(services, "_DATA_DIR", self.data_dir),
            patch.object(services, "_HOTELS_PATH", self.hotels),
            patch.object(services, "_CUSTOMERS_PATH", self.customers),
            patch.object(services, "_RESERVATIONS_PATH", self.reservations),
        ]
        for p in self.patches:
            p.start()

        self.stderr_patch = patch("sys.stderr", new=StringIO())
        self.stderr_patch.start()

    def tearDown(self) -> None:
        for p in self.patches:
            p.stop()
        self.tmp_dir.cleanup()
        self.stderr_patch.stop()

    def test_create_and_display_hotel(self) -> None:
        ok = services.create_hotel("H1", "Hotel Uno", 10)
        self.assertTrue(ok)

        data = services.display_hotel("H1")
        self.assertIsNotNone(data)
        self.assertEqual(data["hotel_id"], "H1")
        self.assertEqual(data["rooms_total"], 10)

    def test_create_duplicate_hotel_returns_false(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertFalse(services.create_hotel("H1", "Hotel Uno", 10))

    def test_modify_hotel(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertTrue(services.modify_hotel("H1", name="Hotel 1", rooms_total=12))

        data = services.display_hotel("H1")
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Hotel 1")
        self.assertEqual(data["rooms_total"], 12)

    def test_delete_hotel(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertTrue(services.delete_hotel("H1"))
        self.assertIsNone(services.display_hotel("H1"))

    def test_create_and_display_customer(self) -> None:
        ok = services.create_customer("C1", "Edgar", "edgar@example.com")
        self.assertTrue(ok)

        data = services.display_customer("C1")
        self.assertIsNotNone(data)
        self.assertEqual(data["customer_id"], "C1")

    def test_modify_customer(self) -> None:
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))
        self.assertTrue(services.modify_customer("C1", name="Edgar Rosas"))

        data = services.display_customer("C1")
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Edgar Rosas")

    def test_delete_customer(self) -> None:
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))
        self.assertTrue(services.delete_customer("C1"))
        self.assertIsNone(services.display_customer("C1"))

    def test_create_reservation_success(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))

        ok = services.create_reservation(
            reservation_id="R1",
            hotel_id="H1",
            customer_id="C1",
            check_in=date(2026, 3, 1),
            check_out=date(2026, 3, 5),
            rooms=3,
        )
        self.assertTrue(ok)

    def test_create_reservation_fails_if_not_enough_rooms(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 3))
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))

        self.assertTrue(
            services.create_reservation(
                reservation_id="R1",
                hotel_id="H1",
                customer_id="C1",
                check_in=date(2026, 3, 1),
                check_out=date(2026, 3, 5),
                rooms=3,
            )
        )

        # Overlapping reservation should fail due to capacity
        self.assertFalse(
            services.create_reservation(
                reservation_id="R2",
                hotel_id="H1",
                customer_id="C1",
                check_in=date(2026, 3, 2),
                check_out=date(2026, 3, 4),
                rooms=1,
            )
        )

    def test_cancel_reservation(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))
        self.assertTrue(
            services.create_reservation(
                reservation_id="R1",
                hotel_id="H1",
                customer_id="C1",
                check_in=date(2026, 3, 1),
                check_out=date(2026, 3, 5),
                rooms=3,
            )
        )
        self.assertTrue(services.cancel_reservation("R1"))
        self.assertFalse(services.cancel_reservation("R1"))

    def test_read_json_with_invalid_content_returns_empty_list(self) -> None:
        # Put invalid JSON in hotels file and ensure services continues
        self.hotels.write_text("{bad json", encoding="utf-8")
        hotels = services.load_hotels()
        self.assertEqual(hotels, [])

    def test_read_json_with_bom_is_accepted(self) -> None:
        # Write UTF-8 BOM + [] and ensure no crash
        bom = "\ufeff"
        self.hotels.write_text(bom + "[]", encoding="utf-8")
        hotels = services.load_hotels()
        self.assertEqual(hotels, [])
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))

    def test_storage_filters_non_dict_items(self) -> None:
        payload = [{"hotel_id": "H1", "name": "Hotel Uno", "rooms_total": 10}, 123, "x"]
        self.hotels.write_text(json.dumps(payload), encoding="utf-8")
        hotels = services.load_hotels()
        self.assertEqual(len(hotels), 1)
        self.assertEqual(hotels[0].hotel_id, "H1")

    def test_create_hotel_invalid_rooms_returns_false(self) -> None:
        self.assertFalse(services.create_hotel("H1", "Hotel Uno", 0))

    def test_modify_hotel_not_found_returns_false(self) -> None:
        self.assertFalse(services.modify_hotel("H404", name="X"))

    def test_create_customer_invalid_email_returns_false(self) -> None:
        self.assertFalse(services.create_customer("C1", "Edgar", "not-an-email"))

    def test_create_reservation_fails_when_hotel_missing(self) -> None:
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))
        self.assertFalse(
            services.create_reservation(
                reservation_id="R1",
                hotel_id="H404",
                customer_id="C1",
                check_in=date(2026, 3, 1),
                check_out=date(2026, 3, 5),
                rooms=1,
            )
        )

    def test_create_reservation_fails_when_customer_missing(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertFalse(
            services.create_reservation(
                reservation_id="R1",
                hotel_id="H1",
                customer_id="C404",
                check_in=date(2026, 3, 1),
                check_out=date(2026, 3, 5),
                rooms=1,
            )
        )

    def test_create_reservation_invalid_dates_returns_false(self) -> None:
        self.assertTrue(services.create_hotel("H1", "Hotel Uno", 10))
        self.assertTrue(services.create_customer("C1", "Edgar", "edgar@example.com"))
        self.assertFalse(
            services.create_reservation(
                reservation_id="R1",
                hotel_id="H1",
                customer_id="C1",
                check_in=date(2026, 3, 5),
                check_out=date(2026, 3, 5),
                rooms=1,
            )
        )


if __name__ == "__main__":
    unittest.main()
