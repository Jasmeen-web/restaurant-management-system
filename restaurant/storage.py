"""File storage helpers for the restaurant application."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .models import CustomerOrder, MenuItem


class FileStorage:
    """Persists menu items and completed orders using flat files."""

    MENU_HEADERS = ["code", "name", "category", "price", "stock"]
    ORDER_HEADERS = [
        "order_id",
        "table_number",
        "server_name",
        "status",
        "created_at",
        "lines",
    ]

    def __init__(self, base_path: Path | str) -> None:
        self.base_path = Path(base_path)
        self.menu_path = self.base_path / "menu.csv"
        self.orders_path = self.base_path / "orders.csv"
        self.bills_path = self.base_path / "bills.txt"

    def ensure_storage_exists(self) -> None:
        """Create storage files with headers if they do not exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        if not self.menu_path.exists():
            with self.menu_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(self.MENU_HEADERS)
        if not self.orders_path.exists():
            with self.orders_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(self.ORDER_HEADERS)
        if not self.bills_path.exists():
            self.bills_path.write_text("", encoding="utf-8")

    def load_menu(self) -> List[MenuItem]:
        """Load all menu items from the CSV file."""
        self.ensure_storage_exists()
        with self.menu_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return [MenuItem.from_csv_row(row) for row in reader]

    def save_menu(self, items: Iterable[MenuItem]) -> None:
        """Write the full menu back to the CSV file."""
        self.ensure_storage_exists()
        with self.menu_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(self.MENU_HEADERS)
            for item in items:
                writer.writerow(item.to_csv_row())

    def load_orders(self) -> List[CustomerOrder]:
        """Load completed orders from CSV."""
        self.ensure_storage_exists()
        with self.orders_path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return [CustomerOrder.from_record(record) for record in reader]

    def append_order_record(self, order: CustomerOrder) -> None:
        """Append a completed order to the CSV file."""
        self.ensure_storage_exists()
        with self.orders_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    order.order_id,
                    order.table_number,
                    order.server_name,
                    order.status,
                    order.created_at,
                    order.serialize_lines(),
                ]
            )

    def append_bill_text(self, text: str) -> None:
        """Append a bill summary to the text archive."""
        self.ensure_storage_exists()
        with self.bills_path.open("a", encoding="utf-8") as handle:
            handle.write(text)
            handle.write("\n" + "=" * 60 + "\n")
