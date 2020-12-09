# Google scraper
Downloading list of search result (SERP) from Google, based on the query passed to the form

## Requirements
1. Get links to websites with position information
* Number of links to configure in the GoogleScraper class constructor
2. Get top 10 most occurring words in descriptions and titles.
* Number of words to configure in TOP_WORDS_QTY variable in the GoogleScraper class
3. Get number of Google results
* Adjusted to different format (like PL 10 000, EN 10,000, DE 10.000)

## Functionalities
1. Query by writing term in the form
2. Save results in a database with user's IP address
3. Cache and get results from a database under specified time, otherwise do re-scraping
   
        class ScraperConfig(AppConfig):
            name = 'google_scraper.scraper'

            SCRAPING_EXPIRATION = 20
4. Database result caching should be configurable   
5. Possibility to simulate custom browser behaviour - browser parameter is available in the GoogleScraper class constructor

        # List based on https://deviceatlas.com/blog/list-of-user-agent-strings#desktop
        BROWSERS = {
   
        # Windows 10-based PC using Edge browser
        'Edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246 ',

        # Chrome OS-based laptop using Chrome browser (Chromebook)
        'Chrome': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/51.0.2704.64 Safari/537.36 ',

        # Linux-based PC using a Firefox browser
        'Firefox': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        
        }
6. Additional query parameters in the GoogleScraper class constructor:
* lang (<i>hl</i>) - interface language
* country (<i>countryXX</i>) - search results location limitation

## Technologies
* Python 3.9<br>
* Django 3.1.3<br>
* Django Rest Framework 3.12.2<br>
* PostgreSQL 13.0<br>
* Docker 19.03.8<br>
* docker-compose 1.27.4<br>
## Run application from docker containers
> docker-compose -f local.yml up -d --build
## Live demo
> https://mt-google-scraper.herokuapp.com/
