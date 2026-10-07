import sys
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analytics import clean_data, metrics
from charts import build_charts
from generate_data import generate

class AnalyticsTests(unittest.TestCase):
    def test_order_lines_and_revenue(self):
        raw = generate(2)
        raw["Order ID"] = "ONE"
        raw["Price"] = [100,200]
        raw["Quantity"] = [2,1]
        raw["Discount"] = [.1,.25]
        df,_ = clean_data(raw)
        self.assertEqual(metrics(df)["orders"],1)
        self.assertEqual(metrics(df)["aov"],330)

    def test_invalid_and_duplicate_rows(self):
        raw = generate(5)
        raw["Quantity"] = raw["Quantity"].astype(float)
        raw.loc[0,"Price"] = -1
        raw.loc[1,"Date"] = "invalid"
        raw.loc[2,"Discount"] = 20
        raw.loc[3,"Quantity"] = 1.5
        raw = pd.concat([raw,raw.iloc[[4]]],ignore_index=True)
        df,report = clean_data(raw)
        self.assertEqual(len(df),1)
        self.assertEqual(report["Invalid rows removed"],4)
        self.assertEqual(report["Exact duplicates removed"],1)

    def test_optional_fields_and_unknown_city(self):
        raw = generate(2).drop(columns=["Discount","Latitude","Longitude","Subcategory","Rating"])
        raw["City"] = "Unknown city"
        df,report = clean_data(raw)
        self.assertFalse(report["Discount supplied"])
        self.assertEqual(report["Rows without map coordinates"],2)
        self.assertTrue((df.Discount==0).all())
        self.assertNotIn("Orders across India",build_charts(df))

    def test_schema_rejected(self):
        with self.assertRaisesRegex(ValueError,"Missing required"):
            clean_data(pd.DataFrame({"Date":["2025-01-01"]}))

    def test_chart_types(self):
        df,_ = clean_data(generate(200))
        figures = build_charts(df)
        self.assertEqual(len(figures),8)
        self.assertEqual({f.data[0].type for f in figures.values()}, {"scatter","bar","pie","scattermap","heatmap","histogram","treemap"})

class DashboardTests(unittest.TestCase):
    def test_app_and_filters(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT/"app.py"),default_timeout=60).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.get("plotly_chart")),8)
        self.assertEqual(app.metric[2].value,"12,000")
        app.segmented_control[0].set_value("Week").run()
        app.segmented_control[1].set_value("Product").run()
        app.slider[0].set_value(50).run()
        self.assertEqual(len(app.exception),0)
        app.multiselect[0].set_value(["Electronics"]).run()
        self.assertEqual(len(app.exception),0)
        self.assertLess(int(app.metric[2].value.replace(",","")),12000)
        app.multiselect[0].set_value([]).run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any("No orders match" in w.value for w in app.warning))
        app.multiselect[0].set_value(["Fashion"]).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.get("plotly_chart")),8)

if __name__ == "__main__":
    unittest.main()
