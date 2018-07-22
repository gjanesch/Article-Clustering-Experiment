from bs4 import BeautifulSoup
import requests
import newspaper
import re
import os
import pandas as pd
from collections import namedtuple


def get_page_html(url):
    return BeautifulSoup(requests.get(url).text, "lxml")


def get_article_recommendations(next_article):
    article_html = get_page_html(next_article)
    recommended_for_you = article_html.find("div",attrs={'id':'article-rec'})
    assert recommended_for_you is not None
    if len(recommended_for_you) > 0:
        articles = recommended_for_you.find_all("a")
        articles = ["https://spectrum.ieee.org" + a["href"] for a in articles]
    else:
        articles = []
    return [a for a in articles if not is_article_excluded(a)]


# quick check to weed out obvious articles that don't fit the requirements
def is_article_excluded(url):
    is_url_wrong = re.search("//spectrum\.ieee\.org/", url) is None
    is_webinar = re.search("/webinar/", url) is not None
    is_whitepaper = re.search("/whitepaper/", url) is not None
    is_static = re.search("/static/",url) is not None
    return is_webinar or is_whitepaper or is_static or is_url_wrong


# figure out which category an article belongs to, for reference when we try clustering
# the articles
def get_article_type(url):
    ieee_article_regex = "^https://spectrum\.ieee\.org/(.*)/.*?$"
    article_type_string = re.match(ieee_article_regex, url)
    if article_type_string is None:
        return ""
    else:
        article_types = article_type_string.group(1).split("/")
        article_categories = [atype for atype in article_types if atype in ARTICLE_CATEGORIES]
        return article_categories[0]



ARTICLE_CATEGORIES = ["aerospace","at-work","biomedical","computing","energy","consumer-electronics",
                      "geek-life","green-tech","tech-history","robotics","semiconductors","telecom","transportation"]

IEEE_ARTICLE_FILE = "article_df.csv"

# If there's a csv of articles already, start with that; if not, start from
# nothing
if os.path.isfile(IEEE_ARTICLE_FILE):
    article_df = pd.read_csv(IEEE_ARTICLE_FILE, sep = "\t")
    seen_articles = article_df["URL"].tolist()
else:
    article_df = pd.DataFrame({"URL":[],"Category":[],"Article_Text":[]})
    article_df = article_df[["URL","Category","Article_Text"]]
    seen_articles = []

ieee_spectrum = newspaper.build("https://www.spectrum.ieee.org/", memoize_articles = False)
article_urls = [a.url for a in ieee_spectrum.articles]

while len(article_urls) > 0:
    print(f"There are {len(article_urls)} unprocessed articles and {len(seen_articles)} that have been seen.")
    all_articles = set(seen_articles + article_urls)

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

ArticleTuple = namedtuple("ArticleTuple",["URL","Category","Article_Text"])
list_of_article_tuples = []

for _ in tqdm.trange(len(seen_articles)):
    article_url = seen_articles[0]
    article = newspaper.Article(article_url)
    article.download()
    article.parse()
    article_tuple = ArticleTuple(url=article_url, article_text = article.text)
    list_of_article_tuples.append(article_tuple)
    seen_articles.pop(0)

with open("article_urls.txt", "w") as f:
    f.writelines([s + "\n" for s in seen_articles])
