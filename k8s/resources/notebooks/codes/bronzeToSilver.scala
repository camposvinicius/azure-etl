import org.apache.spark.sql.functions.count

val PATH_BRONZE = "wasb://bronze@vinietlazure.blob.core.windows.net/data/*.parquet"
val PATH_SILVER = "dbfs:/mnt/silver/processing/distinct"

val df = (
  spark.read.parquet(PATH_BRONZE)
  .distinct()
  .orderBy("symbol")
  )

df.cache()

display(df)

df.coalesce(1).write.mode("overwrite").format("parquet").save(PATH_SILVER)