import base64
import boto3
import json

ONE_DAY = (24 * 60 * 60)
ONE_WEEK = 7 * ONE_DAY
MAX_AGE_SECONDS = 2 * ONE_DAY


def record_temperature(message):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pi_temperature')
        # print(message)
        # calculate the dynamo expiration
        expires_seconds = int(message["timestamp"]) + MAX_AGE_SECONDS
        # json dynamo document
        item = {
            "name": str(message["name"]),
            "celsius": int(message["celsius"]),
            "fahrenheit": int(message["fahrenheit"]),
            "timestamp": int(message["timestamp"]),
            "expires": int(expires_seconds),
            "category": message["category"]
        }
        if "humidity" in message:
            item["humidity"] = int(message["humidity"])
        # print(item)
        # store it
        table.put_item(Item=item)
        print("saved to DynamoDB")
    except Exception as e:
        print(e)


def garage_temp_cloudwatch(message):
    try:
        # cloudwatch
        cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        cloudwatch.put_metric_data(
            Namespace='Wygant Garage', MetricData=[
                {
                    'MetricName': 'fahrenheit', 'Timestamp': int(
                        message["timestamp"]), 'Value': int(
                        message["fahrenheit"]), 'Unit': 'Count'}, {
                    'MetricName': 'celsius', 'Timestamp': int(
                        message["timestamp"]), 'Value': int(
                        message["celsius"]), 'Unit': 'Count'}])
        print("saved to CloudWatch")
    except Exception as e:
        print(e)


def office_temp_cloudwatch(message):
    try:
        # cloudwatch
        cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        cloudwatch.put_metric_data(Namespace='Home Office',
                                   MetricData=[
                                       {
                                           'MetricName': 'fahrenheit',
                                           'Timestamp': int(message["timestamp"]),
                                           'Value': int(message["fahrenheit"]),
                                           'Unit': 'Count'
                                       },
                                       {
                                           'MetricName': 'celsius',
                                           'Timestamp': int(message["timestamp"]),
                                           'Value': int(message["celsius"]),
                                           'Unit': 'Count'
                                       },
                                       {
                                           'MetricName': 'humidity',
                                           'Timestamp': int(message["timestamp"]),
                                           'Value': int(message["humidity"]),
                                           'Unit': 'Percent'
                                       }
                                   ]
                                   )
        print("saved to CloudWatch")
    except Exception as e:
        print(e)


def washer_vibration_cloudwatch(message):
    try:
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.put_metric_data(
            Namespace='Wygant Washer', MetricData=[
                {
                    'MetricName': 'MotionDetected', 'Timestamp': int(
                        message["timestamp"]), 'Value': int(
                        message["motion_detected"]), 'Unit': 'Count', }])
        print("saved to CloudWatch")
    except Exception as e:
        print(e)


def lambda_handler(event, context):
    print(json.dumps(event))
    for record in event["Records"]:
        # decode the json message
        message = json.loads(record["body"])
        # determine how to handle the record
        if message["category"] == "temperature":
            record_temperature(message)
            if message["name"] == "garage":
                garage_temp_cloudwatch(message)
            elif message["name"] == "office":
                office_temp_cloudwatch(message)
            else:
                print("not saved")
        elif message["category"] == "vibration":
            washer_vibration_cloudwatch(message)
        else:
            print("not saved")
    return True
