from fastmcp import FastMCP
import os
import json
import aiosqlite
import tempfile
from datetime import datetime

# --------------------------------------------------
# Paths (Cloud-safe)
# --------------------------------------------------

TEMP_DIR = tempfile.gettempdir()   # guaranteed writable
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")

print("Using database at:", DB_PATH)

mcp = FastMCP("ExpenseTracker")

# --------------------------------------------------
# Database Initialization (SYNC – once)
# --------------------------------------------------

def init_db():
    import sqlite3
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        db.commit()

init_db()

# --------------------------------------------------
# WRITE TOOL
# --------------------------------------------------

@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """Add a new expense entry (WRITE operation)."""

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO expenses (date, amount, category, subcategory, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (date, amount, category, subcategory, note)
            )
            await db.commit()

        return {
            "status": "success",
            "expense_id": cursor.lastrowid
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# READ TOOL
# --------------------------------------------------

@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    """Read expenses between two dates."""

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
            """,
            (start_date, end_date)
        )

        rows = await cursor.fetchall()
        cols = [c[0] for c in cursor.description]

        return [dict(zip(cols, row)) for row in rows]

# --------------------------------------------------
# READ-ONLY SUMMARY TOOL
# --------------------------------------------------

@mcp.tool()
async def summarize_expenses(start_date: str, end_date: str):
    """Summarize expenses by category."""

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date)
        )

        rows = await cursor.fetchall()
        return [
            {"category": r[0], "total": r[1], "count": r[2]}
            for r in rows
        ]

# --------------------------------------------------
# RESOURCE (Always read-only)
# --------------------------------------------------

@mcp.resource("expense:///categories", mime_type="application/json")
def categories():
    return json.dumps({
        "categories": [
            "Food",
            "Transport",
            "Shopping",
            "Education",
            "Bills",
            "Health",
            "Entertainment",
            "Other"
        ]
    }, indent=2)

# --------------------------------------------------
# Run Server
# --------------------------------------------------

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000)
