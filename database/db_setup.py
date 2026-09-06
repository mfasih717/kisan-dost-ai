import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "kisan_dost.db")


def get_connection():
    """Return a connection to the Kisan Dost SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        season TEXT NOT NULL,
        soil_type TEXT NOT NULL,
        water_requirement TEXT NOT NULL,
        expected_yield_per_acre REAL,
        expected_profit_per_acre REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fertilizer_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        urea_bags_per_acre REAL,
        dap_bags_per_acre REAL,
        urea_price_per_bag REAL,
        dap_price_per_bag REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mandi_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        district TEXT NOT NULL,
        price_per_maund REAL,
        date_recorded TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pest_disease (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        symptom_keywords TEXT NOT NULL,
        pest_name TEXT NOT NULL,
        treatment TEXT NOT NULL,
        safe_dosage TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmer_profiles (
        session_id TEXT PRIMARY KEY,
        district TEXT,
        land_size_acres REAL,
        current_crop TEXT,
        last_updated TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Avoid duplicate seeding
    cursor.execute("SELECT COUNT(*) FROM crops")
    if cursor.fetchone()[0] > 0:
        print("Data already seeded, skipping.")
        conn.close()
        return

    crops = [
        ("Wheat", "Rabi", "loamy", "medium", 40, 60000),
        ("Cotton", "Kharif", "sandy", "high", 25, 90000),
        ("Rice", "Kharif", "clay", "high", 35, 75000),
        ("Maize", "Kharif", "loamy", "medium", 45, 65000),
        ("Chickpea (Chana)", "Rabi", "sandy", "low", 15, 50000),
        ("Sugarcane", "Kharif", "loamy", "high", 500, 120000),
    ]
    cursor.executemany("""
        INSERT INTO crops (crop_name, season, soil_type, water_requirement, expected_yield_per_acre, expected_profit_per_acre)
        VALUES (?, ?, ?, ?, ?, ?)
    """, crops)

    fertilizer = [
        ("Wheat", 2.0, 1.5, 3200, 5800),
        ("Cotton", 3.0, 2.0, 3200, 5800),
        ("Rice", 2.5, 1.5, 3200, 5800),
        ("Maize", 2.5, 1.5, 3200, 5800),
        ("Chickpea (Chana)", 0.5, 1.0, 3200, 5800),
        ("Sugarcane", 4.0, 2.5, 3200, 5800),
    ]
    cursor.executemany("""
        INSERT INTO fertilizer_rates (crop_name, urea_bags_per_acre, dap_bags_per_acre, urea_price_per_bag, dap_price_per_bag)
        VALUES (?, ?, ?, ?, ?)
    """, fertilizer)

    mandi = [
        ("Wheat", "Multan", 3100, "2026-09-01"),
        ("Wheat", "Faisalabad", 3050, "2026-09-01"),
        ("Cotton", "Multan", 8500, "2026-09-01"),
        ("Cotton", "Sahiwal", 8300, "2026-09-01"),
        ("Rice", "Sheikhupura", 4200, "2026-09-01"),
        ("Maize", "Faisalabad", 2800, "2026-09-01"),
    ]
    cursor.executemany("""
        INSERT INTO mandi_prices (crop_name, district, price_per_maund, date_recorded)
        VALUES (?, ?, ?, ?)
    """, mandi)

    pests = [
        ("Cotton", "leaves curling, tiny white insects", "Whitefly",
         "Spray Imidacloprid-based insecticide", "0.5 ml per liter of water, max 2 sprays per season"),
        ("Wheat", "yellow stripes on leaves, rust colored spots", "Yellow Rust",
         "Apply Propiconazole fungicide", "1 ml per liter of water"),
        ("Rice", "small brown spots on leaves, stem weakening", "Brown Spot Disease",
         "Apply Mancozeb fungicide", "2 grams per liter of water"),
        ("Maize", "holes in leaves, caterpillar visible", "Fall Armyworm",
         "Spray Emamectin Benzoate", "0.4 grams per liter of water"),
    ]
    cursor.executemany("""
        INSERT INTO pest_disease (crop_name, symptom_keywords, pest_name, treatment, safe_dosage)
        VALUES (?, ?, ?, ?, ?)
    """, pests)

    conn.commit()
    conn.close()
    print("Sample data seeded successfully.")


if __name__ == "__main__":
    create_tables()
    seed_data()