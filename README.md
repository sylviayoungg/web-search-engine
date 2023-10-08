# web-search-engine
Web search engine with GUI.

User can search through 10,000+ web pages scraped from a subset of provided URLs.

The links are checked for validity based on whether or not they belong to a set of valid domains and are unique. The web scraper abides by each web page's robot.txt file, a file that tells web scrapers which links are able to be accessed. The scraped links are indexed in a file system based on the content of the pages.

When the user searches for terms using the GUI, the pages are ranked based on their relevance to the search terms through a custom system according to tf-idf score, word weight, frequency, and position and returned according to the ranking. Irrelevant pages are not returned in the search.
