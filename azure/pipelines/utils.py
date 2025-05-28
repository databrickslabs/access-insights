import requests

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    MapType,
    ArrayType,
    BooleanType,
)
from pyspark.sql import DataFrame, Column, SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    explode,
    concat_ws,
    regexp_extract,
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


hms_table_schema = StructType(
    [
        StructField("catalog", StringType(), True),
        StructField("database", StringType(), True),
        StructField("name", StringType(), True),
        StructField("table_format", StringType(), True),
        StructField("table_type", StringType(), True),
        StructField("location_uri", StringType(), True),
        StructField("status", StringType(), True),
    ]
)

azure_apps_schema = StructType(
    [
        StructField("id", StringType(), True),
        StructField("app_id", StringType(), True),
        StructField("account_enabled", BooleanType(), True),
        StructField("display_name", StringType(), True),
        StructField("service_principal_names", ArrayType(StringType(), True), True),
        StructField("service_principal_type", StringType(), True),
        StructField("created_datetime", StringType(), True),
        StructField("deleted_datetime", StringType(), True),
    ]
)

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
