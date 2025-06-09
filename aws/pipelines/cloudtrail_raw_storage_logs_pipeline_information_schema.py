import dlt
from pyspark.sql.functions import col, regexp_extract, concat, lit, md5, substring, when, from_json, get_json_object, explode, regexp_replace,to_json, lower
from pyspark.sql.types import StructType, StructField, StringType

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
def audit_events():
    return (spark.read.table("system.access.audit")
            .filter((col("service_name") == "unityCatalog") & col("action_name").isin("generateTemporaryTableCredential", "getTable"))
            .select(
                col("request_params.table_full_name").alias("table_full_name"),
                col("request_params.credential_id").alias("credential_id"),
                col("request_params.operation").alias("operation"),
                col("request_params.table_id").alias("table_id"),
                col("request_params.table_url").alias("table_url"),
                col("request_params.aws_access_key_id").alias("aws_access_key_id"),
                col("event_time"),
                col("request_params.commandText").alias("commandText"),
                col("user_identity.email")
            ))

@dlt.table
def joined_audit_information():
    audit_df = dlt.read("audit_events")
    info_schema_df = dlt.read("information_schema")
    
    return audit_df.join(info_schema_df, audit_df["table_full_name"] == info_schema_df["full_table_name"], "inner")

@dlt.table
def cloudtrail_with_auditevents():
    cloudtrail_df = dlt.read_stream("cloudtrail_logs")
    
    joined_audit_df = dlt.read("joined_audit_information")
        
    # Parse the credentials field
    cloudtrail_df = cloudtrail_df.withColumn("parsed_credentials", from_json(col("responseElements.credentials"), credentials_schema))
    
    access_key_id_hash = when(
        col("eventName") == "AssumeRole",
        substring(md5(col("parsed_credentials.accessKeyId")), 0, 8)
    ).otherwise(
        substring(md5(col("userIdentity.accessKeyId")), 0, 8)
    ).alias("access_key_id_hash")
    
    return cloudtrail_df.withColumn("access_key_id_hash", access_key_id_hash).join(
        joined_audit_df,
        regexp_extract(col("aws_access_key_id"), 'REDACTED_ACCESS_KEY\\((.*)\\)', 1) == col("access_key_id_hash"),
        "left"
    )
@dlt.table
def cloudtrail_logs_with_path():
    json_data = (
        dlt.read("access_insights.default.cloudtrail_logs")
        .select(
            col("eventID"),
            col("eventName"),
            col("eventTime"),
            get_json_object(to_json(col("requestParameters")), "$.policy").alias("policy_json"),
            col("responseElements"),
            col("userAgent")
        )
    )

    flattened_data = (
        json_data
        .select(
            col("eventID"),
            col("userAgent"),
            col("eventName"),
            col("eventTime"),
            get_json_object(col("policy_json"), "$.Version").alias("Version"),
            explode(
                from_json(
                    get_json_object(col("policy_json"), "$.Statement"),
                    "array<struct<Effect:string,Action:array<string>,Resource:array<string>,Condition:map<string,map<string,array<string>>>>>"
                )
            ).alias("Statement"),
            col("responseElements")
        )
    )

    exploded_data = (
        flattened_data
        .select(
            col("eventID"),
            col("eventName"),
            col("eventTime"),
            col("Version"),
            col("userAgent"),
            col("Statement.Effect").alias("OriginalEffect"),
            col("Statement.Action").alias("OriginalAction"),
            col("Statement.Resource").alias("OriginalResource"),
            col("Statement.Effect"),
            col("Statement.Condition"),
            explode(col("Statement.Action")).alias("Action2"),
            explode(col("Statement.Resource")).alias("Resource2"),
            col("responseElements")
        )
    )

    return exploded_data.select(
        col("eventID"),
        col("eventName"),
        col("eventTime"),
        col("Version"),
        col("userAgent"),
        col("OriginalEffect"),
        col("OriginalAction"),
        col("OriginalResource"),
        col("Effect"),
        col("Action2"),
        col("responseElements"),
        regexp_replace(col("Resource2"), "arn:aws:s3:::", "s3://").alias("Resource2"),
        col("Condition")
    )