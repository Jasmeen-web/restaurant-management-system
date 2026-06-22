"""Business logic for the restaurant management system."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .exceptions import NotFoundError, ValidationError
from .models import Bill, CustomerOrder, MenuItem, OrderLine
from .storage import FileStorage


class RestaurantSystem:
    """Coordinates menu management, orders, billing, and reporting."""

    def __init__(self, data_path: Path | str) -> None:
        self.storage = FileStorage(data_path)
        self.menu_items: Dict[str, MenuItem] = {}
        self.active_orders: Dict[str, CustomerOrder] = {}
        self.completed_orders: List[CustomerOrder] = []

    def load_state(self) -> None:
        """Load menu items and historical orders from storage."""
        self.storage.ensure_storage_exists()
        self.menu_items = {item.code: item for item in self.storage.load_menu()}
        self.completed_orders = self.storage.load_orders()

    def seed_default_menu(self) -> None:
        """Create starter menu items if the menu is empty."""
        if self.menu_items:
            return
        for item in [
            MenuItem("M01", "Margherita Pizza", "Main Course", 10.99, 15),
            MenuItem("M02", "Veggie Burger", "Main Course", 8.75, 12),
            MenuItem("M03", "Caesar Salad", "Starter", 6.50, 10),
            MenuItem("M04", "Lemonade", "Beverage", 3.25, 30),
            MenuItem("M05", "Chocolate Cake", "Dessert", 4.95, 8),
        ]:
            self.menu_items[item.code] = item
        self.storage.save_menu(self.menu_items.values())

    def list_menu(self) -> List[MenuItem]:
        """Return the menu sorted by item code."""
        return sorted(self.menu_items.values(), key=lambda item: item.code)

    def add_menu_item(
        self, code: str, name: str, category: str, price: float, stock: int
    ) -> MenuItem:
        """Add a new menu item and persist the updated menu."""
        if code in self.menu_items:
            raise ValidationError(f"Menu code {code} already exists.")
        if stock < 0:
            raise ValidationError("Stock cannot be negative.")
        item = MenuItem(code.strip().upper(), name.strip(), category.strip(), price, stock)
        self.menu_items[item.code] = item
        self.storage.save_menu(self.menu_items.values())
        return item

    def restock_item(self, code: str, quantity: int) -> MenuItem:
        """Increase stock for an existing item."""
        item = self.get_menu_item(code)
        item.restock(quantity)
        self.storage.save_menu(self.menu_items.values())
        return item

    def get_menu_item(self, code: str) -> MenuItem:
        """Return a menu item by code."""
        lookup_code = code.strip().upper()
        if lookup_code not in self.menu_items:
            raise NotFoundError(f"Menu item {lookup_code} was not found.")
        return self.menu_items[lookup_code]

    def create_order(self, order_id: str, table_number: int, server_name: str) -> CustomerOrder:
        """Create a new active order."""
        order_key = order_id.strip().upper()
        if order_key in self.active_orders:
            raise ValidationError(f"Order {order_key} already exists.")
        if table_number <= 0:
            raise ValidationError("Table number must be greater than zero.")
        order = CustomerOrder(order_id=order_key, table_number=table_number, server_name=server_name.strip())
        self.active_orders[order_key] = order
        return order

    def add_item_to_order(self, order_id: str, item_code: str, quantity: int) -> CustomerOrder:
        """Add a menu item to an active order."""
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        order = self.get_order(order_id)
        item = self.get_menu_item(item_code)
        item.reserve_stock(quantity)
        order.add_line(OrderLine(item.code, item.name, item.price, quantity))
        self.storage.save_menu(self.menu_items.values())
        return order

    def get_order(self, order_id: str) -> CustomerOrder:
        """Return an active order by ID."""
        lookup_id = order_id.strip().upper()
        if lookup_id not in self.active_orders:
            raise NotFoundError(f"Order {lookup_id} does not exist.")
        return self.active_orders[lookup_id]

    def checkout_order(self, order_id: str) -> Bill:
        """Close an active order, persist it, and return the final bill."""
        order = self.get_order(order_id)
        order.mark_paid()
        bill = Bill(order)
        self.completed_orders.append(order)
        self.storage.append_order_record(order)
        self.storage.append_bill_text(bill.to_text())
        del self.active_orders[order.order_id]
        return bill

    def generate_sales_report(self) -> dict[str, float | int]:
        """Generate a simple sales summary for completed orders."""
        total_revenue = 0.0
        total_items = 0
        for order in self.completed_orders:
            bill = Bill(order)
            total_revenue += bill.calculate_total()
            total_items += order.get_total_items()
        return {
            "completed_orders": len(self.completed_orders),
            "items_sold": total_items,
            "total_revenue": round(total_revenue, 2),
        }
