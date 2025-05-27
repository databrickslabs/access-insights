# Azure Prerequisites

Storage Logs in Azure will need to be routed to a central location via Diagnostic Settings.  Route them to a Central Event Hub or Storage Account.
This pipeline is configured to leverage an azure event hub for diagnostic logging. The ingestion can be adjusted to leverage a storage account
as the target for diagnostic logging.

## Pipeline Configurations

These configurations are all contained in the file `./databricks.yml`, and need to be changed before deploying.

- `host`: workspace URL to deploy the resources to 
- `secret-scope`: secret scope in the target workspace
- `eh-name`: event hub name
- `eh-namespace`: event hub namespace
- `tenant-id`: tenant id for azure 
- `client-id`: client id with access to read from storage, event hub, and MS graph 
- `client-secret`: client secret id value from the secret scope 
- `get-azure-apps`: if you want to scrape the MS graph for entra app ids


## Setup Options

### Preferred Option: Event Hub for Diagnostic Logs

1. Create or leverage an existing **Event Hub** and **Event Hub Namespace**
1. Identity the storage account(s) to monitor 
3. **Navigate to the storage account** in the Azure portal.
4. In the left-hand menu, under **Monitoring**, select **Diagnostic settings**.
5. Select **blob** as a minimum requirement.
6. Click **+ Add diagnostic setting**.
5. Under **Categories groups**, select the logs you want to capture. At a minimum, select:
    * `StorageRead`
    * `StorageWrite`
    * `StorageDelete`
9. Under **Destination details**, select **Stream to an event hub**.
10. Choose your **Event Hub Namespace** and the specific **Event Hub** where logs will be sent.
11. Click **Save**.


### OPTION 2: Storage Account for Diagnostic Logs

1. Identity the storage account(s) to monitor 
3. **Navigate to the storage account** in the Azure portal.
4. In the left-hand menu, under **Monitoring**, select **Diagnostic settings**.
5. Select **blob** as a minimum requirement.
6. Click **+ Add diagnostic setting**.
5. Under **Categories groups**, select the logs you want to capture. At a minimum, select:
    * `StorageRead`
    * `StorageWrite`
    * `StorageDelete`
6. Under **Destination details**, select **Archive to storage account**.
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

## Verification

* After a short period, you should see logs appearing in your specified Storage Account containers and Event Hub.
* You can verify the External Location setup in Databricks Unity Catalog by browsing the location and ensuring you can access the files.

## Note

* Ensure that the necessary IAM permissions are in place for Databricks to access the Storage Account, Event Hub, and MS Graph.
  - Service Principal requires *Azure Event Hubs Data Receiver* on the Event Hub Namespace
    - Refer to [Configure the Structured Streaming Kafka Connector](https://learn.microsoft.com/en-us/azure/databricks/connect/streaming/kafka#configuring-the-structured-streaming-kafka-connector) for additional help
  - Service Principal requires access to read from the MS Graph
* Adjust the log categories selected based on your specific monitoring requirements.
* For detailed instructions on Azure Diagnostic Settings, refer to the official Azure documentation.
* Adjust the asset bundle settings under `./databricks.yml`, and `/resources` for specific deployment considerations
