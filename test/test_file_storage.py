from logging import root
from source.package.storage.file_storage import FileStorage
import pytest
import os
import shutil

@pytest.fixture(scope="module")
def root_folder() -> str:
    return "./test_fs"

@pytest.fixture(scope="module")
def data_folder(root_folder: str) -> str:
    return f"{root_folder}/test_data"

@pytest.fixture(scope="module")
def images_folder(data_folder: str) -> str:
    return f"{data_folder}/images"

@pytest.fixture(scope="module")
def test_fs(root_folder: str, data_folder: str, images_folder: str) -> FileStorage:
    tf = FileStorage(root_folder, data_folder, images_folder)
    yield tf
    if os.path.exists(root_folder):
        shutil.rmtree(root_folder)


def test_constructor(test_fs: FileStorage,
        root_folder: str,
        data_folder: str,
        images_folder: str):
    # Will be initislaied in the fixture
    # Check folders created
    assert (os.path.exists(root_folder)
        and os.path.exists(data_folder)
        and os.path.exists(images_folder))

def test_save_json_file(test_fs: FileStorage,
        data_folder: str):
    
    dict_to_save = {"key1": "value1",
        "key2": ["value2", "value3"],
        "key3": {"subkey1": 1, "subkey2": 2}}

    test_fs.save_json_file(
        dict_to_save,
        data_folder,
        "test_file1")
    assert os.path.exists(f"{data_folder}/test_file1.json")

def test_save_image(test_fs: FileStorage,
        images_folder: str):
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Grosser_Panda.JPG/330px-Grosser_Panda.JPG"
    test_fs.save_image(url, images_folder, "panda.jpg")
    assert os.path.exists(f"{images_folder}/panda.jpg")

def test_list_files(test_fs: FileStorage,
        data_folder: str):
    dicts = [
        {"key4": "value4",
        "key5": ["value5", "value6"],
        "key7": {"subkey3": 3, "subkey4": 4}},
        {"key8": "value8",
        "key9": ["value9", "value10"],
        "key10": {"subkey5": 5, "subkey6": 6}}]

    for idx, d in enumerate(dicts):
        test_fs.save_json_file(
            d,
            data_folder,
            f"test_file{idx + 2}")
    expected_files = [
                f"{data_folder}/test_file1.json", 
                f"{data_folder}/test_file2.json", 
                f"{data_folder}/test_file3.json"
                ]
    files = test_fs.list_files(data_folder)
    assert sorted(expected_files) == sorted(files) and len(files) == 3

def test_read_json_file(test_fs: FileStorage,
        data_folder: str):
    file = test_fs.read_json_file(f"{data_folder}/test_file1.json")
    assert file
