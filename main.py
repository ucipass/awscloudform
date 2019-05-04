import logging
import boto3
import sys
from botocore.exceptions import ClientError

region_name = 'us-east-2'
bucket_name = "aa-cloudform"
file_name = "test.yaml"

session = boto3.session.Session(aws_access_key_id=None, aws_secret_access_key=None,
                                aws_session_token=None, region_name=region_name, botocore_session=None,
                                profile_name='default')

s3 = session.client('s3')

def create_bucket(bucket_name):
    global aws_access_key_id
    global aws_secret_access_key
    global region_name

    try:
        s3.create_bucket(
            Bucket=bucket_name ,
            CreateBucketConfiguration={'LocationConstraint': region_name}
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def is_bucket(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        return False
    return True


if is_bucket(bucket_name):
    print(bucket_name, "bucket exists!")
else:
    if create_bucket(bucket_name):
        print(bucket_name, " bucket created!")
    else:
        sys.exit(1)
try:
    s3.upload_file(file_name, bucket_name, file_name)
except ClientError as e:
    logging.error(e)
    sys.exit(1)

