from recipe import RecipeScraper
from utilities import file_ops

# A list of search terms that can be iterated through
# for multiple scraping variations

searches = ["chickens"]

file_ops.create_folder("./raw_data")

rs = RecipeScraper()

for search in searches:
    try:
        rs.get_recipe_data(search.replace(' ', '+'), 1)
    except RuntimeError as exc:
        print(f"Unable to retrieve data for {search}: {str(exc)}")