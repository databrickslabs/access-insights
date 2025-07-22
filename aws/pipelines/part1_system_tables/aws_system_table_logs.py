import dlt

import sys

from pyspark.dbutils import DBUtils
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()
sys.path.append(spark.conf.get("bundle.sourcePath"))

from utilities.schemas import (
    table_details_schema
)

from utilities.utils import (
    collect_table_details
)

dbutils = DBUtils(spark)

@dlt.table(name="all_table_details")
def all_table_details():
    df_info = spark.read.table("system.information_schema.tables").select(
        F.col("table_catalog"),
        F.col("table_schema"),
        F.col("table_name"),
        F.col("table_type"),
        F.col("data_source_format"),
        F.col("storage_path"),
        F.lit(None).alias("status"),
    )

    df = df_info.select(
        F.col("table_catalog"),
        F.col("table_schema"),
        F.col("table_name"),
        F.concat_ws(
            ".", F.col("table_catalog"), F.col("table_schema"), F.col("table_name")
        ).alias("full_namespace"),
        F.col("storage_path"),
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

    df = collect_table_details(spark=spark, df=df, schema=table_details_schema)

    return df
