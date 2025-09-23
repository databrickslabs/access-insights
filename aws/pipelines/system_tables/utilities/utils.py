import requests
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType
from delta import DeltaTable
from functools import reduce
from pyspark.sql.types import StructType
from pyspark.sql import DataFrame, Column, SparkSession
from pyspark.sql.functions import (
    col,
    lit,
    from_json,
    explode,
    concat_ws,
    regexp_extract,
    struct,
)
def collect_table_details(
    spark: SparkSession, df: DataFrame, schema: StructType | str
) -> DataFrame:
    """Collect all table details"""
    # Filter to external Delta tables only
    external_delta_df = df.filter(
        (col("data_source_format") == "DELTA") & (col("table_type") == "EXTERNAL")
    )
    delta_details_dfs = []
    delta_histories_dfs = []
    # Get a list of dicts for all external Delta table keys
    table_keys = external_delta_df.select(
        "table_catalog", "table_schema", "table_name"
    ).distinct().collect()
    for row in table_keys:
        namespace = f"`{row['table_catalog']}`.`{row['table_schema']}`.`{row['table_name']}`"
        try:
            # DESCRIBE DETAIL
            details_df = (
                DeltaTable.forName(spark, namespace)
                .detail()
                .select(
                    struct(
                        col("partitionColumns").alias("partition_cols"),
                        col("clusteringColumns").alias("clustering_cols"),
                        col("numFiles").alias("num_files"),
                        col("sizeInBytes").alias("size_in_bytes"),
                        col("properties").alias("properties"),
                        col("minReaderVersion").alias("min_reader_version"),
                        col("minWriterVersion").alias("min_writer_version"),
                        col("tableFeatures").alias("table_features"),
                        col("statistics").alias("statistics"),
                    ).alias("table_details")
                )
                .withColumn("table_catalog", lit(row["table_catalog"]))
                .withColumn("table_schema", lit(row["table_schema"]))
                .withColumn("table_name", lit(row["table_name"]))
            )
            delta_details_dfs.append(details_df)
            # HISTORY (top 5 rows, concat as string for preview)
            history_df = (
                DeltaTable.forName(spark, namespace)
                .history()
                .limit(5)
                .select(col("engineInfo").alias("engineInfo"))
                .withColumn("table_catalog", lit(row["table_catalog"]))
                .withColumn("table_schema", lit(row["table_schema"]))
                .withColumn("table_name", lit(row["table_name"]))
            )
            # Optionally, explode/consolidate engineInfo as array
            delta_histories_dfs.append(history_df)
        except Exception as exc:
            # Optionally, log exceptions or store a diagnostics DataFrame
            pass

    if delta_details_dfs:
        all_details_df = reduce(lambda a, b: a.unionByName(b), delta_details_dfs)
    else:
        # If no external delta tables, create empty DataFrame with expected schema
        all_details_df = spark.createDataFrame(
            [],
            StructType(
                [
                    StructField("table_details", StringType(), True),
                    StructField("table_catalog", StringType(), True),
                    StructField("table_schema", StringType(), True),
                    StructField("table_name", StringType(), True),
                ]
            ),
        )

    if delta_histories_dfs:
        all_history_df = reduce(lambda a, b: a.unionByName(b), delta_histories_dfs)
    else:
        # Same: construct empty DataFrame with expected schema
        all_history_df = spark.createDataFrame(
            [],
            StructType(
                [
                    StructField("engineInfo", StringType(), True),
                    StructField("table_catalog", StringType(), True),
                    StructField("table_schema", StringType(), True),
                    StructField("table_name", StringType(), True),
                ]
            ),
        )
    enriched_df = df.join(
        all_details_df, on=["table_catalog", "table_schema", "table_name"], how="left"
    )
    hist_grouped_df = all_history_df.groupBy(
        "table_catalog", "table_schema", "table_name"
    ).agg(F.collect_list("engineInfo").alias("history"))
    # Join history as 'history' column
    enriched_df = enriched_df.join(
        hist_grouped_df, on=["table_catalog", "table_schema", "table_name"], how="left"
    )

    # Example withColumn transformation: status field
    enriched_df = enriched_df.withColumn(
        "status",
        F.when(
            (col("table_details").isNull())
            & (col("data_source_format") == "DELTA")
            & (col("table_type") == "EXTERNAL"),
            F.lit("DeltaTable.details unavailable or error"),
        ),
    )
    return enriched_df.selectExpr("*")

    # Add NULL columns
    # null_columns = [
    #     "eventVersion",
    #     "userIdentity",
    #     "eventTime",
    #     "eventSource",
    #     "eventName",
    #     "awsRegion",
    #     "sourceIPAddress",
    #     "userAgent",
    #     "errorCode",
    #     "errorMessage",
    #     "requestParameters",
    #     "responseElements",
    #     "additionalEventData",
    #     "requestID",
    #     "eventID",
    #     "eventType",
    #     "recipientAccountId",
    #     "serviceEventDetails",
    #     "sharedEventID",
    #     "vpcEndpointId",
    # ]
    # for col_name in null_columns:
    #     enriched_df = enriched_df.withColumn(col_name, F.lit(None).cast(StringType()))