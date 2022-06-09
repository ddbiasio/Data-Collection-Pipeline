# Data-Collection-Pipeline
In this lab, you'll implement an industry grade data collection pipeline that runs scalably in the cloud.

For this project I will use the BBC Good Food website to scrape recipe details
At the basic level a simple key word search can be initiated to return pages of recipe cards
The recipe card provides a link to the recipe page where ingredients, method, nutritional info and other details can be obtained.

The web scraping will be implemented with Selenium as that offers the greatest functionality to deal with a variety of web site implementations.

## Release 1
In this release I started with a basic Scraper class and added methods for initialising the driver, accepting cookies, executing a search and getting lis of URLs from the search results.

--Added a Scraper class with basic methods to initiate a driver, execute a search, navigate through pages and scrape data using Selenium methods find_element and find_elements
--Added a method to accept cookies
--Executes the scraper class in the block if __name__ == "__main__"
--Added a class to represent the recipe data structure, which is exported to json using the __dict__attribute

## Release 2
In this release I extended the Scraper class to implemment the methods for actaully scraping the data from each page in the list of URLs previously obtained.  A unique ID is obtained for each page scraped (in this case from the last portion of the URL), and page details are written to a json file
--Added methods to create a unique ID (from the URL) and a UUID
--Added to main the calls to loop get the recipe URLs and loop through these to extract page data, adding each page dictionary to then be written to individual files
--Added custom JSONDecoder for the cls parameter to provide a serializable version of the UUID
--Added method to download and save an image or images from the URL being scraped
--Modified Scraper class to accept parameters for the locator details (instead of hard-coded values)
--Added Locator class to allow the values to be defined for the find_element(s) By and Value arguments
--Added methods to get data from a single element, a list of elements (returning a single set of values) or a table type structure of elements returning values in a key: value dictionary type format
--Modified the RecipeScraper class to make the calls to the Scraper class to populate the recipe dictionary

## Release 3
In this release I configured a series of pytest unit test scripts and verified the Scraper class methods using a different web site (www.propertypal.com).

--Added unit tests (using pytest) to verify the public methods of the Scraper class
--Added __init__.py to all the folders to allow imports to work
--Created a recipe_constants.py file to hold all the necessary locator details and other values used for scraping recipe data
--Modified the recipe locator values to provide a more detailed XPATH to avoid having to find the parent element first (greatly speeding up operations)
--Modified the relevant methods to use the detailed XPATH formats, without an initial find_element call to get the parent container
--Modified the Scraper class to accept a dictionary which represent the recipe page data, with keys representing the individual data items, and values comtaining structures of Locators to provide details on the elements where data will be scraped from:
    - value is a Locator object: return text from this element
    - value is a single element list object containing a Locator: find all elements for this locator and return their text as a a list
    - value is a dictionary with three items: list_loc, key_loc, value_loc (all Locator objects): find all elements for the list locator, and then within each element find the key / value from the text of the relevant element and return as a dictionary

## Release 4
In this release I added functionality to allow the data to be stored scalably using Amazon Web Services, with data and inage files being saved directly to S3, and with data then being inserted to a database.  The main recipe information is the parent table, with child tables for the 1:M relationships (ingredients, method, planning info and nutritional info).

--Added classes for file operations locally and S3 (FileStorage and S3Storage)
--FileStorage creates the necessary folders and has methods to write json files, read json files and get a list of files
--S3Storage creates a bucket (if not there already), and has methods to write json files, read json files and get a list of files
--Added config.py to create a config.ini, and using confifparser to get AWS settings
--Added a class for database operations (DBStorage) which takes a connection on initialisation, initiates the engine object and has methods to normalise json data into Panda dataframes and insert the data into parent and child tables
--Added config values for local and RDS databases to be passed to DBStorage
--Added two scripts (dcp_local.py and dcp_aws.py) for running the pipeline either with local storage or AWS storage

## Release 5
In this release I restructured and refactored the code, to create a package of classes which provide the pipeline functionality, and then separately the implementation of the actual pipeline using these classes.  The end point of this release was to ensure the pipeline would run for a large amount of pages so I implemented an option to scraoe until there are no search results left.  During this operation I realised the current implementation of reading ALL the results URLS into a list before processing was causing performance issues, propbably due the large memory requirements of maintaining a very large list. I changed the pipeline to process one page of search results at a time, scraping the data for each link on this one page, saving the files and images for these pages, and uploading to the database, and then restarting the process with the next page of search results.  I also realised that the free tier S3 has a limit on requests, which I quickyl reached once scraping continuously, so changed the approach from writing individual json files, to writing one json file per page of search results.

--Refactoring of code:
    --Added an abstract class Storage, and made FileStorage and S3Storage implement this
     --The use of the abstract storage class allows the pipeline to be defined generically for both local and AWS usage.  When the main pipeline function is called, the DBStorage object is initialisied with either the local or RDS connection string, and a concrete Storage object is passed in
    --Added a pipeline script which extracts much of the functionality from the dcp_local.py and dcp_aws.py, and which accepts the search / page numbers parameters, along with a Storage and DBStorage object and performs all the necessary tasks to scrape data
    --Modified dcp_local.py and dcp_aws.py to instantiate the relevant Storage and DBStorage class and make the call to run_pipeline function
--Restructured the folders to create a package folder with all the classes, created a package using setup.py and modified all imports accordingly in source and test
--Added a method to check if an item ID exists in the database to prevent rescraping

## Release 6
From the previous activities, I realised that the free tier S3 has a limit on requests, which I quickly reached once scraping continuously, so changed the approach from writing individual json files, to writing one json file per page of search results.
--Added tests for FileStorage and S3Storage
--Created a Docker image, and built it with all the relevant components and packages installed (using a requirements.text generated from pip freeze) 
        docker build -f DockerFile -t scraper:latest .
--Defined the entrypoint for the container to be the script to run the AWS pipeline
--Modified the AWS pipleine script to accept command line parameters for search / number of pages so these could then be passed into the container in the docker run command

    e.g docker run --name scraper_local -it scraper --search=carbonara --pages=1

--Added logging to the project so that when running 'blind' in the docker information can be obtained later in the event of any issues with the pipeline
    -- Created a function decorator which wraps any function and logs:
        -- debug info deatiling the function called and its arguments
        -- exception info when the function raises an exception
    -- Created a class decorator which allows the log decorator to be applied to all the methods in a class (without haiving to individually decoprate each function)
    --Logger objects are created for each class e.g. package.scraper.scraper so that the source of messages and errors can be easily identified
    --Decoated all the classes
    Decorated functions in the pipeline to log the completion (or not) of each task in the pipeline
--Pushed the docker image to DockerHub, and then pulled it down to an EC2 instance and ran successfully on the EC2 instance

# Project Folder Structure

dcpipline
    source
        package
            scraper
                scraper.py
            storage
                db_storage.py
                file_storage.py
                s3_storage.py
            utils
                logger.py
                utilities.py
        config.ini
        config.py
        dcp_aws.py
        dcp_local.py
        pipeline.py
        recipe_constants.py
        recipe_scraper.py
        test
            test_scraper.py
            test_file_storage.py
            test_s3_storage.py
    DockerFile
    setup.py
