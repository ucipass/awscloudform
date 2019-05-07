import logging
import boto3
import sys
from os import path
from time import sleep
from botocore.exceptions import ClientError
from botocore.exceptions import ValidationError

# stack_name = "aa-vpc1"
#file_name = "aa-vpc1.yaml"
files = ["root.yaml", "aa-vpc1.yaml", "aa-vpc2.yaml", "aa-ec2-1.yaml", "aa-vpcpeering.yaml"]
bucket_name = "aa-cloudforms"
region_name = 'us-west-1'
key_name = "AA-TEST"



session = boto3.session.Session(aws_access_key_id=None, aws_secret_access_key=None,
                                aws_session_token=None, region_name=region_name, botocore_session=None,
                                profile_name='default')
s3 = session.client('s3')
cf_client = session.client('cloudformation')

def create_bucket(bucket_name):
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

def create_s3key(bucket_name,file_name):
    try:
        s3.upload_file(file_name, bucket_name, file_name)
        print(file_name,"uploaded to",bucket_name,"s3 bucket")
    except ClientError as e:
        logging.error(e)
        sys.exit(1)
        return False
    return True

def is_bucket(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        return False
    return True

def show_stack_events(stack_name):
    last_index = 0
    try:
        response = cf_client.describe_stack_events(StackName=stack_name)
        stack_events = response['StackEvents']
        last_index = len(stack_events)
        stack = session.resource('cloudformation').Stack(stack_name)
        status = stack.stack_status
        print(stack_name,status)
        # status = stack_events[0]['ResourceStatus']
        while "PROGRESS" in status:
            sleep(5)
            response = cf_client.describe_stack_events(StackName=stack_name)
            stack_events = response['StackEvents']
            current_index = len(stack_events)
            stack = session.resource('cloudformation').Stack(stack_name)
            status = stack.stack_status
            while last_index <= current_index:
                print( stack_events[current_index-last_index]['EventId'] )
                last_index +=1
    except ClientError as e:
        if e.response['Error']['Code'] != 'ValidationError':
            logging.error(e)
            sys.exit(1)
        else:
            print(stack_name,"stack does not exists!")

def create_stack(bucket_name, file_name, stack_name):
    template_name = "https://s3.amazonaws.com/" + bucket_name + "/" + file_name
    show_stack_events(stack_name)
    try:
        response = cf_client.create_stack(StackName=stack_name, TemplateURL=template_name)
        print(stack_name,"created with template",template_name)
    except ClientError as e:
        logging.error(e)
        sys.exit(1)
    show_stack_events(stack_name)

def update_stack(bucket_name, file_name, stack_name):
    template_name = "https://s3.amazonaws.com/" + bucket_name + "/" + file_name
    show_stack_events(stack_name)
    try:
        response = cf_client.update_stack(StackName=stack_name, TemplateURL=template_name)
        print(stack_name,"updated with template",template_name)
    except ClientError as e:
        logging.error(e)
        sys.exit(1)
    show_stack_events(stack_name)

def delete_stack(stack_name):
    show_stack_events(stack_name)
    try:
        response = cf_client.delete_stack(StackName=stack_name)
        print(stack_name,"stack deletes")
    except ClientError as e:
        logging.error(e)
        sys.exit(1)
    show_stack_events(stack_name)

create_bucket(bucket_name)
for file_name in files:
    create_s3key(bucket_name,file_name)
create_stack(bucket_name, "root.yaml", "root" )
#update_stack(bucket_name, "root.yaml", "root" )
