# Restaurant Management System

## Project Title and Purpose

This project is a menu-driven Python application for a small restaurant. It helps staff manage menu items, create table orders, update stock, produce bills, and review a simple sales report. The purpose is to demonstrate fundamental Python programming concepts in a realistic business scenario.

## Installation and Execution

1. Make sure Python 3.11 or a compatible version is installed.
2. Open a terminal in the project folder.
3. Run the application with:

```powershell
py -3.11 main.py
```

4. Run the automated tests with:

```powershell
py -3.11 -m pytest
```

## Example Usage

1. Choose `4` to create a new order.
2. Choose `5` to add menu items to that order.
3. Choose `6` to review the current order subtotal.
4. Choose `7` to checkout and print the final bill.
5. Choose `8` to view the sales report for completed orders.

## Key Features

- Menu management for adding and restocking food or drink items
- Table order creation with multiple ordered items
- Automatic stock reduction when items are sold
- Bill generation with tax and service charge calculations
- Sales reporting based on completed orders
- Flat-file persistence using CSV and text files

## Files

- `main.py`: console interface
- `restaurant/models.py`: domain classes
- `restaurant/system.py`: business logic
- `restaurant/storage.py`: file input and output
- `restaurant/exceptions.py`: custom exceptions
- `data/menu.csv`: menu storage
- `data/orders.csv`: completed order storage
- `data/bills.txt`: archived bill output
- `tests/test_restaurant_system.py`: automated tests
