# CommerceLens — E-Commerce Analytics Dashboard

A working college project for **Data Visualization: Types, Applications**, built with Python, Pandas, Plotly, and Streamlit. Includes eight visualization types, linked sidebar filters, descriptive findings, data quality checks, CSV upload/export, and an optional Spark aggregation script.

## Run on Windows

Install Python 3.11 or newer. Open PowerShell in this folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

The launcher creates a local virtual environment, installs dependencies, and opens Streamlit at http://localhost:8501. Internet is needed for first-time dependency installation and map tiles. The remaining charts operate locally. Stop with Ctrl+C.

Manual setup (also suitable for macOS/Linux; use `.venv/bin/python` there):

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

## Included files

- `app.py`: dashboard and filters
- `analytics.py`: cleaning, metrics, and findings
- `charts.py`: eight Plotly charts
- `generate_data.py`: deterministic synthetic dataset generator
- `data/sample_orders.csv`: 12,000 demo order lines (seed 42)
- `spark_aggregate.py`: optional distributed monthly/category aggregation
- `PROJECT_REPORT.md`: report draft, chart rationale, limitations, and viva notes
- `tests/test_project.py`: analytical correctness and interaction checks

## Upload your data

Choose **Upload CSV** in the sidebar. Headers are case-sensitive; surrounding whitespace is removed. Required fields:

```csv
Order ID,Date,Customer,Product,Category,Price,Quantity,City,State,Payment Method,Profit
ORD-1,2025-01-10,CUS-1,Laptop,Electronics,50000,1,Mumbai,Maharashtra,UPI,7000
```

Optional: `Discount`, `Subcategory`, `Rating`, `Latitude`, `Longitude`.

- **Price**: pre-discount unit price in INR; finite and nonnegative.
- **Quantity**: positive integer. Each row represents an order line.
- **Discount**: fraction such as `0.20` for 20%, not `20`. Defaults to zero when the column is absent; invalid/missing values in a supplied Discount column reject that row.
- **Profit**: finite signed line profit supplied by your data; losses are allowed.
- **Date**: ISO dates recommended. Timestamps convert to UTC dates.
- **Rating**: optional 1–5 numeric value; invalid values become missing.
- **Subcategory**: defaults to Product when absent.
- **Coordinates**: optional valid latitude/longitude. Missing coordinates use a lookup for the ten demo cities. Unknown cities without coordinates appear in other charts but are excluded from the map.

Repeated Order IDs are kept as separate lines. Exact duplicate rows are removed, so add a unique line identifier if otherwise identical lines are legitimate. AOV uses the selected lines of each order. City/payment distinct-order subtotals may overlap when an order spans groups.

Incoming Revenue columns are ignored: revenue is consistently calculated as `Price × Quantity × (1 − Discount)`. Taxes, shipping revenue, refunds, and exchange rates are outside this model. Required missing fields, invalid dates/numbers, negative prices, fractional/non-positive quantities, and invalid discounts cause row removal. The audit reports removals.

## Demo walkthrough

1. Review the five KPI cards and revenue trend.
2. Switch monthly to weekly trends; compare categories with products.
3. Filter dates, states, categories, and payment methods to show connected analysis.
4. Review payment share, the histogram, and discount–profit outliers.
5. Explore the bubble map and category/subcategory treemap.
6. Explain each chart using the caption below it.
7. Open Data & methodology to show cleaning, formulas, and the filtered table.
8. Export filtered data and findings.

Hover for details, zoom and pan, toggle chart legends, and export chart PNGs using the Plotly toolbar. Scatter rendering is capped at 5,000 reproducibly sampled lines. All KPI calculations and findings use the full filtered dataset.

## Data provenance and interpretation

The sample is **synthetic**, not a real customer dataset. It deliberately weights October/November dates more heavily and includes discounts, negative profits, repeat customers, and regional variation. Findings describe the generated data only. The dashboard makes no unsupported claim about festivals causing sales changes. Source code and seed make the sample reproducible.

Regenerate a larger sample:

```powershell
python generate_data.py --rows 100000 --output data/large_orders.csv
```

The dashboard uses Pandas in memory; a larger CSV alone does not make it distributed big-data processing. Uploads are limited to 100 MB by the supplied Streamlit configuration; feasible size depends on available RAM. Do not claim billion-row scalability from this prototype.

## Optional Spark extension

The standalone script writes monthly/category aggregates without collecting full raw data to Pandas. It is an independent demonstration and its output is not accepted by the order-line dashboard schema. Use a compatible Java installation (Java 17 is a practical choice) and consult the official Spark installation page for the selected release.

```powershell
python -m pip install "pyspark>=4,<5"
spark-submit --master "local[*]" spark_aggregate.py data/large_orders.csv spark-output
```

Use a new output directory for each run. Local mode demonstrates the Spark API on one machine; an actual cluster deployment is separate work. The Spark script validates its required aggregation fields but is not a replacement for the dashboard's complete order-line validator. Spark execution is optional and is not part of the core dashboard test suite.

## Verification

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

Tests cover revenue/AOV with repeated order IDs, cleaning invalid rows and exact duplicates, missing discounts/coordinates, all chart types, and Streamlit filter/empty-selection interactions. Optional Spark needs its own Java/Spark environment.

## Official references

- [Streamlit Plotly integration](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)
- [Plotly tile scatter maps](https://plotly.com/python/tile-scatter-maps/)
- [PySpark installation](https://spark.apache.org/docs/latest/api/python/getting_started/install.html)
