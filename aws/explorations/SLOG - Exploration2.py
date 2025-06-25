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

# COMMAND ----------

# MAGIC %sql
# MAGIC select
# MAGIC   userAgent,
# MAGIC   count(*)
# MAGIC from
# MAGIC   slog.default.cloudtrail_logs
# MAGIC group by
# MAGIC   userAgent

# COMMAND ----------

# MAGIC %sql
# MAGIC Select distinct(userIdentity.invokedBy) from slog.default.cloudtrail_logs

# COMMAND ----------

plotdf = spark.sql("""
    select 
        case 
            when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
            when userAgent like '%Boto%' then 'Boto' 
            when userAgent like '%cli%' then 'cli' 
            else userAgent 
        end as userAgent, 
        count(*) 
    from slog.default.cloudtrail_logs 
    group by 
        case 
            when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
            when userAgent like '%Boto%' then 'Boto' 
            when userAgent like '%cli%' then 'cli' 
            else userAgent 
        end
""").toPandas()

# COMMAND ----------

display(plotdf)

# COMMAND ----------

import matplotlib.pyplot as plt

# Visualization 1: Distribution of requests by client type (bar chart)
plt.figure(figsize=(14, 9))
bars = plt.barh(plotdf['userAgent'], plotdf['count(1)'], color='skyblue')
plt.xlabel('Number of Requests (log scale)', fontsize=14)
plt.ylabel('Client Type', fontsize=14)
plt.title('Distribution of Storage Access by Client Type', fontsize=16)
plt.xscale('log')
plt.grid(axis='x', linestyle='--', alpha=0.7)

# Add count to top of the bar
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}', va='center', ha='left', fontsize=8)

plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %sql
# MAGIC select 
# MAGIC         case 
# MAGIC             when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
# MAGIC             when userAgent like '%Boto%' then 'Boto' 
# MAGIC             when userAgent like '%cli%' then 'cli' 
# MAGIC             else userAgent 
# MAGIC         end as userAgent, 
# MAGIC         count(*) 
# MAGIC     from slog.default.cloudtrail_logs 
# MAGIC     group by 
# MAGIC         case 
# MAGIC             when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
# MAGIC             when userAgent like '%Boto%' then 'Boto' 
# MAGIC             when userAgent like '%cli%' then 'cli' 
# MAGIC             else userAgent 
# MAGIC         end

# COMMAND ----------

# Visualization 2: Access types by client (stacked bar chart)
import matplotlib.pyplot as plt
import numpy as np
tempdf= spark.sql("""Select * FROM slog.default.cloudtrail_with_auditevents where table_type !="MANAGED" """)
tempdf2= spark.sql("""Select * FROM slog.default.cloudtrail_with_auditevents where table_type =="MANAGED" """)
tempdf.createOrReplaceTempView("externalview")
tempdf2.createOrReplaceTempView("managedlview")
access_by_type = spark.sql("""
  SELECT 
    table_type,
    case 
            when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
            when userAgent like '%Boto%' then 'Boto' 
            when userAgent like '%cli%' then 'cli' 
            else userAgent 
        end as userAgent, 
        count(*) as request_count 
  FROM 
    managedlview
  GROUP BY 
    table_type,
    case 
        when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
        when userAgent like '%Boto%' then 'Boto' 
        when userAgent like '%cli%' then 'cli' 
        else userAgent 
    end  
  ORDER BY 
    userAgent, request_count DESC
""").toPandas()

pivot_df = access_by_type.pivot(index='userAgent', columns='table_type', values='request_count').fillna(0)

plt.figure(figsize=(20, 12))
ax = pivot_df.plot(kind='bar', stacked=True, figsize=(20, 12), width=0.8)
plt.yscale('log')
plt.title('Access Types by Client', fontsize=16)
plt.xlabel('Client Type', fontsize=14)
plt.ylabel('Number of Requests (log scale)', fontsize=14)
plt.xticks(rotation=45, ha='right')

# Add total count and datatype to top of the bars
for i, (userAgent, row) in enumerate(pivot_df.iterrows()):
    total = row.sum()
    for j, (table_type, value) in enumerate(row.items()):
        if value > 0:
            plt.text(i, row[:j+1].sum(), f'{table_type}: {int(value)}', ha='center', va='bottom', fontsize=8, rotation=90)

plt.tight_layout()
plt.show()

# COMMAND ----------

access_by_type2 = spark.sql("""
  SELECT 
    table_type,
    case 
            when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
            when userAgent like '%Boto%' then 'Boto' 
            when userAgent like '%cli%' then 'cli' 
            else userAgent 
        end as userAgent, 
        count(*) as request_count 
  FROM 
    externalview
  GROUP BY 
    table_type,
    case 
        when userAgent like '%SDK%' or userAgent like '%sdk%' then 'SDK(java,ruby,js)' 
        when userAgent like '%Boto%' then 'Boto' 
        when userAgent like '%cli%' then 'cli' 
        else userAgent 
    end  
  ORDER BY 
    userAgent, request_count DESC
""").toPandas()

pivot_df = access_by_type2.pivot(index='userAgent', columns='table_type', values='request_count').fillna(0)

plt.figure(figsize=(20, 12))
ax = pivot_df.plot(kind='bar', stacked=True, figsize=(20, 12), width=0.8)
plt.yscale('log')
plt.title('Access Types by Client', fontsize=16)
plt.xlabel('Client Type', fontsize=14)
plt.ylabel('Number of Requests (log scale)', fontsize=14)
plt.xticks(rotation=45, ha='right')

# Add total count and datatype to top of the bars
for i, (userAgent, row) in enumerate(pivot_df.iterrows()):
    total = row.sum()
    for j, (table_type, value) in enumerate(row.items()):
        if value > 0:
            plt.text(i, row[:j+1].sum(), f'{table_type}: {int(value)}', ha='center', va='bottom', fontsize=8, rotation=90)

plt.tight_layout()
plt.show()
