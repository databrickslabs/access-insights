# PROJECT NAME

SLOG - Storage Log Assessment

## Project Description

SLOG helps customers understand the distribution of their data in Cloud Storage in terms of [Unity Catalog Managed vs External](https://docs.databricks.com/aws/en/data-governance/unity-catalog/#managed-versus-external-tables-and-volumes) to help them find good candidates for migration from External to Managed configuration. It explores whether or not External Tables are leveraged by external tools.  

## Why Migrate

Managed tables provide numerous benefits over External tables (Predictive Optimization as one example) and is the preferred configuration for tables in Unity Catalog. 

## Project Support

Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## Prerequisites

Cloud Storage Events need to be captured in order to view the distribution of Managed and External tables. See the README files in the Azure and AWS folders for a guide on setting these up properly.
 
- [AWS](aws/README.md)
- [Azure](azure/README.md)

The rest of the repo assumes that the resources are provisioned.

## Setup (Azure)

1. Run the notebook provided after the prerequiste steps were met.  
e.g for Azure, run /azure/setup/Eventhub Storage Log Setup.ipynb.  This setup assumes senstive information is managed through Secret Scope in Databricks.
2. The setup requires a few parameters to consider, target table name, path for checkpoint.
3. Run the [vw_storage_logs_information_schema.sql](azure/queries/vw_storage_logs_information_schema.sql) query to create a Materialized View which joins the raw audit logs with Information Schema.
4. Configure and run the workflow [eventhub_storage_log_workflow.yml](azure/setup/workflow/eventhub_storage_log_workflow.yml) at your scheduled preference. 
* Run the [refresh query](azure/queries/refresh_slog.default.vw_storageLogs_information_schema.sql) if an updated Materialized View is required before running the pipeline
5. Run the pipeline and wait for successful completion before proceeding to the notebook for exploration.

## Insights (Azure)

1. Review [Notebook SLOG - Exploration](azure/notebooks/SLOG%20Exploration.ipynb) to determine the distribution of external tables across your accounts.
2. Review which tables are good candidates for migration.  Tables that are flagged in the notebook are good candidates.  
3. **Repeat**

### Non-UC Paths

1. The exploration notebook has another query that interrogates paths with _delta_log to determine other candidates that may orginate from HMS or stricly paths.  
