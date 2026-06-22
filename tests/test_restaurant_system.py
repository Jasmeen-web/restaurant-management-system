"""Automated tests for the restaurant management system."""

from pathlib import Path

from restaurant.system import RestaurantSystem


def build_system(tmp_path: Path) -> RestaurantSystem:
    """Create a test system with seeded sample data."""
    system = RestaurantSystem(tmp_path)
    system.load_state()
    system.seed_default_menu()
    return system


def test_seeded_menu_contains_items(tmp_path: Path) -> None:
    """The seeded menu should create starter items."""
    system = build_system(tmp_path)
    assert len(system.list_menu()) >= 5


def test_create_order_and_checkout(tmp_path: Path) -> None:
    """Orders should move from active to completed on checkout."""
    system = build_system(tmp_path)
    system.create_order("ORD1", 2, "Alice")
    system.add_item_to_order("ORD1", "M01", 2)
    system.add_item_to_order("ORD1", "M04", 1)

    bill = system.checkout_order("ORD1")

    assert bill.calculate_total() > 0
    assert "ORD1" not in system.active_orders
    assert len(system.completed_orders) == 1


def test_sales_report_aggregates_revenue(tmp_path: Path) -> None:
    """The sales report should summarize completed orders."""
    system = build_system(tmp_path)
    system.create_order("ORD2", 5, "Nina")
    system.add_item_to_order("ORD2", "M02", 1)
    system.checkout_order("ORD2")

    report = system.generate_sales_report()

    assert report["completed_orders"] == 1
    assert report["items_sold"] == 1
    assert report["total_revenue"] > 0
