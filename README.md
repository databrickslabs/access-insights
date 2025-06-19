# Access Insights

Access Insights - gather details into readers and writers to external tables from storage logs 

## Project Description

Access Insights helps customers understand the distribution of their data in Cloud Storage in terms of [Unity Catalog Managed vs External](https://docs.databricks.com/aws/en/data-governance/unity-catalog/#managed-versus-external-tables-and-volumes) to help them find good candidates for migration from External to Managed configuration. It explores whether or not External Tables are leveraged by external tools.  

## Why Migrate

Managed tables provide numerous benefits over External tables (Predictive Optimization as one example) and is the preferred configuration for tables in Unity Catalog. 

## Project Support

Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## Prerequisites

Cloud Storage Events need to be captured in order to view the distribution of Managed and External tables. See the README files in the Azure and AWS folders for a guide on setting these up properly.
 
- [AWS](aws/README.md)
- [Azure](azure/README.md)
- [GCP](gcp/README.md)

The rest of the repo assumes that the resources are provisioned.

Storage Logs in Azure will need to be routed to a central location via Diagnostic Settings.  Route them to a Central Event Hub or Storage Account.


## Deployed Databricks Resources

A Databricks Asset bundle is created for each of the cloud providers above. Use the Databricks CLI to deploy the bundle into a provided target workspace. The 
bundle will deploy the following assets. 

- `pipeline`: A DLT pipeline to create and manage storage log tables 
- `dashboard`: A dashboard that leverages the tables created from the Declartive pipeline, and system tables. 
  - Tables are classifed as:
    - `Databricks Readers`: Table(s) that have Storage Events that are only Reads from within Databricks Unity Catalog
    - `Databricks Readers & Writers`: Table(s) that have Storage Events that contain both Read & Write events but are within Databricks Unity Catalog
    - `Non-Databricks Readers`: Table(s) that may be a blend of Databricks + External read events and classified considered as external, i.e. having external tools not using Unity Catalog
    - `Non-Databricks Readers + Writers`: Table(s) that may be a blend of Databricks + External read and write events that will be classified as external, i.e. having external tools that read/write to the table(s) not using Unity Catalog

  ![Access Insights Dashboard](/imgs/dashboard_sample.png)