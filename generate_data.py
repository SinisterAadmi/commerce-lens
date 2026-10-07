"""Reproducible synthetic demo data; never presented as real commerce data."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

CITIES = {
    "Mumbai": ("Maharashtra", 19.076, 72.878),
    "Pune": ("Maharashtra", 18.520, 73.857),
    "Delhi": ("Delhi", 28.614, 77.209),
    "Bengaluru": ("Karnataka", 12.972, 77.595),
    "Chennai": ("Tamil Nadu", 13.083, 80.271),
    "Hyderabad": ("Telangana", 17.385, 78.487),
    "Kolkata": ("West Bengal", 22.573, 88.364),
    "Ahmedabad": ("Gujarat", 23.023, 72.571),
    "Jaipur": ("Rajasthan", 26.912, 75.787),
    "Lucknow": ("Uttar Pradesh", 26.847, 80.946),
}
CATALOG = [
    ("Electronics", "Computers", "Laptop", 48000, .17),
    ("Electronics", "Audio", "Headphones", 2400, .32),
    ("Electronics", "Mobiles", "Smartphone", 18000, .19),
    ("Fashion", "Clothing", "T-shirt", 650, .46),
    ("Fashion", "Footwear", "Sneakers", 2600, .40),
    ("Fashion", "Accessories", "Backpack", 1400, .42),
    ("Home & Living", "Kitchen", "Cookware set", 3200, .35),
    ("Home & Living", "Decor", "Desk lamp", 1100, .38),
    ("Home & Living", "Furniture", "Office chair", 6500, .28),
    ("Beauty", "Skincare", "Moisturizer", 780, .48),
    ("Beauty", "Haircare", "Shampoo", 420, .44),
    ("Sports", "Fitness", "Yoga mat", 950, .39),
    ("Sports", "Equipment", "Cricket bat", 2800, .31),
]

def generate(rows=12000, seed=42):
    if rows < 1:
        raise ValueError("rows must be positive")
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", "2025-12-31")
    weights = np.where(dates.month.isin([10, 11]), 1.8, 1.0)
    dates = rng.choice(dates, rows, p=weights / weights.sum())
    items = [CATALOG[i] for i in rng.integers(0, len(CATALOG), rows)]
    cities = rng.choice(list(CITIES), rows, p=[.20,.09,.14,.14,.09,.10,.08,.06,.05,.05])
    prices = np.array([x[3] for x in items]) * rng.uniform(.9, 1.1, rows)
    quantity = rng.choice([1,2,3,4], rows, p=[.66,.23,.08,.03])
    discount = rng.choice([0,.05,.10,.15,.20,.30,.40], rows, p=[.28,.15,.20,.12,.13,.08,.04])
    revenue = prices * quantity * (1 - discount)
    costs = prices * quantity * (1 - np.array([x[4] for x in items]))
    return pd.DataFrame({
        "Order ID": [f"ORD-{i:07d}" for i in range(1, rows+1)],
        "Date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
        "Customer": [f"CUS-{i:05d}" for i in rng.integers(1, max(2, rows//3), rows)],
        "Product": [x[2] for x in items], "Category": [x[0] for x in items],
        "Subcategory": [x[1] for x in items], "Price": prices.round(2),
        "Quantity": quantity, "Discount": discount,
        "City": cities, "State": [CITIES[c][0] for c in cities],
        "Latitude": [CITIES[c][1] for c in cities], "Longitude": [CITIES[c][2] for c in cities],
        "Payment Method": rng.choice(["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Net Banking"], rows, p=[.42,.24,.14,.14,.06]),
        "Rating": rng.choice([1,2,3,4,5], rows, p=[.03,.06,.16,.37,.38]),
        "Profit": (revenue-costs-rng.uniform(25,150,rows)).round(2),
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--output", default=str(Path(__file__).parent / "data" / "sample_orders.csv"))
    args = parser.parse_args()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    generate(args.rows).to_csv(target, index=False)
    print(f"Created {args.rows:,} synthetic rows at {target}")
