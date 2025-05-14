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
)


def parse_eventhub_logs(df: DataFrame, schema: StructType) -> DataFrame:
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
