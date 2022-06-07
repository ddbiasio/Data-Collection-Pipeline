# Data-Collection-Pipeline
In this lab, you'll implement an industry grade data collection pipeline that runs scalably in the cloud.
# Milestone 1
For this project I will use the BBC Good Food website to scrape recipe details
At the basic level a simple key word search can be initiated to return pages of recipe cards
The recipe card provides a link to the recipe page where ingredients, method, nutritional info and other details can be obtained.

# Milestone 2
The web scraping will be implemented with Selenium as that seems to offer more features for interacting with the web site should I need this.
## Task 1
Created an empty scraper class with some basic properties and method stubs
## Task 2
Started filling out the main get_data method which will execute the search, loop through pages and recipe cards to scrape recipe date
The first step is to load the home page, then run a search
Create the methods for loading a recipe search, navigating to a page within the search results and nabigating to a particular URL i.e. a recipe page
The search is executed by adding a key word with a query string
## Task 3
Created a method to accept cookies once the home page is loaded.
## Task 4 
Created a method to loop through pages of search results and gather the links to each recipe
I have limited this to 2 pages for the time being to ensure I am not spending a lot of time waiting for results
## Task 5
Added a call to get_data in the __init__ method.  The initialiser accepts the search string as input which is the passed to the search method to retrieve recipes based on a key word(s).
Added if __name__ == "__main__" block to the code which creates an an instance of the class and returns the links to recipes from the first 2 pages of the search

# Milestone 3
Created a class for the recipe details to make the collection of details easier to read, and with the intention to use the __dict__ attribute to easily output the recipe to dictionary format
## Tasks 1 and 2
Created a method to return a deterministic IC and a UUID
The last element of the recipe page URL is unique so this this used as the item ID
I used uuid.uuid4() to generate a UUID

## Task 3
Created a method in the main class to extract data from a recipe page as identified by a URL passed to the function
This loads the page and extracts ingredients, method, prep and cook times and nutritional info
The recipe details are held in div (class='post recipe') so I find this element first and then subsequent sections are located relevant to this.  with some sections I noticed the class of items Iwanted to find was used in multiple sections so I would find the enclosing block first to be sure I was then looping through the correct elements for the information I needed to find

## Task 4
I used the __dict__ attribute of my recipe class to create a dictionary for the recipe

## Task 5
In my main program (after loading and searching for recipes) I loop through each page to get the recipe URLs.  Then for each URL I load the recipe page to extract the details.  As each recipe dictionary is created I update a dictionary (all_recipes) with each new recipe.  The final dictionary is them written to data.json in a folder ./raw_data/{search} where {search} is the search string used to find the recipes

I discovered that UUIDs are not serializable so created a custom JSONDecoder for the cls parameter to provide a serializable version of the UUID

## Task 6
Each recipe card has a single image.  When building the recipe dictionary I get the image URL from the recipe details and use urllib.request.urlretrieve to extract the image and save to ./raw_data/{search}/images, naming it with the recipe ID e.g. chicken-pasta-bake.jpg so this can be linked to a recipe at a later stage

# Milestone 4

## Tasks 1 and 2
Amended scraper class to be more generic and accept variables for locator strings
Modified this further based on general assumption that generally would want to return either a single element, or a list of elements, or a single elements text value, or values from a list of elements either in list form, or dictionary format where there are key: value structures
All find_element operations can either be executed from the page level, or within another element on the page. Lists of elements can also be within a further container.
The methods created to get any of these types of object are all generic to allow them to be called with or without a parent element, or to look for list elements in a container, or just from the parent element
I also wanted to make the calls to find_element more generic so as not to have to implement methods for each type of locator.  I created a class locator which has attributes to define the and the locator value.  This is set in the calling function for each of the elements to be found in the method.

This reduced the main set of methods for actually scraping the data to get_element retutns a element or a list of elements, get_item_data (returns text of an element), get_data_as_list (returns text from a list of elements as a list) and get_data_as_dict (returns key: value type data from a list of elements), with an additional method to get the image URL from an <img> element.

I added the functions for calling the scraper methods to the recipe class, so it is instantiatated with a recipe URL and then populates the attributes with the relevant data from the web page.  The object __dict__ is then added to the scraper object list of dictinaries, as is the image URL.

Once all data is scraped, the recipe dictionaries and image dictionaies are iterated through to save each recipe as a json, and to download and save each image.

I also added some exception handling to handle elements not being found, or pages not being loaded.

I have updated all docstrings to reflect the changes made.

## Task 3
Using pytest to create unit tests.  During the task I have further refactored the code. I discovered that I could use a more detailed XPATH to go directly to an element so I now find elements using this instead of travewrsing the page stucture to find elements within divs etc.  Once I implemented this I found the scraper to run much faster sicne it requires less find_element operations to get all the data.

I revisited how I could inform the scraper class of the details I needed to scrape, and so I now pass a dictionary to the class which has as it keys the items to be scraped which will be the keys in the dictionary conatining the page data.  The values are locator details (By and value to pass to the find_element function.

For the data I am collecting I either need a single element's text, or text from a list of elements, or text from list of paired elements.  The page defintion dicitonary will therefore inform the class of the type of data being scraped through the format of the values:
 - value is a Locator object: return text fropm this element
 - value is a single element list object containing a Locator: find all elements for this locator and return their text as a a list
 - value is a dctionary with three items: list_loc, key_locm value_loc (all Lcoator objects): find all elements for the list locator, and then within each element find the key / value from the text of the relevant element and return as a dictionary

I therefore have 3 main methods:
 - get_element
 - get_element_list
 - get_element_dict

I have a method to find all the images relating to the recipe (which assumes all images will have the same locator details), and retruns the URLs for these in a list

The Scraper has a method which will then accept a page defintion (dict) and use this to scrape the page and return the data in dictinary format

I also added a method which will scrape all the pages from a search, write each page to a json file and download and save the images.

I created a utilities module for the JSONDecoder class, and also for some of the basic filer operations such as creating folders, downloading and saving an image.

I have installed mypy and implemented code changes to fix issues identified from that, and continue to do so on an ongoing basis.  I have also ran deepsource against my code and applied fixes for some of the issues, and will keep doing this on an ongoing basis.


# Milestone 5

## Task 1
Created classes for local file storage and S3 bucket storage
FileStorage: creates the root folder (raw_data), data folder and images folder, and methods to save a json string directly to a json file, and retrived images from the URL and save
S3Storage: create a bucket (raw_data appended with UUID, only if there isn't an existing raw_data* bucket), and methods to save json string directly to an S3 object (key = search/recipe_ID), and directly save the image from the URL to an S3 object (key = search/images/image_name.jpeg) (this determines the image type).  The create bucket method also applies a security policy - without this the objects cannot be viewed
Generated a config.ini for AWS setting using configparser (config.py)

## Task 2
Created a class for database operations, which creates the connection to the database (can be local or RDS), normalises the JSON data into panda DataFrames and writes these to specified tables (options to append, replace)
Added methods to the storage classes to get a list of files from a folder or bucket location, read in the JSON data.  This JSON data is then passed to the DBStorage class for upload to the database
Added the setting for local and RDS database connection settings to config.py and re-created config.ini

Created two python scripts dcp_aws.py and dcp_local.py to run the pipeline either locally or to AWS
- Scrape the data and return a list of dictionaries
- Save the dictionaries to JSON files, get the images and save those
- Traverse the folder / bucket location and read in the JSON data
- Normalise the JSON data (recipe details is the parent table, the others are child tables linked by the ID), write to DB

Restructured source code folders:
source
    package
        scraper
            recipe_constants.py
            recipe_scraper.py
            scraper.py
        storage
            db_storage.py
            file_storage.py
            s3_storage.py
            utilities.py
    config.ini
    config.py
    dcp_aws.py
    dcp_local.py
    test
        test_scraper.py

## Task 3
Was completed in Task 1

## Task 4
Before updating



DOCKER BUILD: docker build -f DockerFile -t scraper:latest .

docker run --name scraper_local -it scraper --search=carbonara --pages=1

