val cosmosEndpoint = "https://vinicosmosdbetlazure.documents.azure.com:443/"
val cosmosMasterKey = "yourcosmoskey"
val cosmosDatabaseName = "cosmosdbdatabase"
val cosmosContainerName = "cosmosdbcontainer"

val cfg = Map(
  "spark.cosmos.accountEndpoint" -> cosmosEndpoint,
  "spark.cosmos.accountKey" -> cosmosMasterKey,
  "spark.cosmos.database" -> cosmosDatabaseName,
  "spark.cosmos.container" -> cosmosContainerName,
  "spark.cosmos.read.inferSchema.enabled" -> "true"
)

spark.conf.set("spark.sql.catalog.cosmosCatalog", "com.azure.cosmos.spark.CosmosCatalog")
spark.conf.set(s"spark.sql.catalog.cosmosCatalog.spark.cosmos.accountEndpoint", cosmosEndpoint)
spark.conf.set(s"spark.sql.catalog.cosmosCatalog.spark.cosmos.accountKey", cosmosMasterKey)

import org.apache.spark.sql.types.StringType
import org.apache.spark.sql.functions.{col, monotonically_increasing_id}

val PATH_GOLD = "dbfs:/mnt/gold/consume"

val df = (
  spark.read.format("delta")
  .load(PATH_GOLD)
  .withColumn("id", monotonically_increasing_id())
  .withColumn("id", col("id").cast(StringType))
  .withColumn("min_value_by_crypto", col("min_value_by_crypto").cast(StringType))
  .withColumn("max_value_by_crypto", col("max_value_by_crypto").cast(StringType))
  .withColumn("difference_between_min_max", col("difference_between_min_max").cast(StringType))
  .withColumn("year", col("year").cast(StringType))
  .withColumn("month", col("month").cast(StringType))
  .withColumn("day", col("day").cast(StringType))
)

df.printSchema()

df.write.mode("append").format("cosmos.oltp").options(cfg).save()