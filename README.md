# Data-Collection-Pipeline
In this lab, you'll implement an industry grade data collection pipeline that runs scalably in the cloud.
# Milestone 1
For this project I will use the BBC Good Food website to scrape recipe details
At the basic level a simple key word search can be initiated to return pages of recipe cards
The recipe card provides a link to the recipe page where ingredients, method, nutritional info and other details can be obtained.

# Milestone 2
The web scraping will be implemented with Selenium as that seems to offer more features for interacting with the web site should I need this. I am however concerned about performance once I move past scraping a few pages of data.
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


