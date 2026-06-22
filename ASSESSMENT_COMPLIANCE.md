# Assessment Compliance Check

## Technical Requirement Check

1. Classes and Objects: Passed. The project contains `MenuItem`, `OrderLine`, `CustomerOrder`, `Bill`, `FileStorage`, and `RestaurantSystem`.
2. Methods: Passed. Each main class has at least four meaningful methods.
3. Control Structures: Passed. The program uses loops and conditional statements in the console menu, reporting, and data processing.
4. Data Handling: Passed. The system reads and writes `menu.csv`, `orders.csv`, and `bills.txt`.
5. Exception Handling: Passed. The project uses `ValidationError`, `NotFoundError`, and `StockError`, and catches them in the interface.
6. Modules and Packages: Passed. The code is split across multiple Python files inside the `restaurant` package.
7. Code Style: Passed. The code uses clear naming, docstrings, modular structure, and is written to follow PEP 8 style closely.

## Deliverables Check

1. Interactive Python Program: Passed. The application provides a menu-driven restaurant workflow.
2. GitHub Repository Content: Prepared locally. The folder contains source code, sample data, and `README.md`, but you still need to upload it to GitHub and place the final repository link into the report.
3. Written Report Sections: Passed. The report includes Introduction, System Design, Implementation Overview, Testing and Demonstration, and Reflection.
4. Screenshot Placeholders: Passed. The report includes figure placeholders where screenshots can be inserted.
5. Report Format: Passed. The generated `.docx` uses Times New Roman with title size 16, heading size 14, subheading size 13, normal text size 12, and justified body text.
6. PDF Version: Passed. A PDF export of the report has been generated.

## Verification Run

- Automated tests: `py -3.11 -m pytest`
- Result: `3 passed`
- Manual demo: order creation, item addition, checkout, and bill generation completed successfully
