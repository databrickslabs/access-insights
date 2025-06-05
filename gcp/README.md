# GCP Prerequisites

How to Set Up GCP Storage Audit Logs Per Bucket (Capture Read & Write Events)
1. Go to Google Cloud Console > IAM & Admin > Audit Logs
Navigate to the Audit Logs page in the Google Cloud Console for your project.

2. Select Google Cloud Storage Service
Check Admin read, Data read, and Data Write events.

3. Choose the Buckets and Log Types
Run in the GCP Clould Shell for each Bucket to be monitored
gcloud storage buckets update gs://[bucket_to_be_monitored] --log-bucket=gs://[bucket_for_logging] --log-object-prefix=slog

4. Register Locations in Unity Catalog
* 1. Create a Storage Credential in Unity Catalog
In your Databricks workspace (enabled for Unity Catalog), go to Catalog > External data > Credentials.
Click Create credential, select GCP Service Account, and provide a name.
Databricks will generate a Google Cloud service account for you—note the service account email.

* 2. Grant the Service Account Access to Your GCS Bucket
In Google Cloud Console, navigate to IAM & Admin > IAM.
Grant the Databricks-generated service account the necessary permissions (typically storage.buckets.get, storage.objects.get, storage.objects.list, storage.objects.create, storage.objects.delete) on your target GCS bucket.

* 3. Create an External Location in Unity Catalog
In Databricks, go to Catalog > Settings > External Locations.
Click Create external location.
Enter a name, specify the GCS bucket URL (e.g., gs://your-bucket-name), and select the storage credential you created earlier.
Click Create and then Test connection to verify access.
* 4. Assign Permissions to the External Location
In Unity Catalog, grant appropriate privileges (such as ALL PRIVILEGES) on the external location to users or service principals as needed.

## Pipeline Configurations

After prerequisite Steps are Completed, Run the Pipeline and view the Dashboard for Classifications of registered external tables.

## Verification
