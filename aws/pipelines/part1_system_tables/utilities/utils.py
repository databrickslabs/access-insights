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
                df_history = (
                    DeltaTable.forName(spark, namespace)
                    .history()
                    .limit(5)
                    .select(
                        col("engineInfo").alias("engineInfo")
                    )    
                )

                table_vals["history"] = [str(row.engineInfo) for row in df_history.collect()]



            except Exception as exc:
                table_vals["status"] = "\n".join(
                    filter(None, [table_vals.get("status"), str(exc)])
                )

        table_details.append(table_vals)

    return spark.createDataFrame(table_details, schema=schema)
