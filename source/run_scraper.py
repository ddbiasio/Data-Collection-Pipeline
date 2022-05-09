import configparser
from recipe import RecipeScraper
from file_storage import FileStorage
import boto3

def init_storage(root_folder: str):
    return FileStorage(root_folder)

def save_file(fs_client: FileStorage,
        page_dict: dict,
        folder: str):

        fs_client.dict_to_json_file(
            page_dict,
            folder,
            f"{page_dict['item_id']}"
            )

def save_images(fs_client: FileStorage,
        page_dict: dict,
        folder: str):

    for url in page_dict["image_urls"]:
        # Get the file extension from the url
        file_ext = url.rsplit('/', 1)[-1].rsplit('.', 1)[-1]
        fs_client.save_image(
            url,
            folder,
            f"{page_dict['item_id']}.{file_ext}")

if __name__ == "__main__":
    # A list of search terms that can be iterated through
    # for multiple scraping variations
    searches = ["chicken"]

    rs = RecipeScraper()

    for search in searches:
        try:
            rs.get_recipe_data(search.replace(' ', '+'), 1)
        except RuntimeError as exc:
            print(f"Unable to retrieve data for {search}: {str(exc)}")

        # if data has been scraped
        if len(rs.page_data) > 0:
            fs = init_storage("./raw_data")
            # s3.create_bucket("aicore-recipes-raw-data")
            for idx, page_dict in enumerate(rs.page_data):
                # create the folders for data and images
                data_folder = f"{fs.root_folder}/{search.replace(' ', '-')}"
                images_folder = f"{data_folder}/images"
                fs.create_folder(data_folder)
                fs.create_folder(images_folder)
                # save the files in the appropriate folder
                save_file(fs, page_dict, data_folder)
                save_images(fs, page_dict, images_folder)