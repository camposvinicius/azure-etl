val StorageAccountName = "vinietlforsynapse"
val StorageAccountKey = "your-access-key-storage-account-gen2-synapse"

val dwDatabase = "sql_pool_dw_vini_etl"
val dwServer = "vinisynapseworkspace.sql.azuresynapse.net"
val dwUser = "vinietlazure"
val dwPass = "A1b2C3d4"
val dwJdbcPort =  "1433"
val dwJdbcExtraOptions = "encrypt=true;trustServerCertificate=true;hostNameInCertificate=*.database.windows.net;loginTimeout=30;"
val sqlDwUrl = s"jdbc:sqlserver://$dwServer:$dwJdbcPort;database=$dwDatabase;user=$dwUser;password=$dwPass;$dwJdbcExtraOptions"

val tempDir = s"wasbs://vinidatalakegen2@$StorageAccountName.blob.core.windows.net/data"
val tableName = "cryptotable"

sc.hadoopConfiguration.set(
  s"fs.azure.account.key.$StorageAccountName.blob.core.windows.net",
  s"$StorageAccountKey")

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

df.write
  .mode("append")
  .format("com.databricks.spark.sqldw")
  .option("url", sqlDwUrl)
  .option("forwardSparkAzureStorageCredentials", "true")
  .option("dbTable", tableName)
  .option("tempDir", tempDir)
  .save()