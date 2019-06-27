import os
from flask import Flask, flash, request, redirect, url_for
import boto3

UPLOAD_FOLDER = '/Users/akshayambekar/Documents/Imagility/Uploaded'
RAW_INPUT_IMAGES_S3_BUCKET_NAME = 'inputimagesyoukea'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
DYNAMODB_TABLE_NAME_FOR_STATUS_KEEPING = 'image_email_mapper'
SQS_QUEUE_NAME = 'input_image_queue'
AWS_ACCOUNT_ID = '<YOUR_ACCOUNT_ID_HERE>'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'SOME_APP_SECRET_KEY'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("file[]")
        emailid = request.form["email"]
        if files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)
        for file in files:
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

                writeImageToS3(file)

                response = putItemInDynamoDb(file, emailid)
                print(response)

                response = sendMsgToSQS(file)
                print("Response from SQS : "+response)

        return redirect(url_for('successful_file_upload'))
    return '''
    <!doctype html>
    <div style="background-image:url(https://originalmotto.us/wp-content/uploads/2015/09/parchment-background.jpg)">
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file[] multiple>
      Email: <input type=email name=email>
      <input type=submit value=Upload>
    </form>
    </div>
    '''

def writeImageToS3(file):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), RAW_INPUT_IMAGES_S3_BUCKET_NAME, file.filename)

@app.route('/successful_file_upload')
def successful_file_upload():
    return '''
    <!doctype html>
    <title>File Uploaded Successfully</title>
    <h1>Your files have been uploaded successfully!</h1>
    <h3>You will receive an email from devops.youkea@gmail.com with 
    instructions on how to download your processed file!
    </h3>
    '''

def convertImageToByteArray(file):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), "rb") as image:
        f = image.read()
        b = bytearray(f)
    return b

# def convertByteArrayToImage(b):
#
#     recontructedImage = open(os.path.join(app.config['UPLOAD_FOLDER'], 'rec/', file.filename), 'wb')
#     recontructedImage.write(bytearray(b))
#     recontructedImage.close()
#     return recontructedImage

def putItemInDynamoDb(file, emailid):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE_NAME_FOR_STATUS_KEEPING)

    response = table.put_item(
        Item={
            'file_name': file.filename,
            'email_id': emailid,
            'status': 'processing',
        }
    )
    return response

@app.route('/getmessagefromsqs')
def getMsgFromSQS():
    sqs = boto3.client('sqs')

    queue_url = sqs.get_queue_url(
        QueueName=SQS_QUEUE_NAME,
        QueueOwnerAWSAccountId=''
    ).get('QueueUrl')

    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'All',
        ],
        MessageAttributeNames=[
            'All',
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=0,
        WaitTimeSeconds=0,
    )

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    print("RESPONSE FROM SQS >>>>>>>>>")
    print(response)

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)

    return '''
        <!doctype html>
        <title>Message Received And Deleted From Queue Successfully</title>
        <h1>Your message has been received and deleted successfully!</h1>
        '''

def sendMsgToSQS(file):
    sqs = boto3.client('sqs')

    queue_url = sqs.get_queue_url(
        QueueName='input_image_queue',
        QueueOwnerAWSAccountId=AWS_ACCOUNT_ID
    ).get('QueueUrl')

    b = convertImageToByteArray(file)

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'File': {
                'DataType': 'Binary',
                'BinaryValue': b
            },
            'FileName': {
                'DataType': 'String',
                'StringValue': file.filename
            }
        },
        MessageBody=(
            'Input raw image name: '+file.filename+' sent for conversion to 3D'
        )
    )

    return response['MessageId']


if __name__ == '__main__':
    app.run(debug=True)
