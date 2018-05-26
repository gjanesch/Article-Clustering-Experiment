from bs4 import BeautifulSoup
import requests
import newspaper
import re

def get_page_html(url):
    return BeautifulSoup(requests.get(url).text, "lxml")

def get_article_recommendations(next_article):
    article_html = get_page_html(next_article)
    recommended_for_you = article_html.find("div",attrs={'id':'article-rec'})
    assert recommended_for_you is not None
    if len(recommended_for_you) > 0:
        articles = recommended_for_you.find_all("a")
        articles = ["https://www.spectrum.ieee.org" + a["href"] for a in articles]
    else:
        articles = []
    return articles

# There are some articles which lack both significant text and recommended articles;
# we want to detect these in order to remove them
def is_article_excluded(url):
    is_webinar = re.search("/webinar/", url) is not None
    is_whitepaper = re.search("/whitepaper/", url) is not None
    return is_webinar or is_whitepaper


ieee_spectrum = newspaper.build("https://www.spectrum.ieee.org/", memoize_articles = False)

seen_articles = []
article_urls = [a.url for a in ieee_spectrum.articles]

while len(article_urls) > 0:
    print(f"There are {len(article_urls)} unprocessed articles and {len(seen_articles)} that have been seen.")
    all_articles = set(seen_articles).union(set(article_urls))
    
    next_article = article_urls.pop(0)
    print("Processing page " + next_article)
    try:
        new_articles = get_article_recommendations(next_article)
    except AssertionError:
        print("***No recommendations in this article - moving on...***")
    else:
        seen_articles.append(next_article)
        if len(new_articles) > 0:
            new_articles = [na for na in new_articles if na not in all_articles]
        article_urls.extend(new_articles)