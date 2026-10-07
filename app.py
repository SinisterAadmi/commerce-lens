from pathlib import Path
from io import BytesIO
import hashlib
import pandas as pd
import streamlit as st
from analytics import clean_data, metrics, insights, REQUIRED
from charts import build_charts
from generate_data import generate

st.set_page_config(page_title="CommerceLens · E-commerce Analytics", page_icon="📊", layout="wide")
st.markdown("""<style>
.block-container {padding-top:3.5rem; max-width:1500px;}
h1 {letter-spacing:-1.5px;} h3 {font-size:1.15rem!important;}
[data-testid="stMetric"] {background:white;border:1px solid #E1E8F0;padding:18px;border-radius:12px;}
[data-testid="stMetricLabel"] {color:#61748A;}
[data-testid="stMetricValue"] {font-size:1.8rem;}
[data-testid="stSidebar"] {border-right:1px solid #E1E8F0;}
</style>""", unsafe_allow_html=True)

@st.cache_data
def load_sample():
    path = Path(__file__).parent / "data" / "sample_orders.csv"
    return pd.read_csv(path) if path.exists() else generate()

@st.cache_data
def parse_upload(payload):
    return pd.read_csv(BytesIO(payload))

with st.sidebar:
    st.title("◈ CommerceLens")
    st.caption("E-COMMERCE INTELLIGENCE")
    st.divider()
    source = st.radio("Data source", ["Synthetic demo", "Upload CSV"])
    upload = st.file_uploader("Orders CSV", type="csv") if source == "Upload CSV" else None
    st.caption("Currency: INR · one row per order line")

if source == "Upload CSV":
    st.subheader("Upload your e-commerce data")
    st.write("Choose a CSV in the sidebar. Use the exact column names below; each row should represent one order line.")
    with st.expander("CSV schema and field formats", expanded=upload is None):
        required, optional = st.columns(2)
        with required:
            st.markdown("**Required columns**")
            st.code("\n".join(REQUIRED), language=None)
        with optional:
            st.markdown("**Optional columns**")
            st.code("Discount\nSubcategory\nRating\nLatitude\nLongitude", language=None)
        st.markdown("""**Field formats**

- **Date:** use `YYYY-MM-DD`, for example `2025-01-10`.
- **Price:** nonnegative unit price in INR, before discount (for example `1500`).
- **Quantity:** positive whole number (for example `2`).
- **Profit:** numeric profit for the order line; negative values represent losses.
- **Discount:** fraction from `0` to `1`; `0.20` means 20%. If omitted, zero discount is assumed.
- **Rating:** optional numeric value from `1` to `5`.
- **Latitude / Longitude:** numeric coordinates, from −90 to 90 / −180 to 180. Supply them for cities outside the demo lookup to include those cities on the map.
- **Other fields:** nonempty text. Repeated Order IDs are allowed for separate lines of the same order. Subcategory defaults to Product when omitted.
""")
        st.download_button("Download example CSV", load_sample().head(3).to_csv(index=False).encode("utf-8"), "example_orders.csv", "text/csv", key="schema_example")
    if upload is None:
        st.info("Upload a CSV using the sidebar to begin.")
        st.stop()

try:
    raw = load_sample() if source == "Synthetic demo" else parse_upload(upload.getvalue())
    data, quality = clean_data(raw)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError, pd.errors.EmptyDataError) as exc:
    st.error(f"Unable to load this dataset: {exc}")
    st.caption("Required columns: " + ", ".join(REQUIRED))
    st.stop()

with st.sidebar:
    st.subheader("Explore your data")
    # A source-specific prefix prevents stale selections after swapping datasets.
    prefix = hashlib.sha256(upload.getvalue()).hexdigest()[:16] if upload else "demo"
    dates = st.date_input("Date range", value=(data.Date.min().date(),data.Date.max().date()), min_value=data.Date.min().date(),max_value=data.Date.max().date(),key=prefix+"dates")
    categories = st.multiselect("Categories", sorted(data.Category.unique()), default=sorted(data.Category.unique()),key=prefix+"cats")
    states = st.multiselect("States", sorted(data.State.unique()), default=sorted(data.State.unique()),key=prefix+"states")
    methods = st.multiselect("Payment methods",sorted(data["Payment Method"].unique()), default=sorted(data["Payment Method"].unique()),key=prefix+"payments")
    st.caption("All charts and findings respond to these filters. Clear a selection to show no matching rows.")

st.caption("COMMERCE / ANALYTICS WORKSPACE")
st.title("Every order tells a story.")
st.write("Explore revenue, customer behavior, and the drivers of profitability.")
if source == "Synthetic demo":
    st.info("Demo workspace · 12,000 synthetic order lines, 2024–2025. Patterns are generated for teaching and are not evidence of real market behavior.")
if quality["Invalid rows removed"] or quality["Exact duplicates removed"]:
    st.warning(f"Cleaning removed {quality['Invalid rows removed']:,} invalid rows and {quality['Exact duplicates removed']:,} exact duplicates. Review Data & methodology for details.")
if len(dates) != 2:
    st.info("Select an end date to complete the date range.")
    st.stop()
filtered = data.loc[data.Date.between(pd.Timestamp(dates[0]),pd.Timestamp(dates[1])) & data.Category.isin(categories) & data.State.isin(states) & data["Payment Method"].isin(methods)]
if filtered.empty:
    st.warning("No orders match these filters. Expand the date range or select additional categories, states, or payment methods.")
    st.stop()
m = metrics(filtered)
def money(value):
    if abs(value) >= 10000000:
        return f"₹{value/10000000:.2f} Cr"
    if abs(value) >= 100000:
        return f"₹{value/100000:.2f} L"
    return f"₹{value:,.0f}"

st.caption(f"{dates[0]:%d %b %Y} — {dates[1]:%d %b %Y} · {len(filtered):,} order lines · {filtered.Customer.nunique():,} customers")
columns = st.columns(5)
for col,label,value,detail in zip(columns,["Net revenue","Profit","Distinct orders","Avg. order value","Profit margin"],[money(m['revenue']),money(m['profit']),f"{m['orders']:,}",money(m['aov']),f"{m['margin']:.1%}"],[f"₹{m['revenue']:,.2f} · Cr = crore, L = lakh",f"₹{m['profit']:,.2f} · Cr = crore, L = lakh","Distinct Order IDs in this selection",f"₹{m['aov']:,.2f}","Supplied profit divided by calculated net revenue"]):
    col.metric(label,value,help=detail)
overview, behavior, geography, methodology = st.tabs(["Revenue & performance", "Customer & pricing", "Geography & hierarchy", "Data & methodology"])

with overview:
    control1,control2 = st.columns(2)
    frequency = control1.segmented_control("Time granularity",["Day","Week","Month"],default="Month") or "Month"
    group = control2.segmented_control("Compare sales by",["Category","Product"],default="Category") or "Category"
with behavior:
    bins = st.slider("Histogram bins",10,80,30,5)
figures = build_charts(filtered,frequency,group,bins)

WHY = {
    "Revenue over time":"Line · Connects ordered time points to reveal trends. Weekly buckets end on Monday; empty buckets have zero sales.",
    "Sales by category":"Bar · A shared baseline makes category or product magnitudes easy to compare. Shows the top 15 by net revenue.",
    "Payment mix":"Donut / pie · Shows part-to-whole payment share. Distinct orders are counted within each method; split payments can count an order in multiple segments.",
    "Discount vs profit":"Scatter · Shows association, outliers, and tradeoffs between two numeric variables. At most 5,000 reproducibly sampled lines are plotted; findings use all filtered lines.",
    "Sales calendar":"Heatmap · Color exposes patterns across month and weekday. Values are totals, not averages, so calendar-day counts affect comparisons.",
    "Order value distribution":"Histogram · Groups numeric order totals into bins to expose spread and skew. Orders are summed across the selected lines.",
    "Orders across India":"Bubble map · Location reveals geographic concentration. Bubble size encodes distinct orders and color encodes revenue. Base-map tiles require internet.",
    "Category hierarchy":"Treemap · Nested rectangles show category and subcategory contribution; area encodes net revenue. Zero-revenue branches are omitted.",
}

def show_chart(name):
    with st.container(border=True):
        st.subheader(name if name != "Sales by category" else f"Sales by {group.lower()}")
        if name == "Discount vs profit" and not quality["Discount supplied"]:
            st.info("Discount was not supplied. Revenue assumes zero discount; upload Discount fractions to explore this relationship.")
        elif name in figures:
            st.plotly_chart(figures[name],width="stretch",key=name,config={"displaylogo":False})
        else:
            st.info("No usable coordinates for this selection." if name == "Orders across India" else "No positive revenue to display.")
        st.caption(WHY[name])

with overview:
    left,right = st.columns(2)
    with left: show_chart("Revenue over time")
    with right: show_chart("Sales by category")
    show_chart("Sales calendar")
    st.subheader("What the data says")
    for finding in insights(filtered,quality["Discount supplied"]):
        st.write("• " + finding)
    st.download_button("Download analytical findings", "\n".join(insights(filtered,quality["Discount supplied"])),"findings.txt","text/plain")
with behavior:
    left,right = st.columns(2)
    with left: show_chart("Payment mix")
    with right: show_chart("Order value distribution")
    show_chart("Discount vs profit")
with geography:
    left,right = st.columns(2)
    with left: show_chart("Orders across India")
    with right: show_chart("Category hierarchy")
    if quality["Rows without map coordinates"]:
        st.caption(f"{quality['Rows without map coordinates']:,} cleaned rows lack coordinates and are excluded from the map. Supply Latitude and Longitude for cities outside the demo lookup.")
with methodology:
    st.subheader("Data quality audit")
    st.dataframe(pd.DataFrame(quality.items(),columns=["Check","Result"]).astype(str),hide_index=True,width="stretch")
    st.markdown("""**Pipeline:** CSV → validation and cleaning → Pandas aggregation → Plotly → Streamlit.

**Revenue** = Price × Quantity × (1 − Discount). Price is the pre-discount unit price; Discount is a fraction from 0 to 1. Taxes, shipping revenue, and refunds are not modeled. Profit is supplied by the dataset and is not recalculated from revenue.

**Average order value** = selected net revenue ÷ distinct selected Order IDs. When only some lines of an order match the filters, this is the selected portion of that order's value. Repeated Order IDs are retained as order lines; exact duplicate rows are removed. City and payment subtotals can overlap for orders spanning multiple groups.

Rows with missing required fields, unparseable dates, non-finite required numbers, negative prices, non-positive or fractional quantities, or discounts outside 0–1 are removed. Dates are normalized to UTC calendar dates. Invalid optional ratings are treated as missing; unusable coordinates are excluded from the map.

**Scope:** This dashboard processes data in memory with Pandas. The included Spark script demonstrates a distributed aggregation extension; running the dashboard alone is not distributed big-data processing. Correlation and seasonal peaks are descriptive findings, not causal conclusions.
""")
    st.subheader("Filtered order lines")
    st.caption("Preview limited to 1,000 rows. The CSV export contains all matching rows.")
    st.dataframe(filtered.head(1000),hide_index=True,width="stretch")
    st.download_button("Export filtered CSV",filtered.to_csv(index=False).encode("utf-8"),"filtered_orders.csv","text/csv")
st.caption("CommerceLens · Data Visualization: Types, Applications · Python / Pandas / Plotly / Streamlit")
