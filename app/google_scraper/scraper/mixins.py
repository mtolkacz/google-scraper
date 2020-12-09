import datetime
import json
import logging
import random
import pytz
from requests import get

from bs4 import BeautifulSoup

from .apps import ScraperConfig
from .models import Results
from ..core.utils import get_client_ip

# Get an instance of a logger
logger = logging.getLogger(__name__)


class GoogleScraper:
    """
    Scrape Google result
    """

    # Example list of not counted strings in the list of most popular words in the results.
    # In go-live approach to this solution could be more complex and precise.
    # This is an example with the simplest logic.
    EXCLUDED_WORDS = [
        'and', 'na', 'by', 'the', 'to', 'do', 'from', 'jakie', 'me', 'in',
        'ch', 'is', 'of', 'od', 'an', 'pod', 'się', 'jako', 'jego', 'as',
    ]

    # List of characters to delete from title and description result blocks
    ODD_CHARS = [
        ':', '“', '—', '+', '-', '„', '”', ',', '|', '(', ')', '.',
    ]

    # Amount of most popular words in the results
    TOP_WORDS_QTY = 10

    # Different browser simulation
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

    def __init__(self, query, request, results_limitation=20, lang=None, country=None, browser=None):

        # User's query from form
        self.query = query

        # Get custom browser or take from request header
        # If provided incorrect browser then take random custom browser
        if browser:
            if browser in self.BROWSERS:
                user_agent = self.BROWSERS[browser]
            else:
                user_agent = self.BROWSERS[random.choice(list(self.BROWSERS.keys()))]
        else:
            user_agent = request.headers["User-Agent"]

        # Get user's request header to fake google request
        self.usr_agent = {
            'User-Agent': user_agent
        }

        # Limited by parameter number of returned results in Google query
        self.results_limitation = results_limitation

        # Language parameter in the request
        self.lang = lang

        # Country parameter in the request
        self.country = country

        # Prepare Google url, which contains user's query, number of returned results and language
        self.google_url = 'https://www.google.com/search?q={}&num={}' \
            .format(self.query.replace(' ', '+'),
                    self.results_limitation + 5,
                    )

        # Add an optional interface language parameter
        self.google_url += f'&hl={self.lang}' if self.lang else ''

        # Add an optional search results location limitation parameter
        self.google_url += f'&cr=country{self.country}' if self.country else ''

        # Number of Google's results and BeautifulSoup's parsed html
        self.number_of_results, self.soup = None, None

        # Lists of links downloaded from results
        self.links = []

        # List of all and most popular words in results - based on titles and descriptions
        self.words, self.top_words = {}, {}

    def search(self):
        html = self.fetch_results()
        self.parse_results(html)

        results = {
            'query': self.query,
            'links': self.get_enumerated_dict_links(),
            'top_words': self.top_words,
            'number_of_results': self.number_of_results,
            'results_limitation': self.results_limitation,
            'top_words_number': self.TOP_WORDS_QTY,
        } if self.number_of_results else {
            'error': 'No records found',
            'query': self.query,
        }

        return results

    def fetch_results(self):
        response = get(self.google_url, headers=self.usr_agent)
        response.raise_for_status()

        return response.text

    def parse_results(self, raw_html):
        self.soup = BeautifulSoup(raw_html, 'html.parser')
        self.number_of_results = self.get_number_of_results()

        result_block = self.soup.find_all('div', attrs={'class': 'g'})

        for result in result_block:
            try:
                title = result.find('h3').get_text()
                description = result.find('span', attrs={'class': 'aCOpRe'}).get_text()
                link = result.find('a', href=True)
            except AttributeError:
                # This happen when result block is not a standard one, eg. Twitter block
                # We skip this iteration
                continue

            description_words = self.deleted_odd_chars(description).lower().split()
            title_words = self.deleted_odd_chars(title).lower().split()

            title_words = self.get_validated_words(title_words)
            description_words = self.get_validated_words(description_words)
            validated_words = description_words + title_words

            for word in validated_words:
                self.words[word] = self.words[word] + 1 if word in self.words else 1

            self.set_link(title, link)
            if len(self.links) == self.results_limitation:
                break

        self.set_top_words()

    def deleted_odd_chars(self, text):
        """
        Remove all odd and not needed characters from the variable passed.
        """
        for ch in self.ODD_CHARS:
            if ch in text:
                text = text.replace(ch, '')
        return text

    def get_number_of_results(self):
        """
        Parse soup in search of number of all results.
        Include situations where numbers are presented
        with comma or dot separator in different languages.
        PL - 10 000
        DE - 10.000
        EN - 10,000
        """
        try:
            stats_list = self.soup.find_all('div', attrs={'id': 'result-stats'})[0].get_text().split()
            stats_number = ''
            for i, item in enumerate(stats_list):
                if item[0].isdigit():
                    stats_number += item
                elif i > 0:
                    break
        except IndexError as err:
            logger.error(f"Results stats not found in the soup: {err}")
        else:
            # Try to convert stats to int
            # Stats number in different languages may contain dot or comma, so try to delete these chars.
            return int(stats_number.replace('.', '').replace(',', ''))

    def get_validated_words(self, words):
        """
        Return filtered list of words with length greater than 1,
        not digits and not from the list of excluded words.
        """
        validated_words = []
        for word in words:
            if len(word) > 1 and not word.isdigit() and word not in self.EXCLUDED_WORDS:
                validated_words.append(word)
        return validated_words

    def set_link(self, title, link):
        """
        Add link to the list of links if exists and has title.
        In addition it has to lead to external resource
        - this means it's not Google internal request, like /search?=q
        """
        if link and title and 'http' in link['href']:
            self.links.append(link['href'])

    def get_enumerated_dict_links(self):
        return dict((i + 1, link) for i, link in enumerate(self.links))

    def set_top_words(self):
        sorted_words = dict(sorted(self.words.items(), key=lambda item: item[1], reverse=True))

        for i, key in enumerate(list(sorted_words.keys())):
            if i < self.TOP_WORDS_QTY:
                self.top_words[key] = sorted_words[key]


class ResultsMixin(object):

    def __init__(self):
        self.query, self.existing_obj, self.ip = None, None, None
        self.results = {}
        self.now = datetime.datetime.now(pytz.utc)

    def get_results(self, request):
        """
        Get results from db, if exist and valid,
        else scrape new one and update existing or create new Results object
        :return: Results dictionary based on GoogleScraper.search()
        """
        self.query = request.session['query'] if 'query' in request.session else None

        if self.query:
            self.ip = get_client_ip(request)
            try:
                self.existing_obj = self.get_results_from_db()

                if self.results_are_valid():
                    self.results = self.get_result_dict_from_existing()
            except Results.DoesNotExist:
                pass
            finally:
                # Object not exist or is not valid then scrape and create new or update existing object
                if not self.results:
                    scraper = GoogleScraper(self.query, request)
                    self.results = scraper.search()
                    self.save_results_in_db()

            # Delete query session variable to force redirect to form view
            del request.session['query']

            return self.results

    def get_results_from_db(self):
        """
        Get Results object based on user's IP address and query
        """
        return Results.objects.values(
            'id',
            'number_of_results',
            'links',
            'top_words',
            'results_limitation',
            'top_words_number',
            'modified_date',
        ).get(query=self.query.lower(), ip=self.ip)

    def get_result_dict_from_existing(self):
        return {'query': self.query,
                'links': json.loads(self.existing_obj['links']),
                'top_words': json.loads(self.existing_obj['top_words']),
                'number_of_results': self.existing_obj['number_of_results'],
                'results_limitation': self.existing_obj['results_limitation'],
                'top_words_number': self.existing_obj['top_words_number']}

    def save_results_in_db(self):
        """
        Update Results object if already exists in db, else create new one
        """
        if 'error' not in self.results:
            Results.objects.filter(id=self.existing_obj['id']).update(
                number_of_results=self.results['number_of_results'],
                top_words=json.dumps(self.results['top_words']),
                links=json.dumps(self.results['links']),
                results_limitation=self.results['results_limitation'],
                top_words_number=self.results['top_words_number'],
                modified_date=datetime.datetime.now(pytz.utc)
            ) if self.existing_obj else Results.objects.create(
                ip=self.ip,
                query=self.query.lower(),
                number_of_results=self.results['number_of_results'],
                top_words=json.dumps(self.results['top_words']),
                links=json.dumps(self.results['links']),
                results_limitation=self.results['results_limitation'],
                top_words_number=self.results['top_words_number'],
            )

    def results_are_valid(self):
        """
        Check if results are valid in application config according to SCRAPING_EXPIRATION time policy
        :return: True if valid, else False
        """
        expiration_datetime = self.existing_obj['modified_date'] + datetime.timedelta(
            seconds=ScraperConfig.SCRAPING_EXPIRATION
        )
        return True if self.now < expiration_datetime else False


