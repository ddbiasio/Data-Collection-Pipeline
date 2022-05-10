import boto3
import configparser
import requests
from utilities import UUIDEncoder
import json
import uuid

class S3Storage:
    """
    Manages storage of files on an S3 instance

    """

    def __init__(self, 
            access_key_id: str, 
            secret_access_key: str,
            region: str,
            user: str,
            bucket: str):

        self.__client = boto3.client(
            's3',
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key,
            region_name = region
            )
        self.__access_key_id = access_key_id
        self.__secret_access_key = secret_access_key
        self.__region = region
        self.__user = user

        bucket_name, bucketresponse = (
                self.create_bucket(bucket))
        self.bucket_name = bucket_name

    def save_image(self,
            url: str,
            folder: str,
            file: str):

        # Download the file from `url` and save it to s3 under `file_name`:
        r = requests.get(url, stream=True)
        #Key will the the folder/filename
        key = f"{folder}/{file}" 
        self.__client.upload_fileobj(r.raw, self.bucket_name, key)

    def dict_to_json_file(self,
            dict_to_save: dict,
            folder: str,
            file: str):

        self.__client.put_object(
            Body=json.dumps(
                dict_to_save, 
                cls=UUIDEncoder, 
                indent=4),
            Bucket=self.bucket_name,
            Key=f"{folder}/{file}.json")

    def create_bucket_name(self, 
            bucket_prefix):
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, 
            bucket_prefix: str):
       
        for bucket_dict in self.__client.list_buckets().get('Buckets'):
            if bucket_prefix in bucket_dict['Name']:
                return bucket_dict['Name'], True
        
        bucket_name = self.create_bucket_name(bucket_prefix)

        bucket_response = self.__client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
            'LocationConstraint': self.__region})
        
        if bucket_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            # Bucket created
            return bucket_name, True
        else:
            return None, False