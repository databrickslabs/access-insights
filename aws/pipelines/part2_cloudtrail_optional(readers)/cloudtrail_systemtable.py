import dlt
from pyspark.sql.functions import col, regexp_extract, concat, lit, md5, substring, when, from_json, get_json_object, explode, regexp_replace,to_json, lower, sum as spark_sum
from pyspark.sql.types import StructType, StructField, StringType
# Increase the number of shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "200")
# Define the regex pattern to extract the bucket name
pattern = "^s3://([^/]+)/"

# Define the schema for the credentials field
credentials_schema = StructType([
    StructField("accessKeyId", StringType(), True)
])

@dlt.view
def information_schema():
    return (spark.read.table("system.information_schema.tables")
            .filter((col("table_catalog") != "system") & col("storage_path").isNotNull())
            .select(
                col("table_catalog"),
                col("table_schema"),
                col("table_name"),
                col("table_type"),
                col("table_owner"),
                col("last_altered_by"),
                col("data_source_format"),
                col("storage_sub_directory"),
                col("storage_path"),
                concat(col("table_catalog"), lit("."), col("table_schema"), lit("."), col("table_name")).alias("full_table_name"),
                regexp_extract(col("storage_path"), pattern, 1).alias("bucket")
            ))


@dlt.view
def cloudtrail_logs_with_storagepath():
    json_data = (
        dlt.read("access_insights.default.cloudtrail_logs")
        .select(
            "*",
            get_json_object(to_json(col("requestParameters")), "$.policy").alias("policy_json")
        )
    )

    flattened_data = (
        json_data
        .select(
            "*",
            get_json_object(col("policy_json"), "$.Version").alias("Version"),
            explode(
                from_json(
                    get_json_object(col("policy_json"), "$.Statement"),
                    "array<struct<Effect:string,Action:array<string>,Resource:array<string>,Condition:map<string,map<string,array<string>>>>>"
                )
            ).alias("Statement")
    )
    )

    exploded_data = (
        flattened_data
        .select(
            "*",
            col("Statement.Effect").alias("OriginalEffect"),
            col("Statement.Action").alias("OriginalAction"),
            col("Statement.Resource").alias("OriginalResource"),
            col("Statement.Effect"),
            col("Statement.Condition"),
            explode(col("Statement.Action")).alias("Action2"),
            explode(col("Statement.Resource")).alias("Resource2_renamed")
        )
    )

    return exploded_data.select(
        "*",
        regexp_replace(col("Resource2_renamed"), "arn:aws:s3:::", "s3://").alias("storage_path")
    )

@dlt.table
def all_tables_joined_with_cloud_trail_grouped():
    read_actions = ['s3:AssumeRole', 's3:GetObject', 's3:ListObjects']
    write_actions = ['s3:PutObject', 's3:DeleteObject']

    # Read source datasets
    df_tables = dlt.read("all_table_details").alias("a")
    df_cloudtrail = dlt.read("cloudtrail_logs_with_storagepath").alias("b")

    # Perform LEFT JOIN
    joined_df = df_tables.join(
        df_cloudtrail,
        col("a.storage_path") == col("b.storage_path"),
        how="left"
    )

    # Determine if the access is internal or external based on userAgent
    enriched_df = joined_df.withColumn(
        "access_type",
        when(lower(col("b.userAgent")).contains("databricks"), "internal").otherwise("external")
    ).withColumn(
        "is_read",
        when(col("b.Action2").isin(read_actions), 1).otherwise(0)
    ).withColumn(
        "is_write",
        when(col("b.Action2").isin(write_actions), 1).otherwise(0)
    ).withColumn(
        "internal_read",
        when((lower(col("b.userAgent")).contains("databricks")) & col("b.Action2").isin(read_actions), 1).otherwise(0)
    ).withColumn(
        "internal_write",
        when((lower(col("b.userAgent")).contains("databricks")) & col("b.Action2").isin(write_actions), 1).otherwise(0)
    ).withColumn(
        "external_read",
        when((~lower(col("b.userAgent")).contains("databricks")) & col("b.Action2").isin(read_actions), 1).otherwise(0)
    ).withColumn(
        "external_write",
        when((~lower(col("b.userAgent")).contains("databricks")) & col("b.Action2").isin(write_actions), 1).otherwise(0)
    )

    # Group by table metadata (not access_type)
    grouped_df = enriched_df.groupBy(
        "a.table_catalog",
        "a.table_schema",
        "a.table_name",
        "a.full_namespace",
        "a.table_type",
        "a.data_source_format"
    ).agg(
        spark_sum("internal_read").alias("internal_reads"),
        spark_sum("internal_write").alias("internal_writes"),
        spark_sum("external_read").alias("external_reads"),
        spark_sum("external_write").alias("external_writes")
    )

    return grouped_df



