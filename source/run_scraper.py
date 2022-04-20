from recipe import RecipeScraper
from utilities import file_ops

# A list of search terms that can be iterated through
# for multiple scraping variations

searches = ["chicken"]

file_ops.create_folder("./raw_data")

rs = RecipeScraper()

for search in searches:
    # Data folder ./raw_data/search_term (replace spaces with underscore)
    data_folder = f"./raw_data/{search.replace(' ', '_')}"
    # Images folder ./raw_data/search_term/images
    images_folder = f"{data_folder}/images"
    file_ops.create_folder(data_folder)
    file_ops.create_folder(images_folder)
    rs.get_recipe_data(search.replace(' ', '+'), 2, data_folder, images_folder)




