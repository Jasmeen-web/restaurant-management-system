"""Domain models used by the restaurant application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List

from .exceptions import StockError, ValidationError


@dataclass
class MenuItem:
    """Represents a dish or drink that the restaurant can sell."""

    code: str
    name: str
    category: str
    price: float
    stock: int

    def update_price(self, new_price: float) -> None:
        """Update the selling price after validation."""
        if new_price <= 0:
            raise ValidationError("Price must be greater than zero.")
        self.price = round(new_price, 2)

    def has_stock(self, quantity: int) -> bool:
        """Return whether the requested quantity is available."""
        return quantity > 0 and self.stock >= quantity

    def reserve_stock(self, quantity: int) -> None:
        """Reduce stock when an order item is added."""
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if not self.has_stock(quantity):
            raise StockError(
                f"Not enough stock for {self.name}. Available: {self.stock}."
            )
        self.stock -= quantity

    def restock(self, quantity: int) -> None:
        """Increase stock when deliveries arrive."""
        if quantity <= 0:
            raise ValidationError("Restock quantity must be greater than zero.")
        self.stock += quantity

    def to_csv_row(self) -> list[str]:
        """Convert the menu item into a CSV-compatible row."""
        return [self.code, self.name, self.category, f"{self.price:.2f}", str(self.stock)]

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "MenuItem":
        """Create a menu item instance from CSV data."""
        try:
            return cls(
                code=row["code"].strip(),
                name=row["name"].strip(),
                category=row["category"].strip(),
                price=float(row["price"]),
                stock=int(row["stock"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid menu data: {row}") from exc


@dataclass
class OrderLine:
    """Represents a single ordered item within a customer order."""

    item_code: str
    item_name: str
    unit_price: float
    quantity: int

    def increase_quantity(self, amount: int) -> None:
        """Increase the quantity of the order line."""
        if amount <= 0:
            raise ValidationError("Increase amount must be greater than zero.")
        self.quantity += amount

    def decrease_quantity(self, amount: int) -> None:
        """Decrease the quantity of the order line."""
        if amount <= 0:
            raise ValidationError("Decrease amount must be greater than zero.")
        if amount >= self.quantity:
            raise ValidationError("Decrease amount must be smaller than quantity.")
        self.quantity -= amount

    def set_quantity(self, new_quantity: int) -> None:
        """Set a new quantity after validation."""
        if new_quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        self.quantity = new_quantity

    def line_total(self) -> float:
        """Return the line total for billing."""
        return round(self.unit_price * self.quantity, 2)

    def to_storage_value(self) -> str:
        """Serialize the line for CSV storage."""
        return (
            f"{self.item_code}|{self.item_name}|{self.unit_price:.2f}|{self.quantity}"
        )

    @classmethod
    def from_storage_value(cls, value: str) -> "OrderLine":
        """Deserialize a line from CSV storage."""
        parts = value.split("|")
        if len(parts) != 4:
            raise ValidationError(f"Invalid order line value: {value}")
        try:
            return cls(
                item_code=parts[0],
                item_name=parts[1],
                unit_price=float(parts[2]),
                quantity=int(parts[3]),
            )
        except ValueError as exc:
            raise ValidationError(f"Invalid order line value: {value}") from exc


@dataclass
class CustomerOrder:
    """Represents an order placed by a restaurant table."""

    order_id: str
    table_number: int
    server_name: str
    status: str = "OPEN"
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    lines: List[OrderLine] = field(default_factory=list)

    def add_line(self, new_line: OrderLine) -> None:
        """Add a new line or merge it with an existing line."""
        for line in self.lines:
            if line.item_code == new_line.item_code:
                line.increase_quantity(new_line.quantity)
                return
        self.lines.append(new_line)

    def remove_line(self, item_code: str) -> None:
        """Remove a line item from the order."""
        for index, line in enumerate(self.lines):
            if line.item_code == item_code:
                self.lines.pop(index)
                return
        raise ValidationError(f"Item {item_code} is not part of this order.")

    def get_total_items(self) -> int:
        """Return the total quantity of ordered items."""
        return sum(line.quantity for line in self.lines)

    def calculate_subtotal(self) -> float:
        """Return the subtotal before tax and service charge."""
        return round(sum(line.line_total() for line in self.lines), 2)

    def mark_paid(self) -> None:
        """Mark the order as completed."""
        if not self.lines:
            raise ValidationError("Cannot close an empty order.")
        self.status = "PAID"

    def serialize_lines(self) -> str:
        """Serialize all lines for CSV storage."""
        return ";;".join(line.to_storage_value() for line in self.lines)

    @classmethod
    def from_record(cls, record: dict[str, str]) -> "CustomerOrder":
        """Create an order from CSV data."""
        try:
            order = cls(
                order_id=record["order_id"],
                table_number=int(record["table_number"]),
                server_name=record["server_name"],
                status=record["status"],
                created_at=record["created_at"],
            )
            raw_lines = record.get("lines", "").strip()
            if raw_lines:
                order.lines = [
                    OrderLine.from_storage_value(value)
                    for value in raw_lines.split(";;")
                    if value
                ]
            return order
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid order record: {record}") from exc


@dataclass
class Bill:
    """Calculates charges for a completed order."""

    order: CustomerOrder
    tax_rate: float = 0.07
    service_rate: float = 0.05

    def calculate_tax(self) -> float:
        """Return the sales tax amount."""
        return round(self.order.calculate_subtotal() * self.tax_rate, 2)

    def calculate_service_charge(self) -> float:
        """Return the service charge amount."""
        return round(self.order.calculate_subtotal() * self.service_rate, 2)

    def calculate_total(self) -> float:
        """Return the grand total."""
        subtotal = self.order.calculate_subtotal()
        return round(subtotal + self.calculate_tax() + self.calculate_service_charge(), 2)

    def build_lines(self) -> Iterable[str]:
        """Build readable bill lines."""
        yield f"Bill for Order {self.order.order_id} - Table {self.order.table_number}"
        yield f"Server: {self.order.server_name}"
        yield "-" * 48
        for line in self.order.lines:
            yield (
                f"{line.item_name} x{line.quantity} @ ${line.unit_price:.2f}"
                f" = ${line.line_total():.2f}"
            )
        yield "-" * 48
        yield f"Subtotal: ${self.order.calculate_subtotal():.2f}"
        yield f"Tax (7%): ${self.calculate_tax():.2f}"
        yield f"Service Charge (5%): ${self.calculate_service_charge():.2f}"
        yield f"Grand Total: ${self.calculate_total():.2f}"

    def to_text(self) -> str:
        """Return the bill as a formatted text block."""
        return "\n".join(self.build_lines())
