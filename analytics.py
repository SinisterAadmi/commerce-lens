"""Validation and aggregations, independent of the presentation layer."""
import numpy as np
import pandas as pd
from generate_data import CITIES

REQUIRED = ["Order ID", "Date", "Customer", "Product", "Category", "Price", "Quantity", "City", "State", "Payment Method", "Profit"]

def clean_data(raw):
    df = raw.copy()
    df.columns = df.columns.str.strip()
    if df.columns.duplicated().any():
        raise ValueError("Column names must be unique after trimming whitespace.")
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    report = {"Input rows": len(df)}
    df = df.drop_duplicates()
    report["Exact duplicates removed"] = report["Input rows"] - len(df)
    for col in ["Order ID", "Customer", "Product", "Category", "City", "State", "Payment Method"]:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True).dt.tz_convert(None).dt.normalize()
    for col in ["Price", "Quantity", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    has_discount = "Discount" in df
    if not has_discount:
        df["Discount"] = 0.0
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce")
    valid = df[REQUIRED].notna().all(axis=1) & (df.Price >= 0) & (df.Quantity > 0) & (df.Quantity % 1 == 0) & df.Discount.between(0,1)
    report["Invalid rows removed"] = int((~valid).sum())
    df = df.loc[valid].copy()
    if df.empty:
        raise ValueError("No valid rows remain. Check dates, required fields, numeric values, and Discount fractions (0 to 1).")
    # Repeated IDs may be separate order lines. Keep them and count distinct orders.
    if "Subcategory" not in df:
        df["Subcategory"] = df["Product"]
    df["Subcategory"] = df.Subcategory.astype("string").fillna("Unknown").replace("", "Unknown")
    if "Rating" in df:
        df["Rating"] = pd.to_numeric(df.Rating, errors="coerce").where(lambda x: x.between(1,5))
    else:
        df["Rating"] = np.nan
    for col, index in [("Latitude",1),("Longitude",2)]:
        known = df.City.map({c: v[index] for c,v in CITIES.items()})
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(known) if col in df else known
    valid_coords = df.Latitude.between(-90,90) & df.Longitude.between(-180,180)
    df.loc[~valid_coords, ["Latitude","Longitude"]] = np.nan
    df["Revenue"] = (df.Price * df.Quantity * (1-df.Discount)).round(2)
    df["Month"] = df.Date.dt.to_period("M").astype(str)
    df["Weekday"] = df.Date.dt.dayofweek
    report["Valid rows"] = len(df)
    report["Rows without map coordinates"] = int(df.Latitude.isna().sum())
    report["Discount supplied"] = has_discount
    return df, report

def metrics(df):
    revenue = float(df.Revenue.sum())
    orders = int(df["Order ID"].nunique())
    return {"revenue": revenue, "profit": float(df.Profit.sum()), "orders": orders,
            "aov": revenue/orders if orders else 0, "margin": df.Profit.sum()/revenue if revenue else 0}

def insights(df, has_discount=True):
    m = metrics(df)
    categories = df.groupby("Category").Revenue.sum().sort_values(ascending=False)
    cities = df.groupby("City")["Order ID"].nunique().sort_values(ascending=False)
    months = df.groupby("Month").Revenue.sum().sort_values(ascending=False)
    lines = [f"{categories.index[0]} leads revenue at ₹{categories.iloc[0]:,.0f}" + (f" ({categories.iloc[0]/m['revenue']:.1%} of the selected total)." if m['revenue'] else "."),
             f"{cities.index[0]} has the most distinct orders in this selection ({cities.iloc[0]:,}).",
             f"{months.index[0]} is the highest revenue month at ₹{months.iloc[0]:,.0f}. Partial months and unequal coverage can affect this ranking.",
             f"{(df.Profit < 0).mean():.1%} of order lines are loss-making; overall profit margin is {m['margin']:.1%}."]
    if has_discount and df.Discount.nunique() > 1 and df.Profit.nunique() > 1 and len(df) > 2:
        correlation = df.Discount.corr(df.Profit)
        lines.append(f"Discount and line profit have Pearson correlation {correlation:.2f}. Product mix and order size can influence this association; it does not establish causation.")
    return lines
