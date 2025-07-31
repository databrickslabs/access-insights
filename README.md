# Access Insights

This Access Insights dashboard gathers details about a customers’ tables, for example by showing which readers and writers are accessing these tables (using storage logs). 

## Project Description

Access Insights helps customers find the best UC external table candidates which they [can convert to UC managed tables](https://docs.databricks.com/aws/en/tables/convert-external-managed) first, by analyzing cloud storage logs and providing insights.

## Why Convert to UC Managed Tables

UC managed tables provide numerous benefits over UC external tables, such as increasing query speeds and lowering storage costs (using Predictive Optimization, for example). See our [blog](https://www.databricks.com/blog/how-unity-catalog-managed-tables-automate-performance-scale) for more information on the benefits of UC managed tables, the preferred table type in Unity Catalog.

## Which Tables Should be Converted First?

The following information may be useful when analyzing or converting UC external table candidates:

- Table type
  - In this context, UC external tables should be identified to convert to UC managed.
- External (non-Databricks) read/write access patterns
  - Tables with Databricks reads/writes only, should be converted first
  - Tables with external (non-Databricks) reads from tools that support reads from UC managed tables (see list, not exhaustive), can be converted next
- Table size
  - Tables <1 TB should be converted first, followed by tables 1-10 TB size, followed by tables > 10 TB in size.
- Path-based access
  - Tables who have readers/writers that use path-based access, must be updated to use name-based access, otherwise they will fail (for the time being).
- Use of the Uniform table feature
  - Tables with Uniform enabled, must have Uniform dropped before converting the table to be UC managed (for the time being), however, this does not necessarily impact which tables should be converted first.
- Commit rate
  - Tables with a lower commit rate (such as <2,000 commits/day) should be converted first, and those which are faster moving (such as >2,000 commits/day) should be converted last
- Whether optimize jobs exist on a table
  - These should be canceled before conversion, since UC managed tables will take care of running optimizations automatically for you (not canceling may lead to conflicts).
- \# of files
  - Tables with appropriately sized files (not too many small files) are ideal to convert first.
- Multiple Cloud Regions
  - If the default managed location of your Unity Catalog metastore, catalog, or schema is in a different cloud region from the storage location of the external table being converted, you may incur additional cross-region data transfer costs.

## Project Support

Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## General Feedback

For general feedback or suggestions for improvement, please fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSf2Mz_S9bzCwABsaumDMvloJc5zGRtJ2HYpMvGFI08iFSjv6g/viewform?usp=sharing&ouid=117813373515543542412). 

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
## Estimating Reader and Writer Downtime
Exact downtime for readers and writers during conversion from UC external tables to UC managed tables can be estimated as follows:
Table Size
Recommended Cluster Size
Time for Data Copy 
Reader*/Writer Downtime
100 GB or less
32-core / DBSQL small
~6min or less
~1-2min or less
1 TB
64-core / DBSQL medium
~30 min
~1-2min 
10 TB
256-core / DBSQL x-large
~1.5 hrs
~1-5min

Project Support
Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs). They are provided AS-IS and we do not make any guarantees of any kind. Please do not submit a support ticket relating to any issues arising from the use of these projects.
Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo. We do welcome your feedback. These GitHub issues will be reviewed as time permits, but there are no formal SLAs for support.

  
