import dlt
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    MapType,
    ArrayType,
)
from pyspark.sql import DataFrame, Column
from pyspark.sql.functions import (
    col,
    from_json,
    explode,
    concat_ws,
    regexp_extract,
    lit,
    to_timestamp,
    when,
    expr,
)


secret_scope = spark.conf.get("secret-scope")
eh_name = spark.conf.get("eh-name")
eh_namespace = dbutils.secrets.get(secret_scope, spark.conf.get("eh-namespace"))
client_id = dbutils.secrets.get(secret_scope, spark.conf.get("eh-slogs-client-id"))
client_secret = dbutils.secrets.get(
    secret_scope, spark.conf.get("eh-slogs-client-secret")
)
tenant_id = dbutils.secrets.get(secret_scope, spark.conf.get("eh-slogs-tenant-id"))

# Define the schema for Event Hub storage logs
eventhub_logs_schema = StructType(
    [
        StructField(
            "records",
            ArrayType(
                StructType(
                    [
                        StructField("time", StringType(), True),
                        StructField("resourceId", StringType(), True),
                        StructField("category", StringType(), True),
                        StructField("operationName", StringType(), True),
                        StructField("operationVersion", StringType(), True),
                        StructField("schemaVersion", StringType(), True),
                        StructField("statusCode", LongType(), True),
                        StructField("statusText", StringType(), True),
                        StructField("durationMs", LongType(), True),
                        StructField("callerIpAddress", StringType(), True),
                        StructField("correlationId", StringType(), True),
                        StructField(
                            "identity",
                            StructType(
                                [
                                    StructField("type", StringType(), True),
                                    StructField("tokenHash", StringType(), True),
                                    StructField(
                                        "authorization",
                                        ArrayType(
                                            StructType(
                                                [
                                                    StructField(
                                                        "action", StringType(), True
                                                    ),
                                                    StructField(
                                                        "roleAssignmentId",
                                                        StringType(),
                                                        True,
                                                    ),
                                                    StructField(
                                                        "roleDefinitionId",
                                                        StringType(),
                                                        True,
                                                    ),
                                                    StructField(
                                                        "principals",
                                                        ArrayType(
                                                            StructType(
                                                                [
                                                                    StructField(
                                                                        "id",
                                                                        StringType(),
                                                                        True,
                                                                    ),
                                                                    StructField(
                                                                        "type",
                                                                        StringType(),
                                                                        True,
                                                                    ),
                                                                ]
                                                            )
                                                        ),
                                                        True,
                                                    ),
                                                    StructField(
                                                        "denyAssignmentId",
                                                        StringType(),
                                                        True,
                                                    ),
                                                    StructField(
                                                        "type", StringType(), True
                                                    ),
                                                    StructField(
                                                        "result", StringType(), True
                                                    ),
                                                    StructField(
                                                        "reason", StringType(), True
                                                    ),
                                                ]
                                            )
                                        ),
                                        True,
                                    ),
                                    StructField(
                                        "requester",
                                        StructType(
                                            [
                                                StructField(
                                                    "objectId", StringType(), True
                                                ),
                                                StructField(
                                                    "tenantId", StringType(), True
                                                ),
                                            ]
                                        ),
                                        True,
                                    ),
                                ]
                            ),
                            True,
                        ),
                        StructField("location", StringType(), True),
                        StructField(
                            "properties", MapType(StringType(), StringType()), True
                        ),
                        StructField("uri", StringType(), True),
                        StructField("protocol", StringType(), True),
                        StructField("resourceType", StringType(), True),
                    ]
                )
            ),
            True,
        )
    ]
)


sasl_config = f'kafkashaded.org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required clientId="{client_id}" clientSecret="{client_secret}" scope="https://{eh_namespace}/.default" ssl.protocol="SSL";'

kafka_options = {
    # Port 9093 is the EventHubs Kafka port
    "kafka.bootstrap.servers": f"{eh_namespace}:9093",
    "kafka.sasl.jaas.config": sasl_config,
    "kafka.sasl.oauthbearer.token.endpoint.url": f"https://login.microsoft.com/{tenant_id}/oauth2/v2.0/token",
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.mechanism": "OAUTHBEARER",
    "kafka.sasl.login.callback.handler.class": "kafkashaded.org.apache.kafka.common.security.oauthbearer.secured.OAuthBearerLoginCallbackHandler",
    "subscribe": eh_name,
    "startingOffsets": "earliest",
}


def parse_eventhub_logs(df: DataFrame, schema: StructField) -> DataFrame:
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema=schema).alias("data")
    ).select("data.records")

    # Explode the records array to get individual records
    exploded_df = parsed_df.select(explode(col("records")).alias("record")).select(
        "record.*"
    )

    return exploded_df


def parse_storage_path(col: Column) -> Column:
    parsed_path = concat_ws(
        "/",
        regexp_extract(col, "abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?", 2),
        regexp_extract(col, "abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?", 1),
        regexp_extract(col, "abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?", 4),
    )
    return parsed_path


@dlt.table
def azure_storage_logs_raw():
    df = spark.readStream.format("kafka").options(**kafka_options).load()
    df = parse_eventhub_logs(df=df, schema=eventhub_logs_schema)
    return df


@dlt.view
def information_details():
    df_tables = spark.read.table("system.information_schema.tables").where(
        (col("table_catalog") != "system") & (col("storage_path").isNotNull())
    )

    df_tabes = df_tables.select(
        concat_ws(
            ".", col("table_catalog"), col("table_schema"), col("table_name")
        ).alias("table_name"),
        col("storage_path"),
        parse_storage_path(col("storage_path")).alias("parsed_path"),
        col("table_type"),
        col("table_owner").alias("created_by"),
        col("last_altered_by"),
        col("data_source_format"),
        col("storage_sub_directory"),
    )

    df_volumes = spark.read.table("system.information_schema.volumes").where(
        (col("volume_catalog") != "system") & (col("storage_location").isNotNull())
    )

    df_volumes = df_volumes.select(
        concat_ws(
            ".", col("volume_catalog"), col("volume_schema"), col("volume_name")
        ).alias("volume_name"),
        col("storage_location"),
        parse_storage_path(col("storage_location")).alias("parsed_path"),
        col("volume_type"),
        col("volume_owner").alias("created_by"),
        col("last_altered_by"),
        lit("unstructured").alias("data_source_format"),
        lit(None).alias("storage_sub_directory"),
    )

    df = df_tabes.unionByName(df_volumes, allowMissingColumns=True)
    return df


@dlt.table
def azure_storage_logs():
    df = dlt.read("azure_storage_logs_raw").alias("slog")
    df = df.join(
        dlt.read("information_details").alias("info"),
        on=expr("slog.properties.objectKey like concat('%', info.parsed_path, '%')"),
        how="left",
    )

    df = df.select(
        to_timestamp(col("slog.time")).alias("storage_time"),
        when(col("info.table_name").isNotNull(), lit(1))
        .otherwise(0)
        .alias("match_found"),
        col("slog.properties.clientRequestId").alias("storage_clientRequestId"),
        col("slog.properties.userAgentHeader").alias("storage_userAgentHeader"),
        col("slog.protocol").alias("storage_protocol"),
        col("slog.correlationId").alias("storage_correlationId"),
        col("slog.identity.type").alias("storage_authenticationType"),
        col("slog.identity.requester.tenantId").alias("storage_tenantId"),
        col("slog.identity.requester.objectId").alias("storage_principalId"),
        col("slog.operationName").alias("storage_operationName"),
        col("slog.statusText").alias("storage_statusText"),
        regexp_extract(col("slog.identity.authorization")[0].action, "[^/]+$", 0).alias(
            "storage_action"
        ),
        col("slog.category").alias("storage_category"),
        col("slog.callerIpAddress").alias("storage_callerIpAddress"),
        col("slog.properties.accountName").alias("storage_accountName"),
        col("slog.properties.objectKey").alias("storage_relativePath"),
        col("info.parsed_path").alias("info_parsedPath"),
        col("info.table_name").alias("info_tableName"),
        col("info.table_type").alias("info_tableType"),
    )
    return df
