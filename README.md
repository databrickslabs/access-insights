# SLOG

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

Storage Logs in Azure will need to be routed to a central location via Diagnostic Settings.  Route them to a Central Event Hub or Storage Account

#### Pipeline Run

Ensure all prerequisites are setup, secret scope and values are correct, and variables are verified.

1. Clone the Repo
2. Deploy the pipeline using the databricks cli and asset bundles via the command 

```sh
cd azure && databricks bundle deploy
```


3. Navigate to the deployed pipeline, trigger the first run, and wait for successful completion 


## Insights

1. Review [Notebook SLOG - Exploration](azure/notebooks/SLOG%20Exploration.ipynb) to determine the distribution of external tables across your accounts.
2. Review which tables are good candidates for migration.  Tables that are flagged in the notebook are good candidates.  

### Non-UC Paths

1. The exploration notebook has another query that interrogates paths with _delta_log to determine other candidates that may originate from HMS or strictly paths.  

