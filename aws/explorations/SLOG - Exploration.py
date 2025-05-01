# Databricks notebook source
# MAGIC %sql
# MAGIC select
# MAGIC   *
# MAGIC from
# MAGIC   slog.default.cloudtrail_with_auditevents
# MAGIC where
# MAGIC   table_name is not null
# MAGIC limit 100;

# COMMAND ----------

# MAGIC %sql
# MAGIC with good_candidates as (
# MAGIC   SELECT
# MAGIC     table_type,
# MAGIC     eventCategory,
# MAGIC     eventSource,
# MAGIC     table_full_name,
# MAGIC     table_url,
# MAGIC     data_source_format,
# MAGIC     storage_path,
# MAGIC     AssumeRole_count,
# MAGIC     GetObject_count,
# MAGIC     PutObject_count,
# MAGIC     DeleteObject_count,
# MAGIC     ListObjects_count
# MAGIC   FROM
# MAGIC     (
# MAGIC       SELECT
# MAGIC         table_type,
# MAGIC         eventCategory,
# MAGIC         eventSource,
# MAGIC         requestParameters.prefix AS prefix,
# MAGIC         table_full_name,
# MAGIC         table_url,
# MAGIC         data_source_format,
# MAGIC         storage_path,
# MAGIC         eventName,
# MAGIC         COUNT(*) as event_count
# MAGIC       FROM
# MAGIC         slog.default.cloudtrail_with_auditevents
# MAGIC       WHERE
# MAGIC         table_name IS NOT NULL
# MAGIC       GROUP BY
# MAGIC         table_type,
# MAGIC         eventCategory,
# MAGIC         eventSource,
# MAGIC         requestParameters.prefix,
# MAGIC         table_full_name,
# MAGIC         table_url,
# MAGIC         data_source_format,
# MAGIC         storage_path,
# MAGIC         eventName
# MAGIC     )
# MAGIC       PIVOT (
# MAGIC         SUM(event_count) FOR eventName IN (
# MAGIC           'AssumeRole' AS AssumeRole_count,
# MAGIC           'GetObject' AS GetObject_count,
# MAGIC           'PutObject' AS PutObject_count,
# MAGIC           'DeleteObject' AS DeleteObject_count,
# MAGIC           'ListObjects' AS ListObjects_count
# MAGIC         )
# MAGIC       )
# MAGIC )
# MAGIC select
# MAGIC   *
# MAGIC from
# MAGIC   good_candidates
