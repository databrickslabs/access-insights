import dlt
from pyspark.sql.functions import col, explode, to_date

schema_hints = """Records.element.requestParameters map<string, string>,
                     Records.element.responseElements map<string, string>,
                     Records.element.resources array<map<string, string>>,
                     Records.element.serviceEventDetails map<string, string>,
                     Records.element.additionalEventData map<string, string>,
                     Records.element.userIdentity.sessionContext.webIdFederationData struct<federatedProvider:string, attributes:map<string,string>>"""
 
ingest_path = spark.conf.get("ingestPath")
 
options = {
    "cloudFiles.format": "json",
    "cloudFiles.inferColumnTypes": "true",
    "cloudFiles.schemaEvolutionMode": "addNewColumns",
    "cloudFiles.schemaHints": schema_hints
}

@dlt.view(
    name="cloudtrail_ingest"
)
@dlt.expect_or_fail("valid_records", "size(Records) > 0") # this helps us monitor any failures in parsing the whole Record
@dlt.expect_or_fail("clean_schema", "_rescued_data is null") # this helps us monitor any columns that fail to parse
def cloudtrail_ingest():
    return (spark
            .readStream
            .format("cloudfiles")
            .options(**options)
            .load(ingest_path)
           )
  

@dlt.table(
  name="cloudtrail_logs",
  table_properties={
    "quality": "bronze", 
    "pipelines.autoOptimize.managed": "true",
    "delta.autoOptimize.optimizeWrite": "true",
    "delta.autoOptimize.autoCompact": "true"
  }
)
def cloudtrail_logs():
  return (dlt.read_stream("cloudtrail_ingest")
          .select(explode('Records').alias('record')) # flatten the nested records
          .select(
            'record.*', 
            #col('_metadata.file_path').alias('filename'), 
            to_date('record.eventTime').alias('eventDate')
          )
          .filter(col("eventDate") >= "2025-04-28")
          .filter(col("record.eventSource").isin("sts.amazonaws.com", "s3.amazonaws.com"))
          .filter(col("record.eventName").isin("AssumeRole", "GetObject", "PutObject", "DeleteObject", "ListObjects"))
  )