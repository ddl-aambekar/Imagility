var aws = require('aws-sdk');
var ses = new aws.SES();
var dynamoDb = new aws.DynamoDB.DocumentClient();
const TABLE_NAME = 'image_email_mapper';
const s3 = new aws.S3();
var toEmail;

exports.handler = function(event, context, callback) {
    console.log("Incoming: ", event);

    const myBucket = 'processedimagesyoukea';
    const myKey = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
    var keyForDynamoDb;

    if(myKey.includes(".binvox")) {
        keyForDynamoDb = myKey.substring(0, myKey.length-7);
    }
    else if(myKey.includes(".npy")) {
        keyForDynamoDb = myKey.substring(0, myKey.length-4);
    } else {
        keyForDynamoDb = myKey;
    }

    var updateParams = {
        TableName:TABLE_NAME,
        Key: {
          file_name : keyForDynamoDb,
        },
        UpdateExpression: "set file_status = :p",
        ExpressionAttributeValues: {
            ":p": "processed"
        }
    };

    console.log("Updating the item...");
    dynamoDb.update(updateParams, function(err, data) {
        if (err) {
            console.error("Unable to update item. Error JSON:", JSON.stringify(err, null, 2));
        } else {
            console.log("UpdateItem succeeded:", JSON.stringify(data, null, 2));
        }
    });

    console.log('Key to search in DynamoDB: '+keyForDynamoDb);
    const params = {
    TableName: TABLE_NAME,
    Key: {
      file_name : keyForDynamoDb,
        },
    };

    var getObjectPromise =

    dynamoDb.get(params, (error, result) => {
        if (error) {
            console.log("Error", error);
        } else {
        console.log("Success in fetching details from DynamoDB : ", result.Item);
        toEmail = result.Item.email_id;
        }
    }).promise();

    getObjectPromise.then (function(data) {
    const signedUrlExpireSeconds = 60 * 60;
    const url = s3.getSignedUrl('getObject', {
        Bucket: myBucket,
        Key: myKey,
        Expires: signedUrlExpireSeconds,
    });

    console.log("===SIGNED URL IS===");
    console.log(url);

    var eParams = {
        Destination: {
            ToAddresses: [toEmail]
        },
        Message: {
            Body: {
                Text: {
                    Data:   'Hello There! Thanks for submitting a request to process 2D Images.'+
                            ' Your files are now ready for download.'+
                            ' Please use the below link/s to download them. Thank you!' +
                            '\n\nLink : '+url
                }
            },
            Subject: {
                Data: 'Your files are ready!'
            }
        },
        Source: "devops.youkea@gmail.com"
    };
    console.log('===SENDING EMAIL===');
    var email = ses.sendEmail(eParams, function(err, data) {
        if (err) console.log(err);
        else {
            console.log("===EMAIL SENT===");
            // console.log(data);
            console.log('EMAIL: ', email);
            context.succeed(event);
        }
    });
})};