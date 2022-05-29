import boto3
import configparser
import requests
from .utilities import UUIDEncoder
import json
import uuid
from boto3_type_annotations.s3 import ServiceResource, Bucket
class S3Storage:

    def __init__(self, 
            access_key_id: str, 
            secret_access_key: str,
            region: str,
            bucket_prefix: str,
            data_folder: str,
            images_folder: str):
        """Creates an instance of the S3Storage class

        Parameters
        ----------
        access_key_id : str
            AWS Access Key ID
        secret_access_key : str
            AWS Secret Access Key
        region : str
            AWS region
        data_folder : str
            Name of the data folder to create on initialisation
        images_folder : str
            Name of the image folder to create on initialisation
        """
        self.__s3resource = boto3.resource(
            's3',
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key,
            region_name = region
            )

        self.__region = region
        self.__s3bucket = None
        self.__bucket_name = None
        self.data_folder = data_folder
        self.images_folder = images_folder
        self.__create_bucket(bucket_prefix)

    def save_image(self,
            url: str,
            folder: str,
            file: str):
        """Retrieves image from a URL and saves to S3 bucket

        Parameters
        ----------
        url : str
            The URL of the imahe
        folder : str
            The name of the 'folder' to store the image in
        file : str
            The name of the image file
        """
        # Download the file from `url` and save it to s3 under `file_name`:
        r = requests.get(url, stream=True)
        #Key will the the folder/filename
        key = f"{folder}/{file}" 
        self.__s3bucket.upload_fileobj(r.raw, key)

    def save_json_file(self,
            dict_to_save: dict,
            folder: str,
            file: str):
        """Creates a file in JSON format from a dictionary and saves to the S3 bucket

        Parameters
        ----------
        dict_to_save : dict
            The dictionary object to be written to file
        folder : str
            The name of the folder to save to
        file : str
            The name of the JSON file to be created
        """            
        self.__s3bucket.put_object(
            Body=json.dumps(
                dict_to_save, 
                cls=UUIDEncoder, 
                indent=4),
            Bucket=self.__bucket_name,
            Key=f"{folder}/{file}.json")

    def __create_bucket_name(self, 
            bucket_prefix: str) -> str:
        """Creates a unique S3 bucket name

        Parameters
        ----------
        bucket_prefix : str
            Prefix for the bucket name

        Returns
        -------
        str
            bucket name as prefix + UUID
        """            
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def __create_bucket(self, 
            bucket_prefix: str):
        """Creates an S3 bucket

        Parameters
        ----------
        bucket_prefix : str
            Prefix for the bucket name

        Returns
        -------
        Bucket
           Bucket: S3 Bucket
        """            
        for bucket in self.__s3resource.buckets.all():
            if bucket_prefix in bucket.name:
                self.__s3bucket = bucket
        
        bucket_name = self.__create_bucket_name(bucket_prefix)

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
        self.__s3bucket = bucket
        self.__bucket_name = bucket_name

    def list_files(self,
            folder: str,
            file_type: str = None) -> list:
        """Lists files in an S3 bucket folder (filtered optionally by file type)

        Parameters
        ----------
        folder : str
            Name of the folder
        file_type : str, optional
            A valid file type extension, by default None

        Returns
        -------
        list
            List of file names (keys)
        """            
        files = []

        for object_summary in self.__s3bucket.objects.filter(Prefix=f"{folder}/"):
            if file_type is None or object_summary.key.endswith(file_type) :
                files.append(object_summary.key)

        return files

    def read_json_file(self,
            file: str) -> str:
        """Reads a json file and returns as string in json format

        Parameters
        ----------
        file : str
            The key of the json file

        Returns
        -------
        str
            A string in json format
        """            
        content_object = self.__s3bucket.Object(file)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        return json.loads(file_content)