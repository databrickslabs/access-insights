import requests

from delta import DeltaTable

from pyspark.sql.types import StructType
from pyspark.sql import DataFrame, Column, SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    explode,
    concat_ws,
    regexp_extract,
    struct,
)


def parse_eventhub_logs(df: DataFrame, schema: StructType) -> DataFrame:
    """Extract details from a JSON field in the eventhub logs"""

    parsed_df = df.select(
        from_json(col("value").cast("string"), schema=schema).alias("data")
    ).select("data.records")

    # Explode the records array to get individual records
    exploded_df = parsed_df.select(explode(col("records")).alias("record")).select(
        "record.*"
    )

    return exploded_df


def parse_storage_path(col: Column) -> Column:
    """Parse out the storage path from the storage column"""

    parsed_path = concat_ws(
        "/",
        regexp_extract(col, "abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?", 2),
        regexp_extract(col, "abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?", 1),
        regexp_extract(col, "abfss?://([^/]+)@([^.]+)(\.[^/]+)(?:/(.+))?", 4),
    )
    return parsed_path


def azure_apps(
    spark: SparkSession,
    tenant_id: str,
    client_id: str,
    client_secret: str,
    app_names: str | list[str],
    schema: StructType | str,
) -> DataFrame:
    """
    List Azure enterprise applications and returns a PySpark DataFrame.

    Args:
        spark: SparkSession instance
        tenant_id: Azure tenant ID
        client_id: Azure client ID
        client_secret: Azure client secret
        app_names: Single or List of display names
        schema: PySpark StructType schema for the DataFrame

    Returns:
        PySpark DataFrame containing enterprise applications data
    Raises:
        HTTPException: when failed to authenticate or read from MS graph
    """

    if isinstance(app_names, str):
        app_names = list(app_names)

    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    auth_response = requests.post(auth_url, data=auth_data)

    auth_response.raise_for_status()

    access_token = auth_response.json().get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "ConsistencyLevel": "eventual",
    }

    apps_data = []

    for app in app_names:
        url = f'https://graph.microsoft.com/v1.0/servicePrincipals?$search="displayName:{app}"'
        response = requests.get(url, headers=headers)

        response.raise_for_status()

        for value in response.json().get("value", []):
            app_details = {
                "id": value.get("id"),
                "app_id": value.get("appId"),
                "account_enabled": value.get("accountEnabled"),
                "display_name": value.get("displayName"),
                "service_principal_names": value.get("servicePrincipalNames"),
                "service_principal_type": value.get("servicePrincipalType"),
                "created_datetime": value.get("createdDateTime"),
                "deleted_datetime": value.get("deletedDateTime"),
            }
            apps_data.append(app_details)

    return spark.createDataFrame(apps_data, schema=schema)


def collect_table_details(
    spark: SparkSession, df: DataFrame, schema: StructType | str
) -> DataFrame:
    """Collect all table details"""

    tables = df.collect()

    table_details = []
    for table in tables:
        table_vals = table.asDict()
        table_vals["table_details"] = None
        namespace = (
            f"`{table.table_catalog}`.`{table.table_schema}`.`{table.table_name}`"
        )

        if table.data_source_format == "DELTA" and table.table_type == "EXTERNAL":
            try:
                print(namespace)
                df = (
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
                        ).alias("details")
                    )
                )

                table_vals["table_details"] = df.first().details.asDict()

            except Exception as exc:
                table_vals["status"] = "\n".join(
                    filter(None, [table_vals.get("status"), str(exc)])
                )

        table_details.append(table_vals)

    return spark.createDataFrame(table_details, schema=schema)
