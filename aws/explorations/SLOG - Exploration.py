# Databricks notebook source
# MAGIC %md
# MAGIC ####Look into external tools 
# MAGIC - Objective - Look into read, write, delete operations on Storage for external tables ONLY.   To identify good candidates that can be migrated to Managed Tables.
# MAGIC   - Identify if an external table is being leveraged by an external platform. If it is it would not be a good candidate until the write operations subside.
# MAGIC
# MAGIC External Table -> catalog.schema.xyz
# MAGIC - Leveraged by Databricks
# MAGIC - Leveraged by External Platforms, Read Only for Good Candidate
# MAGIC
# MAGIC External Table -> catalog.schema.xyz
# MAGIC - Leveraged by Databricks
# MAGIC - Good Candidate would be read, write, delete

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH good_candidates AS (
# MAGIC   SELECT
# MAGIC     table_type,
# MAGIC     eventCategory,
# MAGIC     eventSource,
# MAGIC     table_full_name,
# MAGIC     table_url,
# MAGIC     data_source_format,
# MAGIC     storage_path,
# MAGIC     AssumeRole_count,
# MAGIC     COALESCE(GetObject_count, 0) + COALESCE(ListObjects_count, 0) AS reads,
# MAGIC     COALESCE(PutObject_count, 0) + COALESCE(DeleteObject_count, 0) AS writes
# MAGIC   FROM (
# MAGIC     SELECT
# MAGIC       table_type,
# MAGIC       eventCategory,
# MAGIC       eventSource,
# MAGIC       requestParameters.prefix AS prefix,
# MAGIC       table_full_name,
# MAGIC       table_url,
# MAGIC       data_source_format,
# MAGIC       storage_path,
# MAGIC       eventName,
# MAGIC       COUNT(*) AS event_count
# MAGIC     FROM
# MAGIC       slog.default.cloudtrail_with_auditevents
# MAGIC     WHERE
# MAGIC       table_name IS NOT NULL
# MAGIC     GROUP BY
# MAGIC       table_type,
# MAGIC       eventCategory,
# MAGIC       eventSource,
# MAGIC       requestParameters.prefix,
# MAGIC       table_full_name,
# MAGIC       table_url,
# MAGIC       data_source_format,
# MAGIC       storage_path,
# MAGIC       eventName
# MAGIC   ) PIVOT (
# MAGIC     SUM(event_count) FOR eventName IN (
# MAGIC       'AssumeRole' AS AssumeRole_count,
# MAGIC       'GetObject' AS GetObject_count,
# MAGIC       'PutObject' AS PutObject_count,
# MAGIC       'DeleteObject' AS DeleteObject_count,
# MAGIC       'ListObjects' AS ListObjects_count
# MAGIC     )
# MAGIC   )
# MAGIC )
# MAGIC SELECT
# MAGIC   case when writes = 0 then 1 else 0 end as `good_candidate`,
# MAGIC   *
# MAGIC FROM
# MAGIC   good_candidates
# MAGIC WHERE
# MAGIC   table_type = 'EXTERNAL' 
# MAGIC   and data_source_format = 'DELTA'
