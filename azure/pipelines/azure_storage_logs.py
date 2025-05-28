import dlt

import sys

from pyspark.dbutils import DBUtils
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
sys.path.append(spark.conf.get("bundle.sourcePath"))

from pipelines.utils import (
    parse_storage_path,
    parse_eventhub_logs,
    hms_table_schema,
    eventhub_logs_schema,
    azure_apps,
    azure_apps_schema,
)

dbutils = DBUtils(spark)

secret_scope = spark.conf.get("secret-scope")
eh_name = spark.conf.get("eh-name")
eh_namespace = spark.conf.get("eh-namespace")
client_id = spark.conf.get("client-id")
client_secret = dbutils.secrets.get(secret_scope, spark.conf.get("client-secret"))
tenant_id = spark.conf.get("tenant-id")
get_azure_apps = spark.conf.get("get-azure-apps")

if get_azure_apps:
    get_azure_apps = bool(get_azure_apps)

sasl_config = f'kafkashaded.org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required clientId="{client_id}" clientSecret="{client_secret}" scope="https://{eh_namespace}/.default" ssl.protocol="SSL";'

kafka_options = {
    "kafka.bootstrap.servers": f"{eh_namespace}:9093",
    "kafka.sasl.jaas.config": sasl_config,
    "kafka.sasl.oauthbearer.token.endpoint.url": f"https://login.microsoft.com/{tenant_id}/oauth2/v2.0/token",
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.mechanism": "OAUTHBEARER",
    "kafka.sasl.login.callback.handler.class": "kafkashaded.org.apache.kafka.common.security.oauthbearer.secured.OAuthBearerLoginCallbackHandler",
    "subscribe": eh_name,
    "startingOffsets": "earliest",
    "failOnDataLoss": False,
}


# crawl all the tables in hive_metastore
@dlt.table(name="hms_details")
def gather_hms_details() -> DataFrame:
    hms_catalog = "hive_metastore"
    table_details: list[dict[str, str | None]] = []
    filter_statement = (
        (F.col("col_name") == "Catalog")
        | (F.col("col_name") == "Database")
        | (F.col("col_name") == "Table")
        | (F.col("col_name") == "Type")
        | (F.col("col_name") == "Provider")
        | (F.col("col_name") == "Location")
    )

    dbs = spark.sql(f"SHOW SCHEMAS IN {hms_catalog}")

    for db in dbs.collect():
        tables = spark.sql(f"SHOW TABLES IN {hms_catalog}.{db.databaseName}")
        for table in tables.collect():
            if table.isTemporary:
                continue

            namespace = f"{hms_catalog}.{table.database}.{table.tableName}"
            try:
                tbl_metadata = spark.sql(f"DESCRIBE EXTENDED {namespace}").filter(
                    filter_statement
                )
                tbl_metadata = (
                    tbl_metadata.groupBy()
                    .pivot("col_name")
                    .agg({"data_type": "first"})
                    .first()
                )

                table_details.append(
                    {
                        "catalog": tbl_metadata.Catalog,
                        "database": tbl_metadata.Database,
                        "name": tbl_metadata.Table,
                        "table_format": tbl_metadata.Provider,
                        "table_type": tbl_metadata.Type,
                        "location_uri": tbl_metadata.Location,
                        "status": None,
                    }
                )

            except Exception as exc:
                print(f"fail {namespace}")
                table_details.append(
                    {
                        "catalog": hms_catalog,
                        "database": table.database,
                        "name": table.tableName,
                        "table_format": None,
                        "table_type": None,
                        "location_uri": None,
                        "status": str(exc),
                    }
                )

    return spark.createDataFrame(data=table_details, schema=hms_table_schema)


@dlt.table
def azure_storage_logs_raw() -> DataFrame:
    df = spark.readStream.format("kafka").options(**kafka_options).load()
    df = parse_eventhub_logs(df=df, schema=eventhub_logs_schema)
    return df


@dlt.table(name="all_table_details")
def information_details():
    df_info = spark.read.table("system.information_schema.tables").select(
        F.col("table_catalog"),
        F.col("table_schema"),
        F.col("table_name"),
        F.col("table_type"),
        F.col("data_source_format"),
        F.col("storage_path"),
        F.lit(None).alias("status"),
    )

    df_hms = spark.read.table("hms_details").select(
        F.col("catalog").alias("table_catalog"),
        F.col("database").alias("table_schema"),
        F.col("name").alias("table_name"),
        F.col("table_type"),
        F.upper(F.col("table_format")).alias("data_source_format"),
        F.col("location_uri").alias("storage_path"),
        F.col("status"),
    )

    df_table_details = df_info.unionByName(df_hms, allowMissingColumns=True)

    df = df_table_details.select(
        F.col("table_catalog"),
        F.col("table_schema"),
        F.col("table_name"),
        F.concat_ws(
            ".", F.col("table_catalog"), F.col("table_schema"), F.col("table_name")
        ).alias("full_namespace"),
        F.col("storage_path"),
        F.coalesce(parse_storage_path(F.col("storage_path")), F.lit(None)).alias(
            "parsed_path"
        ),
        F.col("table_type"),
        F.col("data_source_format"),
        F.col("status"),
    )

    df = df.where(
        (~F.col("table_catalog").isin("system", "__databricks_internal"))
        & (~F.col("table_name").like("__materialization%"))
        & (
            (F.col("table_type").isin("MANAGED", "EXTERNAL"))
            | (F.col("table_type").isNull())
        )
        & (
            (~F.col("data_source_format").isin("DELTASHARING"))
            | (F.col("data_source_format").isNull())
        )
    )

    return df


@dlt.table
def azure_application_details():
    try:
        df_creds = spark.read.table("system.information_schema.storage_credentials")

        app_names: list[str] = (
            df_creds.select(
                F.collect_set(
                    F.regexp_extract("credential", "accessConnectors/(.*?),mi_id", 1)
                ).alias("access_connector_name")
            )
            .first()
            .access_connector_name
        )

        if app_names:
            return azure_apps(
                spark=spark,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                app_names=app_names,
                schema=azure_apps_schema,
            )
        return spark.createDataFrame([], azure_apps_schema)
    except Exception:
        return spark.createDataFrame([], azure_apps_schema)


@dlt.table
def azure_storage_logs():
    df_slog = spark.read.table("azure_storage_logs_raw").alias("slog")
    df_info = spark.read.table("all_table_details").alias("info")

    df_join = df_slog.join(
        df_info,
        on=F.expr(
            "slog.properties.objectKey LIKE CONCAT('%', info.parsed_path, '%') AND info.parsed_path != ''"
        ),
        how="left",
    )

    # Select and transform the required columns
    df_result = df_join.select(
        F.to_timestamp(F.col("slog.time")).alias("storage_time"),
        F.split(F.col("slog.resourceId"), "/")[2].alias("subscription_id"),
        F.split(F.col("slog.resourceId"), "/")[4].alias("resource_group"),
        F.split(F.col("slog.resourceId"), "/")[8].alias("storage_account"),
        F.coalesce(F.col("info.table_catalog"), F.lit("foreign")).alias(
            "table_catalog"
        ),
        F.coalesce(F.col("info.table_schema"), F.lit("foreign")).alias("table_schema"),
        F.coalesce(F.col("info.table_name"), F.lit("foreign")).alias("table_name"),
        F.coalesce(F.col("info.full_namespace"), F.lit("foreign")).alias(
            "full_namespace"
        ),
        F.coalesce(
            F.col("info.storage_path"),
            F.concat(
                F.lit("abfss://"),
                F.regexp_extract(
                    F.regexp_extract(
                        F.col("slog.properties.objectKey"), "(.*)(/_delta_log)", 1
                    ),
                    "^/[^/]+/([^/]+)",
                    1,
                ),
                F.lit("@"),
                F.regexp_extract(
                    F.regexp_extract(
                        F.col("slog.properties.objectKey"), "(.*)(/_delta_log)", 1
                    ),
                    "^/([^/]+)",
                    1,
                ),
                F.lit(".dfs.core.windows.net/"),
                F.regexp_extract(
                    F.regexp_extract(
                        F.col("slog.properties.objectKey"), "(.*)(/_delta_log)", 1
                    ),
                    "^/[^/]+/[^/]+/(.*)",
                    1,
                ),
            ),
        ).alias("storage_path"),
        F.coalesce(F.col("info.table_type"), F.lit("EXTERNAL")).alias("table_type"),
        F.coalesce(F.col("info.data_source_format"), F.lit("DELTA")).alias(
            "data_source_format"
        ),
        F.col("slog.category"),
        F.col("slog.operationName"),
        F.col("slog.statusText"),
        F.col("slog.durationMs"),
        F.col("slog.callerIpAddress"),
        F.col("slog.identity.type").alias("authType"),
        F.col("slog.identity.requester.objectId").alias("authObjectId"),
        F.col("slog.properties.userAgentHeader").alias("userAgentHeader"),
        F.col("slog.properties.clientRequestId").alias("clientRequestId"),
        F.col("slog.properties.objectKey").alias("objectKey"),
    )

    df_result = df_result.where(
        (F.col("slog.category").isin("StorageWrite", "StorageDelete", "StorageRead"))
        & (F.col("slog.properties.objectKey").like("%_delta_log%"))
        & (~F.col("slog.properties.objectKey").like("%unity%"))
        & (F.col("slog.statusText") == "Success")
    )

    return df_result
