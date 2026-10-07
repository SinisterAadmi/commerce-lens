"""Optional distributed monthly aggregation. Install pyspark separately."""
import argparse
from pyspark.sql import SparkSession, functions as F

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="CSV path or Spark-readable directory")
    parser.add_argument("output", help="New output directory (existing paths are not overwritten)")
    args = parser.parse_args()
    spark = SparkSession.builder.appName("CommerceLensMonthlyRevenue").getOrCreate()
    try:
        df = spark.read.option("header",True).csv(args.input)
        required = {"Order ID","Date","Category","Price","Quantity","Profit"}
        if not required.issubset(df.columns):
            raise ValueError(f"Missing columns: {sorted(required-set(df.columns))}")
        df = df.dropDuplicates().withColumn("Date",F.to_date("Date"))
        for column in ["Price","Quantity","Profit"]:
            df = df.withColumn(column,F.col(column).cast("double"))
        discount = F.col("Discount").cast("double") if "Discount" in df.columns else F.lit(0.0)
        df = df.withColumn("Discount",discount).dropna(subset=list(required | {"Discount"}))
        df = df.filter((F.col("Price")>=0) & (F.col("Quantity")>0) & (F.col("Quantity")==F.floor("Quantity")) & F.col("Discount").between(0,1))
        df = df.withColumn("Revenue",F.round(F.col("Price")*F.col("Quantity")*(1-F.col("Discount")),2))
        result = df.groupBy(F.date_format("Date","yyyy-MM").alias("Month"),"Category").agg(F.sum("Revenue").alias("Revenue"),F.sum("Profit").alias("Profit"),F.countDistinct("Order ID").alias("Orders"))
        result.write.mode("errorifexists").option("header",True).csv(args.output)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
