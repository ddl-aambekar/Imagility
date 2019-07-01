provider "aws" {
  region = "${var.aws_region}"
}

resource "aws_vpc" "vpc-prod-tf" {
  cidr_block = "10.0.0.0/26"

  tags = {
    Owner = "${var.fellow_name}"
    Name  = "imagility-vpc-tf"
  }
}

resource "aws_subnet" "subnet-prod-tf" {
  vpc_id     = "${aws_vpc.vpc-prod-tf.id}"
  cidr_block = "10.0.0.0/26"

  tags = {
    Name = "Main-tf"
  }
}

resource "aws_security_group" "sg-prod-tf" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"
  vpc_id      = "${aws_vpc.vpc-prod-tf.id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_launch_template" "lt-prod-tf" {
  name_prefix            = "LT_for_Imagility"
  image_id               = "ami-0d169a6277386a513"
  instance_type          = "m4.xlarge"
  vpc_security_group_ids = ["${aws_security_group.sg-prod-tf.id}"]
}

resource "aws_autoscaling_group" "asg-prod" {
  name = "ASG_for_Imagility"

  //  availability_zones  = ["us-east-1a"]
  desired_capacity    = 2
  max_size            = 5
  min_size            = 2
  vpc_zone_identifier = ["${aws_subnet.subnet-prod-tf.id}"]

  launch_template {
    id      = "${aws_launch_template.lt-prod-tf.id}"
    version = "$Latest"
  }
}

resource "aws_sqs_queue" "input-image-queue-tf" {
  name                      = "input-image-queue-tf"
  receive_wait_time_seconds = 10

  tags = {
    Environment = "production"
  }
}

resource "aws_s3_bucket" "input-image-bucket" {
  bucket = "inputimagesyoukea"

  tags = {
    Name        = "Input image bucket"
    Environment = "production"
  }
}

resource "aws_s3_bucket_public_access_block" "input-image-s3-bucket" {
  bucket = "${aws_s3_bucket.input-image-bucket.id}"

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_s3_bucket" "processed-image-bucket" {
  bucket = "processed-image-bucket"

  tags = {
    Name        = "Processed image bucket"
    Environment = "production"
  }
}

resource "aws_s3_bucket_public_access_block" "processed-image-s3-bucket" {
  bucket = "${aws_s3_bucket.processed-image-bucket.id}"

  block_public_acls   = true
  block_public_policy = true
}

resource "aws_dynamodb_table" "dynamodb-table" {
  name           = "image_email_mapper"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "file_name"

  attribute {
    name = "file_name"
    type = "S"
  }

  tags = {
    Name        = "image_email_mapper"
    Environment = "production"
  }
}