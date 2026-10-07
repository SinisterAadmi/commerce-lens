# E-Commerce Big Data Visualization Dashboard

**Project title:** CommerceLens  
**Assigned topic:** Data Visualization: Types, Applications  
**Student / roll number / institution:** [Fill in]  
**Tools:** Python, Pandas, Plotly, Streamlit; optional PySpark extension

## Abstract

CommerceLens transforms order-line data into an interactive analytics dashboard. It validates CSV inputs, derives net revenue, aggregates business measures, and presents eight complementary visualization types. Linked filters enable exploration by date, category, state, and payment method. Findings are computed from the current selection rather than hard-coded. The supplied dataset is explicitly synthetic and reproducible. A separate Spark script illustrates a path toward distributed aggregation without overstating the scale of the Pandas prototype.

## Problem and objectives

A list of transaction records makes it difficult to detect revenue trends, compare products, understand payment behavior, or identify unprofitable orders. The project addresses these questions through visual encoding and descriptive analysis.

Objectives are to clean heterogeneous CSV inputs; calculate consistent revenue, profit, order count, AOV and margin; demonstrate eight chart types; explain why each suits the data; connect filtering to all outputs; and document the limits of descriptive findings and in-memory processing.

## Architecture

```text
CSV / reproducible sample
          ↓
Schema validation and row cleaning
          ↓
Pandas: derived measures and filters
          ↓
Aggregations + descriptive findings
          ↓
Plotly visualizations → Streamlit dashboard → CSV / text export

Optional extension:
Large CSV → PySpark transformations → monthly/category CSV aggregates
```

The optional Spark output is a separate aggregate dataset. A future production dashboard would read bounded aggregate tables from storage rather than loading all raw transactions in memory.

## Dataset and preprocessing

The demo contains 12,000 rows from January 2024 to December 2025, generated with NumPy seed 42. Fields include Order ID, Date, Customer, Product, Category, Subcategory, Price, Quantity, Discount, City, State, Payment Method, Rating, Profit, Latitude and Longitude. The generator includes ten Indian cities and five product categories. It weights October and November dates more heavily to support a seasonality demonstration. These are synthetic design decisions, not observed facts about the economy.

Column whitespace is removed; missing required columns reject the upload. Exact duplicate rows are removed. Required blank fields, invalid dates, non-finite numeric values, negative prices, fractional/non-positive quantities and discount fractions outside 0–1 reject rows. Repeated order IDs are retained as lines. Missing discount columns imply zero discount; the scatter analysis is disabled when discounts were not supplied. Optional ratings and geographic coordinates are validated separately. The dashboard exposes the row-count audit.

## Business measures

| Measure | Definition | Interpretation |
|---|---|---|
| Net revenue | Sum of Price × Quantity × (1 − Discount) | Post-discount sales before taxes/shipping/refunds |
| Profit | Sum of supplied line Profit | Depends on the upstream profit definition |
| Orders | Distinct selected Order IDs | Avoids counting multi-line orders repeatedly |
| Average order value | Net revenue / distinct orders | Value of selected order portions |
| Profit margin | Profit / net revenue | Shown as zero when revenue is zero to avoid division errors |

## Visualization choices

| Type | Application | Why selected | Interpretation limit |
|---|---|---|---|
| Line | Revenue over day/week/month | Connects ordered time observations | Partial periods and missing coverage affect trends |
| Bar | Category or product revenue | Common baseline supports magnitude comparisons | Top 15 only; revenue does not equal profit |
| Pie / donut | Payment method share | Part-to-whole composition with few categories | Orders with split payment methods can overlap |
| Bubble map | City orders and revenue | Spatial position reveals concentration | Coordinates needed; tile map needs internet |
| Scatter | Discount versus line profit | Shows association, outliers and heterogeneous groups | Sampled for rendering; confounding prevents causal claims |
| Heatmap | Month × weekday revenue | Color supports two-dimensional pattern scanning | Totals reflect how many weekdays occur in each month |
| Histogram | Order value distribution | Reveals skew and spread using numeric bins | Bin width changes apparent shape |
| Treemap | Category → subcategory revenue | Nested area represents hierarchy and share | Fine differences are harder to compare than bars |

## Analysis and findings

Findings are generated after filtering: leading revenue category and its share, city with most distinct orders, highest-revenue month, share of loss-making lines, margin, and discount/profit Pearson correlation when both variables vary. The findings are descriptive. A negative correlation does not prove discounts caused losses because product cost, quantity and category mix may differ. A high October/November total in the demo follows the generation model and cannot substantiate real festival behavior.

For the final submission, paste exported findings from the selection you demonstrate and label them as synthetic-sample results. If you replace the sample with real data, record its source, collection period, units, permissions and missing-data limitations.

## Interaction and demonstration

All metrics, charts and findings respond to the sidebar date/category/state/payment filters. Time granularity, category/product comparison, and histogram bin count provide additional controls. Hover, legend toggles, zoom and PNG export are available through Plotly. Filtered CSV and text findings are downloadable. Empty filters produce an explicit no-results message rather than broken charts.

## Big-data scope

Pandas is an in-memory engine and the bundled sample is small. The prototype demonstrates analytics and visual communication; it should not be presented as proof of distributed scale. The PySpark extension uses Spark transformations and grouped aggregation. To establish an actual BDA evaluation, run it on a suitably large dataset, report input bytes/rows, machine or cluster resources, runtime, partitions and peak memory, then compare consistent outputs. This report does not invent performance results.

## Limitations and future work

The data is synthetic; local city coordinates are a limited lookup; map tiles need internet; currency is assumed INR; refunds and taxes are outside the revenue model. Filtered AOV can reflect partial orders. Exact-duplicate removal can remove legitimate identical lines unless a unique line ID distinguishes them. Scatter uses at most 5,000 points, while calculations use every filtered row. Privacy controls, authentication and cloud deployment are future work. Possible extensions include Spark-backed aggregate storage, daily-normalized seasonality analysis, cohort retention and source-specific schemas.

## Conclusion

The dashboard demonstrates how chart selection follows data structure and analytical purpose. It combines transaction validation, consistent business measures, interactive exploration and qualified findings in a working application.

## Suggested presentation sequence

1. Problem and analytical questions.
2. Dataset fields, synthetic provenance and cleaning.
3. Architecture and measure definitions.
4. Revenue charts: line, bar and heatmap.
5. Customer/pricing charts: donut, histogram and scatter.
6. Geography and hierarchy: map and treemap.
7. Live filter demonstration and exported findings.
8. Scope, limitations and Spark extension.

## Viva preparation

- **Why use a bar instead of a pie for category revenue?** Bars support more precise comparisons through a shared baseline.
- **Why is the histogram not a bar chart of products?** Its bins partition a numeric variable; product categories are discrete labels.
- **Does correlation prove that discounts reduce profit?** No. Product mix and order size can confound the relationship.
- **What makes this a big-data system?** The core application is a Pandas prototype; the Spark extension demonstrates distributed APIs. Actual cluster-scale results require measured execution.
- **Why count distinct orders?** One order can contain multiple lines.
- **How do you prevent misleading insights?** Explicit provenance, filter-aware calculations, formula definitions, audit counts and interpretation caveats.

## References

[Streamlit chart integration](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [Plotly map documentation](https://plotly.com/python/tile-scatter-maps/), [Spark installation](https://spark.apache.org/docs/latest/api/python/getting_started/install.html).
