import data_collector

if __name__ == "__main__":
    my_scraper = data_collector.dc_scraper()
    my_scraper.search_recipes("chicken")
