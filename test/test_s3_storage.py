from logging import root
from source.package.storage.s3_storage import S3Storage
import pytest
import os
import configparser
import botocore

@pytest.fixture(scope="module")
def root_folder() -> str:
    return "test-s3"

@pytest.fixture(scope="module")
def data_folder(root_folder: str) -> str:
    return f"test-data"

@pytest.fixture(scope="module")
def images_folder(data_folder: str) -> str:
    return f"images"

@pytest.fixture(scope="module")
def test_s3(root_folder: str, data_folder: str, images_folder: str) -> S3Storage:
    # Get the aws settings from config file
    config = configparser.ConfigParser()
    config.read_file(open('../source/config.ini'))
    aws_access_key = config.get('S3Storage', 'accesskeyid')
    aws_secret_key = config.get('S3Storage', 'secretaccesskey') 
    aws_region = config.get('S3Storage', 'region') 
    s3 = S3Storage(aws_access_key, aws_secret_key, aws_region, root_folder, data_folder, images_folder)
    yield s3

def test_constructor(test_s3: S3Storage,
        root_folder: str):
    # Will be initislaied in the fixture
    # Check bucket created
    bucket_exists = False
    for bucket in test_s3._S3Storage__s3resource.buckets.all():
        if root_folder in bucket.name:
            bucket_exists = True
            break
    assert bucket_exists

def test_save_json_file(test_s3: S3Storage,
        data_folder: str):
    
    dict_to_save = {"key1": "value1",
        "key2": ["value2", "value3"],
        "key3": {"subkey1": 1, "subkey2": 2}}

    test_s3.save_json_file(
        dict_to_save,
        data_folder,
        "test_file1")
    try:
        test_s3._S3Storage__s3resource.Object(
            test_s3._S3Storage__bucket_name, f"{data_folder}/test_file1.json").load()
    except botocore.exceptions.ClientError as e:
        file_saved = False
    else:
        file_saved = True
    assert file_saved

def test_save_image(test_s3: S3Storage,
        images_folder: str):
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Grosser_Panda.JPG/330px-Grosser_Panda.JPG"
    test_s3.save_image(url, images_folder, "panda.jpg")
    try:
        test_s3._S3Storage__s3resource.Object(test_s3._S3Storage__bucket_name, f"{images_folder}/panda.jpg").load()
    except botocore.exceptions.ClientError as e:
        file_saved = False
    else:
        file_saved = True
    assert file_saved

def test_list_files(test_s3: S3Storage,
        data_folder: str):
    dicts = [
        {"key4": "value4",
        "key5": ["value5", "value6"],
        "key7": {"subkey3": 3, "subkey4": 4}},
        {"key8": "value8",
        "key9": ["value9", "value10"],
        "key10": {"subkey5": 5, "subkey6": 6}}]

    for idx, d in enumerate(dicts):
        test_s3.save_json_file(
            d,
            data_folder,
            f"test_file{idx + 2}")
    expected_files = [
                f"{data_folder}/test_file1.json", 
                f"{data_folder}/test_file2.json", 
                f"{data_folder}/test_file3.json"
                ]
    files = test_s3.list_files(data_folder)
    assert sorted(expected_files) == sorted(files) and len(files) == 3

def test_read_json_file(test_s3: S3Storage,
        data_folder: str):
    file = test_s3.read_json_file(f"{data_folder}/test_file1.json")
    assert file
