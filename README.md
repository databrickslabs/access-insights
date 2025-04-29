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

Cloud Storage Events need to be captured in order to begin understanding the distribution of Managed and External tables.  Below is a breakdown of how that may be achieved in Azure and AWS.  This repo provides the setup for both, but assumes that the resources are provisioned in advance.

### Azure

Storage Logs in Azure will need to be routed to a central location via Diagnostic Settings.  Route them to a Central Event Hub or Storage Account

#### [OPTION 1]: Configure Storage Account for Logs

1. **Navigate to your Storage Account** in the Azure portal.
2. In the left-hand menu, under "Monitoring," select **Diagnostic settings**.
3. Click **+ Add diagnostic setting**.
4. Provide a **Diagnostic setting name** (e.g., `StorageAccountLogs`).
5. Under "Categories details," select the logs you want to capture. At a minimum, select:
    * `StorageRead`
    * `StorageWrite`
    * `StorageDelete`
6. Under "Destination details," select **Send to storage account**.
7. Choose your **Storage account** where logs will be stored.
8. Click **Save**.

#### Register Central Storage Account in Databricks Unity Catalog for Storage Logs

1. In your Azure Databricks workspace, navigate to the **Catalog** section.
2. Create a new **External Location**.
3. Provide a **Name** for the external location.
4. Enter the **Storage credential** details, ensuring that the Access Connector/System Assigned Managed Identity for Databricks has "Storage Blob Data Contributor" rights on the Storage Account.
5. Enter the **URL** in the format: `abfss://insights-logs-storageread@[StorageAccountName].dfs.core.windows.net/` (Replace `[StorageAccountName]` with the actual name of your storage account).
6. Click **Create**.
7. Do this for Read, Write, and Delete locations

#### [OPTION 2]: Configure Event Hub for Diagnostic Logs

1. **Navigate to your Event Hub Namespace** in the Azure portal.
2. In the left-hand menu, under "Monitoring," select **Diagnostic settings**.
3. Click **+ Add diagnostic setting**.
4. Provide a **Diagnostic setting name** (e.g., `EventHubDiagnosticLogs`).
5. Under "Categories details," select the logs you want to capture.
6. Under "Destination details," select **Send to Event Hub**.
7. Choose your **Event Hub Namespace** and the specific **Event Hub** where logs will be sent.
8. Click **Save**.

#### Verification

* After a short period, you should see logs appearing in your specified Storage Account containers and Event Hub.
* You can verify the External Location setup in Databricks Unity Catalog by browsing the location and ensuring you can access the files.

#### Note

* Ensure that the necessary IAM permissions are in place for Databricks to access the Storage Account and Event Hub.
* Adjust the log categories selected based on your specific monitoring requirements.
* For detailed instructions on Azure Diagnostic Settings, refer to the official Azure documentation.

### Azure Pipeline Setup

The first time the pipeline runs it will setup a catalog and schema for the output table `azure_raw_storage_logs`, and materialized view named `azure_storage_logs` under the same catalog and schema.

All injected variables can be edited in the file `databricks.yml`. Below are the variables, description, and usage.

#### Variables 

- `catalog`: 
  - value: `slog` 
  - description: target catalog for tables and views to be created
- `schema`: 
  - value: `default`
  - description: target schema for tables and views to be created
- `raw_table`: 
  - value: `azure_raw_storage_logs`
  - description: table containing the raw data from the eventhub
- `materialzed_table`: 
  - value: `azure_storage_logs_vw`
  - description: name of the materialized view created off of the `raw_table` name
- `checkpoint`: 
  - value: `abfss://slog@stsezsandbox07.dfs.core.windows.net/checkpoints/azure_raw_storage_log` 
  - description: external location for the checkpoint path for the streaming operation
- `secret-scope`:
  - value: `slog-scope` 
  - description: secret scope used in the pipeline
- `eh-namespace`: 
  - value: `eh-namespace` 
  - description: the eventhub namespace where the storage logs are sent to, and is gathered from the secret scope
- `eh-name`: 
  - value: `slog`
  - description: the eventhub name
- `eh-conn-string`:
  - value: `eh-slog`
  - description: the connect string for the eventhub, and is gathered from the secret scope

#### Pipeline Run

Ensure all prerequisites are setup, secret scope and values are correct, and variables are verified.

1. Deploy the pipeline using the databricks cli and asset bundles via the command 

```sh
databricks bundle deploy
```

2. Navigate the deployed pipeline, trigger the first run, and wait for successful completion 

## Insights

1. Run the notebook `SLOG - Exploration` under `/azure/notebooks` to determine the distribution of external tables across your accounts.
2. Review the visuals for the tables are good candidates for migration.  
  - Tables that are flagged in the notebook are good candidates.  
3. **Repeat**

### Non-UC Paths

1. The exploration notebook has another query that interrogates paths with _delta_log to determine other candidates that may orginate from HMS or stricly paths.  
