# Imagility

The setup for this project entails the following:
1. 2 S3 buckets, one for raw input images and another for output processed images, respectively.
2. Amazon SQS for sending messages to EC2.
3. DynamoDB for status keeping of all images.
4. AWS Lambda for updating process status of images in dynamodb, fetching email_id of developer who uploaded image, and sending email via AWS SES to the requestor.
5. Autoscaling group of EC2s to ensure availability, resiliency, and scaling of models according to incoming message traffic.
6. AWS CloudWatch for monitoring and alerting on approx age of oldest messages in SQS and average CPU Utilization to trigger autoscaling.


# AWS Setup
1. Create a AWS account (or use an existing one).
2. Create an IAM admin user and group. AWS credentialling is confusing. This instruction creates a new sub-user that will be safer to use than the root account you just created in step 1.
3. Get the access key and secret access key from the IAM administrator user you just created.  
• Go to the IAM console  
• Choose Users and then the administrator user you just created.  
• Select the Security Credentials tab and then hit Create Access Key  
• Choose Show   
• We need to export these as enviornment variables in your ~/.bash_profile. You should add something that looks like this to the bottom of your profile using your favorite text editor, where the keys are your own of course:
```
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```
Then source your profile ```source ~/.bash_profile``` and now your laptop will be fully authorized to create resources on AWS!
