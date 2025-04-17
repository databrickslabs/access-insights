# PROJECT NAME
SLOG - Storage Log Assessment

## Project Description
Understanding of what is accessing data leveraging Cloud Native Storage and Information Schema in Databricks

## Project Support
Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.


## Prerequisites
### Azure
Storage Logs in Azure will need to be routed to a central location via Diagnostic Settings.  Route them to an Central Event Hub or Storage Account

#### Configure Storage Account for Logs

1.  **Navigate to your Storage Account** in the Azure portal.
2.  In the left-hand menu, under "Monitoring," select **Diagnostic settings**.
3.  Click **+ Add diagnostic setting**.
4.  Provide a **Diagnostic setting name** (e.g., `StorageAccountLogs`).
5.  Under "Categories details," select the logs you want to capture. At a minimum, select:
    *   `StorageRead`
    *   `StorageWrite`
    *   `StorageDelete`
6.  Under "Destination details," select **Send to storage account**.
7.  Choose your **Storage account** where logs will be stored.
8.  Click **Save**.

#### Configure Event Hub for Diagnostic Logs

1.  **Navigate to your Event Hub Namespace** in the Azure portal.
2.  In the left-hand menu, under "Monitoring," select **Diagnostic settings**.
3.  Click **+ Add diagnostic setting**.
4.  Provide a **Diagnostic setting name** (e.g., `EventHubDiagnosticLogs`).
5.  Under "Categories details," select the logs you want to capture.
6.  Under "Destination details," select **Send to Event Hub**.
7.  Choose your **Event Hub Namespace** and the specific **Event Hub** where logs will be sent.
8.  Click **Save**.

####: Register Central Storage Account in Databricks Unity Catalog for Storage Logs

1.  In your Azure Databricks workspace, navigate to the **Catalog** section.
2.  Create a new **External Location**.
3.  Provide a **Name** for the external location.
4.  Enter the **Storage credential** details, ensuring that the Access Connector/System Assigned Managed Identity for Databricks has "Storage Blob Data Contributor" rights on the Storage Account.
5.  Enter the **URL** in the format: `abfss://insights-logs-storageread@[StorageAccountName].dfs.core.windows.net/` (Replace `[StorageAccountName]` with the actual name of your storage account).
6.  Click **Create**.
7.  Do this for Read, Write, and Delete locations

## Verification

*   After a short period, you should see logs appearing in your specified Storage Account containers and Event Hub.
*   You can verify the External Location setup in Databricks Unity Catalog by browsing the location and ensuring you can access the files.

## Note

*   Ensure that the necessary IAM permissions are in place for Databricks to access the Storage Account and Event Hub.
*   Adjust the log categories selected based on your specific monitoring requirements.
*   For detailed instructions on Azure Diagnostic Settings, refer to the official Azure documentation.


#### Setup 
1. Run the notebook provided after the prerequiste steps were met.  
e.g for Azure, run /azure/setup/Eventhub Storage Log Setup.ipynb

#### Insights 
1. Review the Notebook SLOG - Exploration in the /azure/notebooks area to and determine the distribution of external tables across your accounts.
2. Review which tables you would like to migrate
3. **Repeat**

