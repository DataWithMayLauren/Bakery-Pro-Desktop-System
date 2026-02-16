# 🥖 Bakery Pro: Smart Inventory & Sales System

An advanced, stable Point of Sale (POS) and Inventory Management System built specifically for artisan bakeries. This system features real-time ledger tracking, ingredient-to-product recipe linking, and automated financial reporting.

✨ Key Features
📊 Dynamic Dashboard: Real-time tracking of Today's Sales, Monthly Revenue, Expenses, and Net Profit.

📅 Pre-Order System: Log customer reservations with pickup dates directly into the ledger.

🍳 Recipe Linker: Automatically deducts raw materials (flour, sugar, eggs) when a finished product is sold.

📜 Official Ledger: Generates professional .txt monthly reports in the required format: Date | Item | Qty | Total.

💹 Costing Analysis: Export detailed profit margin reports to see which bakes are "Healthy" or "Low Margin."

🛡️ Auto-Backup: Creates timestamped backups of all CSV databases every time the app starts.

🚀 Getting Started
Prerequisites
Python 3.10+

Dependencies: Install required libraries via terminal:

Bash
pip install customtkinter pandas pillow
Installation
Clone this repository or download the ZIP.

Ensure your logo.png is in the same folder as the script.

Run the application:

Bash
python bakery_system.py
📂 File Structure
bakery_inventory.csv: Finished products and pricing.

ingredients.csv: Raw materials and admin expenses.

sales_records.csv: Historical sales data.

pre_orders.csv: Customer reservations.

recipes.json: Links ingredients to products.

/backups/: Auto-generated safety copies of your data.

🛠️ Tech Stack
Frontend: CustomTkinter (Modern UI/UX)

Backend: Python 3.12

Database: CSV & JSON (Lightweight & Portable)

Data Processing: Pandas
