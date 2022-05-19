import boto3
import configparser
import requests
from .utilities import UUIDEncoder
import json
import uuid

class S3Storage:
    """
    Manages storage of files on an S3 instance

    Attributes
    ----------
    bucket_name: str
        The name
    """

    def __init__(self, 
            access_key_id: str, 
            secret_access_key: str,
            region: str,
            user: str,
            bucket: str):

        self.__s3resource = boto3.resource(
            's3',
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key,
            region_name = region
            )
        self.__access_key_id = access_key_id
        self.__secret_access_key = secret_access_key
        self.__region = region
        self.__user = user

        self.__s3bucket = self.create_bucket(bucket)
        self.__bucket_name = self.__s3bucket.name

    def save_image(self,
            url: str,
            folder: str,
            file: str):

        # Download the file from `url` and save it to s3 under `file_name`:
        r = requests.get(url, stream=True)
        #Key will the the folder/filename
        key = f"{folder}/{file}" 
        self.__s3bucket.upload_fileobj(r.raw, key)

    def dict_to_json_file(self,
            dict_to_save: dict,
            folder: str,
            file: str):

        self.__s3bucket.put_object(
            Body=json.dumps(
                dict_to_save, 
                cls=UUIDEncoder, 
                indent=4),
            Bucket=self.__bucket_name,
            Key=f"{folder}/{file}.json")

    def create_bucket_name(self, 
            bucket_prefix):
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, 
            bucket_prefix: str):
       
        for bucket in self.__s3resource.buckets.all():
            if bucket_prefix in bucket.name:
                return bucket
        
        bucket_name = self.create_bucket_name(bucket_prefix)

        bucket = self.__s3resource.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
            'LocationConstraint': self.__region})
        
        bucket_policy_json = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "GetPutObjects",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        })
        bucket_policy = self.__s3resource.BucketPolicy(bucket_name)
        bucket_policy.put(Policy=bucket_policy_json)
        return bucket

    def list_files(self,
            folder: str,
            file_type: str = None) -> list:

        files = []

        for object_summary in self.__s3bucket.objects.filter(Prefix=f"{folder}/"):
            if file_type is None or object_summary.key.endswith(file_type) :
                files.append(object_summary.key)

        return files

    def read_json_file(self,
            file: str):
        content_object = self.__s3bucket.Object(file)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        return json.loads(file_content)