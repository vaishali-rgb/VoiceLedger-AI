import sqlite3
import os
from datetime import date, datetime

os.makedirs("data", exist_ok=True)
DB_PATH = "data/voiceledger.db"


def init_db():
    """Create all tables if they don't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Transactions: every sale or expense
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      TEXT    NOT NULL,
            time      TEXT    NOT NULL,
            type      TEXT    NOT NULL,   -- 'sale' or 'expense'
            item      TEXT    NOT NULL,
            item_hindi TEXT,
            quantity  REAL,
            unit      TEXT,
            price     REAL    NOT NULL
        )
    """)

    # Inventory: current stock levels
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            item                TEXT    UNIQUE NOT NULL,
            item_hindi          TEXT,
            stock_qty           REAL    DEFAULT 0,
            unit                TEXT,
            low_stock_threshold REAL    DEFAULT 5
        )
    """)

    conn.commit()
    conn.close()


def save_transaction(type_: str, item: str, item_hindi: str,
                     quantity, unit: str, price: float):
    """Insert a new sale or expense into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now()
    c.execute("""
        INSERT INTO transactions
            (date, time, type, item, item_hindi, quantity, unit, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        type_, item, item_hindi, quantity, unit, price
    ))

    # Auto-update inventory for sales (deduct stock)
    if type_ == "sale" and quantity:
        c.execute("""
            INSERT INTO inventory (item, item_hindi, stock_qty, unit)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item) DO UPDATE SET
                stock_qty = MAX(0, stock_qty - excluded.stock_qty)
        """, (item, item_hindi, quantity, unit))

    # Auto-update inventory for purchases (add stock)
    if type_ == "expense" and quantity:
        c.execute("""
            INSERT INTO inventory (item, item_hindi, stock_qty, unit)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item) DO UPDATE SET
                stock_qty = stock_qty + excluded.stock_qty
        """, (item, item_hindi, quantity, unit))

    conn.commit()
    conn.close()


def get_todays_summary() -> str:
    """Return today's sales, expenses, profit and recent transactions as text."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = date.today().strftime("%Y-%m-%d")

    c.execute("SELECT COALESCE(SUM(price),0) FROM transactions WHERE date=? AND type='sale'", (today,))
    total_sales = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(price),0) FROM transactions WHERE date=? AND type='expense'", (today,))
    total_expenses = c.fetchone()[0]

    profit = total_sales - total_expenses

    c.execute("""
        SELECT time, type, item_hindi, quantity, unit, price
        FROM transactions WHERE date=?
        ORDER BY id DESC LIMIT 10
    """, (today,))
    rows = c.fetchall()
    conn.close()

    lines = []
    for row in rows:
        t, typ, name, qty, unit, price = row
        emoji = "💰" if typ == "sale" else "💸"
        qty_str = f"{qty} {unit}" if qty else ""
        lines.append(f"  {emoji} [{t}] {typ.upper()}: {name} {qty_str} = ₹{price:.0f}")

    transactions_block = "\n".join(lines) if lines else "  (No transactions yet today)"

    return f"""
📅 Date: {today}
━━━━━━━━━━━━━━━━━━━━━━
💰 Total Sales:     ₹{total_sales:.2f}
💸 Total Expenses:  ₹{total_expenses:.2f}
📈 Net Profit:      ₹{profit:.2f}
━━━━━━━━━━━━━━━━━━━━━━
Recent Transactions:
{transactions_block}
"""


def get_low_stock_items(threshold_multiplier=1.0) -> list:
    """Return inventory items that are at or below their low-stock threshold."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT item, item_hindi, stock_qty, unit, low_stock_threshold
        FROM inventory
        WHERE stock_qty <= low_stock_threshold * ?
        ORDER BY stock_qty ASC
    """, (threshold_multiplier,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_transactions(limit=50) -> list:
    """Return recent transactions for display in UI."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT date, time, type, item_hindi, quantity, unit, price
        FROM transactions ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_inventory() -> list:
    """Return full inventory list."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT item_hindi, item, stock_qty, unit, low_stock_threshold FROM inventory ORDER BY item")
    rows = c.fetchall()
    conn.close()
    return rows
