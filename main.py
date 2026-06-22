"""Console entry point for the restaurant management system."""

from __future__ import annotations

from pathlib import Path

from restaurant import NotFoundError, RestaurantSystem, StockError, ValidationError


def print_header(title: str) -> None:
    """Print a section header for the console interface."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def show_menu_items(system: RestaurantSystem) -> None:
    """Display the current restaurant menu."""
    print_header("Restaurant Menu")
    for item in system.list_menu():
        print(
            f"{item.code:<4} | {item.name:<20} | {item.category:<12} | "
            f"${item.price:>6.2f} | Stock: {item.stock}"
        )


def show_order(system: RestaurantSystem) -> None:
    """Display a selected active order."""
    order_id = input("Enter order ID: ").strip().upper()
    order = system.get_order(order_id)
    print_header(f"Order {order.order_id} for Table {order.table_number}")
    if not order.lines:
        print("This order has no items yet.")
        return
    for line in order.lines:
        print(
            f"{line.item_code:<4} | {line.item_name:<20} | "
            f"Qty: {line.quantity:<2} | ${line.line_total():.2f}"
        )
    print(f"Subtotal: ${order.calculate_subtotal():.2f}")


def prompt_float(label: str) -> float:
    """Read a floating-point number from the user."""
    return float(input(label).strip())


def prompt_int(label: str) -> int:
    """Read an integer from the user."""
    return int(input(label).strip())


def main() -> None:
    """Run the menu-driven restaurant management system."""
    data_path = Path(__file__).resolve().parent / "data"
    system = RestaurantSystem(data_path)
    system.load_state()
    system.seed_default_menu()

    actions = {
        "1": "View menu",
        "2": "Add menu item",
        "3": "Restock menu item",
        "4": "Create order",
        "5": "Add item to order",
        "6": "View active order",
        "7": "Checkout order",
        "8": "View sales report",
        "9": "Exit",
    }

    while True:
        print_header("Restaurant Management System")
        for key, label in actions.items():
            print(f"{key}. {label}")

        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                show_menu_items(system)
            elif choice == "2":
                code = input("Code: ")
                name = input("Name: ")
                category = input("Category: ")
                price = prompt_float("Price: ")
                stock = prompt_int("Opening stock: ")
                item = system.add_menu_item(code, name, category, price, stock)
                print(f"Added {item.name} successfully.")
            elif choice == "3":
                code = input("Menu code to restock: ")
                quantity = prompt_int("Additional stock: ")
                item = system.restock_item(code, quantity)
                print(f"{item.name} now has stock level {item.stock}.")
            elif choice == "4":
                order_id = input("New order ID: ")
                table_number = prompt_int("Table number: ")
                server_name = input("Server name: ")
                order = system.create_order(order_id, table_number, server_name)
                print(f"Created order {order.order_id} for table {order.table_number}.")
            elif choice == "5":
                order_id = input("Order ID: ")
                item_code = input("Menu item code: ")
                quantity = prompt_int("Quantity: ")
                order = system.add_item_to_order(order_id, item_code, quantity)
                print(
                    f"Order {order.order_id} updated. "
                    f"Subtotal: ${order.calculate_subtotal():.2f}"
                )
            elif choice == "6":
                show_order(system)
            elif choice == "7":
                order_id = input("Order ID to checkout: ")
                bill = system.checkout_order(order_id)
                print_header("Final Bill")
                print(bill.to_text())
            elif choice == "8":
                report = system.generate_sales_report()
                print_header("Sales Report")
                print(f"Completed Orders: {report['completed_orders']}")
                print(f"Items Sold: {report['items_sold']}")
                print(f"Total Revenue: ${report['total_revenue']:.2f}")
            elif choice == "9":
                print("Exiting system. Goodbye.")
                break
            else:
                print("Please choose a valid option from the menu.")
        except (ValidationError, NotFoundError, StockError, ValueError) as exc:
            print(f"Error: {exc}")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
