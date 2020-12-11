import random

import pytest
from bs4 import BeautifulSoup
from django import urls
from requests import get

from ..mixins import GoogleScraper


@pytest.fixture
def soup():
    """
    Prepare soup based on "test" query with 5 results
    """
    url = 'https://www.google.com/search?q=test&num=5'
    browsers = GoogleScraper.BROWSERS
    usr_agent = {
        'User-Agent': browsers[random.choice(list(browsers.keys()))]
    }
    raw_html = get(url, headers=usr_agent).text
    return BeautifulSoup(raw_html, 'html.parser')


def test_result_block(soup):
    """
    Check if result blocks with the 'q' class exists in Google result
    """
    return soup.find('div', attrs={'class': 'g'})


@pytest.fixture
def result_block(soup):
    """
    Use test result blocks as a other tests fixture
    """
    return soup.find('div', attrs={'class': 'g'})


def test_title(result_block):
    """
    Verify if title is in a result block
    """
    assert result_block.find('h3')


def test_description(result_block):
    """
    Verify if description is in a result block
    """
    assert result_block.find('span', attrs={'class': 'aCOpRe'})


def test_link(result_block):
    """
    Verify if link is in a result block
    """
    assert result_block.find('a', href=True)


def test_scraper_site(client):
    """
    Verify if scraper site renders as expected
    """
    url = urls.reverse('scraper:index')
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'form' in resp.content


def test_results_site(client):
    """
    Verify if results site failed as expected when try access with no query
    """
    url = urls.reverse('scraper:results')
    resp = client.get(url)
    assert resp.status_code == 302


@pytest.mark.django_db
def test_redirect_to_results_when_scraping(client):
    """
    Verify that after passing value in scraper form,
    user is redirected to results view.
    """
    url = urls.reverse('scraper:index')
    resp = client.post(url, {
        'query': 'test',
    })
    assert resp.url == urls.reverse('scraper:results')
