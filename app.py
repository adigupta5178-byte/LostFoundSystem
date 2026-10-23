from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("lostfound.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            lost_location TEXT NOT NULL,
            lost_date TEXT NOT NULL,
            description TEXT,
            contact_info TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Still Available'
        )
    """)

    columns = [
        row[1] for row in conn.execute("PRAGMA table_info(lost_items)")
    ]

    if "status" not in columns:
        conn.execute("""
            ALTER TABLE lost_items
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Still Available'
        """)

    conn.commit()
    conn.close()


def init_found_items_table():
    conn = sqlite3.connect("lostfound.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            found_location TEXT NOT NULL,
            found_date TEXT NOT NULL,
            description TEXT,
            contact_info TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Still Available'
        )
    """)

    columns = [
        row[1] for row in conn.execute("PRAGMA table_info(found_items)")
    ]

    if "status" not in columns:
        conn.execute("""
            ALTER TABLE found_items
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Still Available'
        """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/lost-item", methods=["GET", "POST"])
def lost_item():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        lost_location = request.form.get("lost_location", "").strip()
        lost_date = request.form.get("lost_date", "").strip()
        description = request.form.get("description", "").strip()
        contact_info = request.form.get("contact_info", "").strip()

        if not all([item_name, category, lost_location, lost_date, contact_info]):
            return "Please fill in all required fields.", 400

        conn = sqlite3.connect("lostfound.db")

        conn.execute("""
            INSERT INTO lost_items
            (item_name, category, lost_location, lost_date, description, contact_info)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item_name,
            category,
            lost_location,
            lost_date,
            description,
            contact_info
        ))

        conn.commit()
        conn.close()

        return "<h2>Lost item submitted successfully!</h2><a href='/'>Back to Home</a>"

    return render_template("lost_item.html")


@app.route("/found-item", methods=["GET", "POST"])
def found_item():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        found_location = request.form.get("found_location", "").strip()
        found_date = request.form.get("found_date", "").strip()
        description = request.form.get("description", "").strip()
        contact_info = request.form.get("contact_info", "").strip()

        if not all([item_name, category, found_location, found_date, contact_info]):
            return "Please fill in all required fields.", 400

        conn = sqlite3.connect("lostfound.db")

        conn.execute("""
            INSERT INTO found_items
            (item_name, category, found_location, found_date, description, contact_info)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item_name,
            category,
            found_location,
            found_date,
            description,
            contact_info
        ))

        conn.commit()
        conn.close()

        return "<h2>Found item submitted successfully!</h2><a href='/'>Back to Home</a>"

    return render_template("found_item.html")


@app.route("/view-lost-items")
def view_lost_items():
    conn = sqlite3.connect("lostfound.db")
    conn.row_factory = sqlite3.Row

    items = conn.execute(
        "SELECT * FROM lost_items ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("lost_items.html", items=items)


@app.route("/view-found-items")
def view_found_items():
    conn = sqlite3.connect("lostfound.db")
    conn.row_factory = sqlite3.Row

    items = conn.execute(
        "SELECT * FROM found_items ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("found_items.html", items=items)


@app.route("/update-status/<string:item_type>/<int:item_id>", methods=["POST"])
def update_status(item_type, item_id):
    if item_type not in ("lost", "found"):
        return "Invalid item type.", 400

    status = request.form.get("status", "")

    if status not in ("Still Available", "Returned"):
        return "Invalid status.", 400

    table = "lost_items" if item_type == "lost" else "found_items"

    conn = sqlite3.connect("lostfound.db")

    cursor = conn.execute(
        f"UPDATE {table} SET status = ? WHERE id = ?",
        (status, item_id)
    )

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return "Item not found.", 404

    list_page = "view_lost_items" if item_type == "lost" else "view_found_items"

    return redirect(url_for(list_page))


if __name__ == "__main__":
    init_db()
    init_found_items_table()
    app.run(debug=True)
