# Azure Prerequisites

Storage Logs in Azure will need to be routed to a central location via Diagnostic Settings.  Route them to a Central Event Hub or Storage Account

## Setup Options

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

## Verification

* After a short period, you should see logs appearing in your specified Storage Account containers and Event Hub.
* You can verify the External Location setup in Databricks Unity Catalog by browsing the location and ensuring you can access the files.

## Note

* Ensure that the necessary IAM permissions are in place for Databricks to access the Storage Account and Event Hub.
  - Refer to [Configure the Structured Streaming Kafka Connector](https://learn.microsoft.com/en-us/azure/databricks/connect/streaming/kafka#configuring-the-structured-streaming-kafka-connector) for additional help
* Adjust the log categories selected based on your specific monitoring requirements.
* For detailed instructions on Azure Diagnostic Settings, refer to the official Azure documentation.
* Adjust the asset bundle settings under `/resources` for specific deployment considerations
