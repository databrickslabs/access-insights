# Prerequisites
- Cloud Trail setup
- S3-setup
- Onboarding on Databricks
## Cloud Trail Setup
- **Enable CloudTrail Logs**-- Goto Cloudtrail and Create a Trail and choose a our logs bucket to send the logs. Encrypting the logs or not is our choice.

![](https://miro.medium.com/v2/resize:fit:4800/format:webp/1*K5a0rIA4Tfwog8kEeC9_dw.png)

- **Select Events** - We can choose what all events to be logged. Select all the events along with management events and data events. Primarily for DataEvents we select only S3 .

![](https://miro.medium.com/v2/resize:fit:4800/format:webp/1*GCtpwPYp7c1J6wBCXe-Zsg.png)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*YlIqnSrWFO8e-JBmL-9frA.png)
- **Final Access to your logs in your designated S3** - In the logs folder of S3 bucket, all our logs are saved. Cloudtrail logs are saved in the subfolder of AWSLogs

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*NOfAjjwRxPIXvBXaRoZJHQ.png)


## S3-setup
- Note - Always configure your S3 to store logs in a different dedicated S3 for logs
- Log into your console and go to your S3 . Click on Properties tab. You could find server access logging. Click on Edit

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*C78Gi1zkHudmvirwIyljsA.png)
-  Click on Enable . You need to provide a Destination bucket. Browse the list of the available S3 buckets. Select the log bucket which is created as part of cloud trail configuration.
Paste the full S3 path . Save the changes once its done.
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Jfi3NsQejX9QRnWilKxjuw.png)

