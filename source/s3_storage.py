import boto3
import configparser
import requests
from utilities import UUIDEncoder
import json

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
        self.bucket_name = bucket

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

    def create_bucket(self,
            bucket: str):

        bucket_owner = self.user

        response = self.__client.head_bucket(
            Bucket=bucket,
            ExpectedBucketOwner=bucket_owner)

        if not response == 200:
            bucket = self.__client.create_bucket(
                Bucket=bucket, 
                CreateBucketConfiguration=
                    {'LocationConstraint': self.region})
