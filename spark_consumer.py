# spark_consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, sum as _sum, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

spark = SparkSession.builder \
    .appName("SalesAggregator") \
    .getOrCreate()

kafka_bootstrap = "localhost:9092"
topic = "sales"
output_path = "aggregator_output"  # folder to write aggregated JSON

schema = StructType([
    StructField("order_id", StringType()),
    StructField("product_id", StringType()),
    StructField("category", StringType()),
    StructField("price", DoubleType()),
    StructField("quantity", IntegerType()),
    StructField("timestamp", StringType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap) \
    .option("subscribe", topic) \
    .option("startingOffsets", "latest") \
    .load()

# value is bytes - parse JSON
json_df = df.selectExpr("CAST(value AS STRING) as json_str")
parsed = json_df.select(from_json(col("json_str"), schema).alias("data"))
exploded = parsed.selectExpr(
    "data.order_id as order_id",
    "data.product_id as product_id",
    "data.category as category",
    "CAST(data.price AS DOUBLE) as price",
    "CAST(data.quantity AS INT) as quantity",
    "to_timestamp(data.timestamp) as event_time"
)

# Aggregate: total_sales and total_orders per category per 1-minute window
agg = exploded.groupBy(window(col("event_time"), "1 minute"), col("category")) \
    .agg(
        _sum(col("price") * col("quantity")).alias("total_sales"),
        _sum(col("quantity")).alias("total_units"),
        expr("count(distinct order_id) as orders")
    ) \
    .selectExpr("window.start as window_start", "window.end as window_end", "category", "total_sales", "total_units", "orders")

query = agg.writeStream \
    .outputMode("complete") \
    .format("json") \
    .option("path", output_path) \
    .option("checkpointLocation", output_path + "/_checkpoint") \
    .trigger(processingTime="30 seconds") \
    .start()

query.awaitTermination()
