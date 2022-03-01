import org.apache.spark.sql.functions.{
  min, max, expr, 
  year, month, dayofmonth, 
  current_date
}

val PATH_SILVER = "dbfs:/mnt/silver/processing/distinct"
val PATH_GOLD = "dbfs:/mnt/gold/consume"

val df = (
  spark.read.parquet(PATH_SILVER)
  .groupBy("symbol")
  .agg(
    min("price").alias("min_value_by_crypto"), max("price").alias("max_value_by_crypto")
  )
  .withColumn("difference_between_min_max", expr("max_value_by_crypto - min_value_by_crypto"))
  .withColumn("year", year(current_date()))
  .withColumn("month", month(current_date()))
  .withColumn("day", dayofmonth(current_date()))
  .orderBy("symbol")
  )

df.cache()

display(df)

df.coalesce(1).write.partitionBy("year", "month", "day").mode("overwrite").format("delta").save(PATH_GOLD)