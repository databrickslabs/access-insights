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
        StructField("history", ArrayType(StringType(), True), True),
        StructField("status", StringType(), True),
        StructField("reads", StringType(), True),
        StructField("writes", StringType(), True),
        StructField("internal_reads", LongType(), True),
        StructField("internal_writes", LongType(), True),
        StructField("external_reads", LongType(), True),
        StructField("external_writes", LongType(), True),
        # StructField("requestID", StringType(), True),
        # StructField("userAgent", StringType(), True),
        # StructField("userIdentity", StructType(), True),
        # StructField("requestParameters", MapType(StringType(), StringType(), True), True,),
    ]
)