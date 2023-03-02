import os
import json
import requests
import re
import numpy as np
import string
from nltk import word_tokenize
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET
from bs4.element import Comment
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from scipy import spatial
import gensim.downloader as api
from lxml import html

from dotenv import load_dotenv
load_dotenv()


# define parameters for API calls to the Encyclopedia Britannica products

article_list_url = {
    'advanced': 'https://syndication.api.eb.com/production/articles?articleTypeId=1&page=',
    'concise': 'https://syndication.api.eb.com/production/articles?articleTypeId=45&page=',
    'intermediate': 'https://syndication.api.eb.com/production/articles?articleTypeId=31&page='
}

json_header = {
    'advanced': {
        'x-api-key': os.getenv('EB_API_KEY_ADV'),
        'content-type': 'application/json'
    },
    'concise': {
        'x-api-key': os.getenv('EB_API_KEY_CON'),
        'content-type': 'application/json'
    },
    'intermediate': {
        'x-api-key': os.getenv('EB_API_KEY_INT'),
        'content-type': 'application/json'
    }
}

xml_header = {
    'advanced': {
        'x-api-key': os.getenv('EB_API_KEY_ADV'),
        'content-type': 'text/xml; charset=UTF-8'
    },
    'intermediate': {
        'x-api-key': os.getenv('EB_API_KEY_INT'),
        'content-type': 'text/xml; charset=UTF-8'
    },
    'concise': {
        'x-api-key': os.getenv('EB_API_KEY_CON'),
        'content-type': 'text/xml; charset=UTF-8'
    }
}


# get list of metadata for all entries in each source (e.g. for each encyclopedia article)
def get_encyclopedia_metadata(source="advanced", dir_path=None):
    article_metadata = []

    code = 200
    page = 1

    url = article_list_url[source] + str(page)
    response = requests.get(url, headers=json_header[source])

    while code == 200 and page < 100:
        this_data = json.loads(response.text)['articles']
        article_metadata += this_data
        page += 1
        url = article_list_url[source] + str(page)
        response = requests.get(url, headers=json_header[source])
        code = response.status_code

    path = dir_path
    if not os.path.exists(path):
        os.makedirs(path)

    filepath = os.path.join(path, source + '.json')
    if os.path.exists(filepath):
        os.remove(filepath)

    with open(filepath, 'w') as outfile:
        json.dump(article_metadata, outfile, indent=2)

    return article_metadata


# get article content (text) for a given article_id
def get_article_title_text(article_id, source="advanced"):
    url = f'https://syndication.api.eb.com/production/article/{str(article_id)}/xml'
    response = requests.get(url, headers=xml_header[source])
    soup = BeautifulSoup(response.text, features="xml")
    tree = html.fromstring(response.content)
    title = tree.xpath("//article")[0].xpath("title/text()")[0]
    text = text_from_html(soup)
    return title, text


# get text content for a collection of article_ids
def get_articles(article_ids, source="advanced"):
    articles = []
    for article_id in article_ids:
        title, text = get_article_title_text(article_id, source=source)
        this_article = {
            "article_id": article_id,
            "title": title,
            "text": text
        }
        articles.append(this_article)
    return articles


####################################

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(soup):
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


####################################

