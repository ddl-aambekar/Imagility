# Imagility

To run the code in this repo, you will need the following tools-
1. Terraform
2. Ansible
3. AWS
4. 



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
