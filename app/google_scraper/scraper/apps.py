from django.apps import AppConfig


class ScraperConfig(AppConfig):
    name = 'google_scraper.scraper'

    # Time parameter in sec when scraping result will be updated
    SCRAPING_EXPIRATION = 20
