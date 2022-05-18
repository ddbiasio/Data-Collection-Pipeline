import configparser
from recipe_scraper import RecipeScraper
from s3_storage import S3Storage
import boto3

def init_storage(bucket: str):
    # Get the aws settings from config file
    config = configparser.ConfigParser()
    config.read_file(open('./source/config.ini'))
    aws_access_key = config.get('S3Storage', 'accesskeyid')
    aws_secret_key = config.get('S3Storage', 'secretaccesskey') 
    aws_user = config.get('S3Storage', 'iamuser') 
    aws_region = config.get('S3Storage', 'region') 
    
    return S3Storage(
            aws_access_key,
            aws_secret_key,
            aws_region,
            aws_user,
            bucket)

def save_file(s3storage: S3Storage,
        page_dict: dict,
        folder: str):

        s3storage.dict_to_json_file(
            page_dict,
            folder,
            f"{page_dict['item_id']}"
            )

def save_images(s3storage: S3Storage,
        page_dict: dict,
        folder: str):

    for url in page_dict["image_urls"]:
        # Get the file extension from the url
        file_ext = url.rsplit('/', 1)[-1].rsplit('.', 1)[-1]
        s3storage.save_image(
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
            s3 = init_storage("raw-data")
            for idx, page_dict in enumerate(rs.page_data):
                folder_name = search.replace(' ', '-')
                save_file(s3, page_dict, search)
                save_images(s3, page_dict, f"{search}/images")