# Imagility

The purpose of this project is to deploy a machine learning model in production with focus on availability, resiliency, scaling, and monitoring. The machine learning model, which converts 2D images of chairs into 3D, was developed by Pravinth and can be found at 
```
https://github.com/pravinthsam/Ilios-3D-model-generation
``` 

The architecture for Imagility is as follows:

<img src="https://github.com/iamakshayba/Imagility/blob/master/readme_images/architecture.png"/>

The setup for this project entails the following:
1. A flask application using which user can upload 2D images and specify email address to receive processed images
2. S3 buckets, one for storing raw input images and another for storing processed output images, respectively.
3. Amazon SQS for sending messages to the autoscaling group.
4. DynamoDB for keeping status of processing of all images.
5. AWS Lambda for updating process status of images in dynamodb, fetching email of user who uploaded image, and sending an email to retrieve the processed file from S3, via AWS SES, to the requestor.
6. Autoscaling group of EC2s to ensure availability, resiliency, and scaling of models according to incoming message traffic.
7. AWS CloudWatch for monitoring AWS managed services and alerting on approx. age of oldest messages in SQS.


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

# Files in this project

1. Flask app (app.py): This file contains the flask app code. Run the file by navigating to the file path in your favorite terminal and type
```
python app.py
```
This will bring up a user interface, accessible at http://localhost:5000, that allows users to upload single or multiple 2D images and specify their email id.

2. Clone the repo
```
https://github.com/pravinthsam/Ilios-3D-model-generation
``` 
to an EC2 instance. 

3. demo.py: This file contains changes that allow the processed output files to be stored on S3 bucket. Simply replace the demo.py file present in Ilios-3D-model-generation/src folder after cloning the above repo with this file. 

4. Message Listener: This code will listen to message from AWS SQS. Copy the message listener code on each EC2 instance that has the model, under the path ~/Ilios-3D-model-generation/src. You can activate the code by running the below commands in the ssh shell
```
cd ~/Ilios-3D-model-generation/src
source activate ilios
python message_listener.py start
``` 
The above commands activate the conda environment and start a daemon thread that polls for messages from the SQS queue.

5. Terraform: The terraform files for bringing up the infrastructure are housed in this folder. 


