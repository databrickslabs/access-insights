# AWS Prerequisites

The following are required for tracking access to managed and external tables in AWS:

- CloudTrail setup
- S3 setup
- Onboarding on Databricks

## CloudTrail Setup

1. **Enable CloudTrail Logs**  
    - Navigate to CloudTrail, create a Trail, and select a logs bucket to store the logs. Encrypting the logs is optional.  
    ![](https://miro.medium.com/v2/resize:fit:4800/format:webp/1*K5a0rIA4Tfwog8kEeC9_dw.png)

2. **Select Events**  
    - Choose the events to log. Select all events, including management events and data events. For data events, primarily select S3.  
    ![](https://miro.medium.com/v2/resize:fit:4800/format:webp/1*GCtpwPYp7c1J6wBCXe-Zsg.png)  
    ![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*YlIqnSrWFO8e-JBmL-9frA.png)

3. **Access Logs in S3**  
    - CloudTrail logs are saved in the `AWSLogs` subfolder of the designated S3 bucket.  
    ![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*NOfAjjwRxPIXvBXaRoZJHQ.png)

## S3 Setup

**Note: Always configure a separate S3 bucket to store logs.**  

- Log in to the AWS Management Console and navigate to S3.  
- Select the desired bucket, go to the **Properties** tab, and locate the **Server access logging** section. Click **Edit**.  
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*C78Gi1zkHudmvirwIyljsA.png)

- Click Enable under "Service Access Logging" and provide a destination bucket. Browse the list of available S3 buckets and select the log bucket created during the CloudTrail configuration. 
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Jfi3NsQejX9QRnWilKxjuw.png)
