# ACCESS_INSIGHTS
This Access Insights dashboard gathers details about a customers’ tables (using systemTables/ storage logs). 

There are 2 Modes to this implementation
- **External Run** - This has cloud dependencies such as CloudTrail, Rerouting Log settings of S3, right IAM Roles.
- **Internal Run**- This mode is gathers info of tables from system Tables.

# External Run
## AWS Prerequisites

Storage Logs in AWS will need to be routed to a central location via CLoud Trail. Route them to a Central Storage Account. This pipeline is configured to leverage an S3 from central CLoudTrail.

The following are required for tracking access to managed and external tables in AWS:
- CloudTrail setup
- S3 setup
- Onboarding on Databricks

## CloudTrail Setup

1. **Enable CloudTrail Logs**  
    - Navigate to CloudTrail, create a Trail, and select a logs bucket to store the logs. Encrypting the logs is optional.

    <img src="https://miro.medium.com/v2/resize:fit:4800/format:webp/1*K5a0rIA4Tfwog8kEeC9_dw.png" width="500" height="250"/>

2. **Select Events**  
    - Choose the events to log. Select all events, including management events and data events. For data events, primarily select S3.
      
    <img src="https://miro.medium.com/v2/resize:fit:4800/format:webp/1*GCtpwPYp7c1J6wBCXe-Zsg.png" width="500" height="300"/>  
    <img src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*YlIqnSrWFO8e-JBmL-9frA.png" width="500" height="250"/>

3. **Access Logs in S3**  
    - CloudTrail logs are saved in the `AWSLogs` subfolder of the designated S3 bucket.  
    <img src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*NOfAjjwRxPIXvBXaRoZJHQ.png" width="500" height="250"/>

## S3 Setup

**Note: Always configure a separate S3 bucket to store logs.**  

- Log in to the AWS Management Console and navigate to S3.  
- Select the desired bucket, go to the **Properties** tab, and locate the **Server access logging** section. Click **Edit**.  
<img src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*C78Gi1zkHudmvirwIyljsA.png" width="500" height="250"/>

- Click Enable under "Service Access Logging" and provide a destination bucket. Browse the list of available S3 buckets and select the log bucket created during the CloudTrail configuration. 
<img src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Jfi3NsQejX9QRnWilKxjuw.png" width="500" height="250"/>

# PipeLine creation Steps
- Clone the AccessInsights code Repo https://github.com/databrickslabs/access-insights
<img src="https://e2-demo-field-eng.cloud.databricks.com/ajax-api/2.0/workspace-files/Users/samer.zabaneh%40databricks.com/access-insights/aws/resources/Screenshot%202025-07-16%20at%206.53.15%E2%80%AFPM.png" width="500" height="250"/>


- The Folder Structure resembles below

<img src="https://e2-demo-field-eng.cloud.databricks.com/ajax-api/2.0/workspace-files/Users/samer.zabaneh%40databricks.com/access-insights/aws/resources/Screenshot 2025-07-16 at 8.25.35 PM.png" width="500" height="250/">

## Pipeline Configurations

These configurations are all contained in the file `./databricks.yml`, and need to be changed before deploying.

- `host`: workspace URL to deploy the resources to 
- `ingestPath`: Path to your cloud trail (Egs:-'s3://databricks-deployment-fe/AWSLogs/997819012307/CloudTrail/*/*/*/*/*') 
- `secret-scope`: secret scope in the target workspace
- `Default catalog`: Catalog to create your schema to store your tables and views
- `Default schema`: schema to store your tables and views

<img src="https://e2-demo-field-eng.cloud.databricks.com/ajax-api/2.0/workspace-files/Users/samer.zabaneh%40databricks.com/access-insights/aws/resources/Screenshot 2025-07-16 at 8.32.59 PM.png" width="500" height="450/">

## Limitations

1. Hive metastore details will only be captured from the workspace where the pipeline is running 
1. CloudTrail Logs needs to be configured to right options to capture right events.