from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    MapType,
    ArrayType,
    BooleanType,
)

table_details_schema = StructType(
    [
        StructField("table_catalog", StringType(), True),
        StructField("table_schema", StringType(), True),
        StructField("table_name", StringType(), True),
        StructField("full_namespace", StringType(), True),
        StructField("storage_path", StringType(), True),
        StructField("parsed_path", StringType(), True),
        StructField("table_type", StringType(), True),
        StructField("data_source_format", StringType(), True),
        StructField(
            "table_details",
            StructType(
                [
                    StructField("clustering_cols", ArrayType(StringType(), True), True),
                    StructField("min_reader_version", LongType(), True),
                    StructField("min_writer_version", LongType(), True),
                    StructField("num_files", LongType(), True),
                    StructField("partition_cols", ArrayType(StringType(), True), True),
                    StructField(
                        "properties",
                        MapType(StringType(), StringType(), True),
                        True,
                    ),
                    StructField("size_in_bytes", LongType(), True),
                    StructField(
                        "statistics",
                        MapType(StringType(), StringType(), True),
                        True,
                    ),
                    StructField("table_features", ArrayType(StringType(), True), True),
                ]
            ),
            True,
        ),
        StructField("status", StringType(), True),
    ]
)

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
