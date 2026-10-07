# Verification — 7 October 2026

Tested with Python 3.13 on Windows, Streamlit 1.65.0, Pandas 2.3.3, NumPy 2.5.3, Plotly 7.1.0. The complete installed package list is in `requirements-lock.txt`; `requirements.txt` supplies compatible version ranges for fresh environments.

**Result: 6 tests passed.**

- Eight chart outputs generated from valid synthetic data.
- Invalid dates, prices, discounts, quantities and exact duplicates handled correctly.
- Missing optional fields and unknown map coordinates handled.
- Revenue and AOV calculated correctly for a multi-line order.
- Missing required columns rejected with an actionable error.
- Streamlit started without app exceptions; weekly time grouping, product comparison, histogram bin changes, category filtering, empty selections and recovery all passed.

The dashboard was also started at `http://127.0.0.1:8501` and inspected in the browser. Layout inspection led to compact currency formatting on KPI cards. The synthetic CSV has 12,000 valid rows with no cleaning removals or missing map coordinates.

Streamlit's test runner and the preview required loopback socket access outside the execution sandbox. This was an environment restriction, not an app failure. Pandas/NumPy emits a upstream timedelta deprecation warning during weekly resampling; tests pass. Optional Spark execution was not verified because the core demonstration does not require a Java/Spark environment. Map tiles depend on external tile availability.
