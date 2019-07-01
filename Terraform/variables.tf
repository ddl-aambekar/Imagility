/* 

Terraform file to define which variables are used

This is NOT where you set the variables. Instead, they should be 
set at the command line, with .tfvars files, or with environment variables

 */

variable "aws_region" {
  description = "AWS region to launch servers."
  default     = "us-west-2"
}

variable "keypair_name" {
  description = "Name of your keypair"
  default     = "akshay-IAM-keypair"
}

variable "fellow_name" {
  description = "The name that will be tagged on your resources."
  default     = "Akshay"
}

variable "ami" {
  description = "AMI that contains the model with the SQS message listener"
  default     = "ami-0d169a6277386a513"
}

variable "ec2_name" {
  description = "The name for your instances in your cluster"
  default     = "Image-Processor"
}
