#!/usr/bin/env python3

import feedparser
import requests
import time

# Constants

LOBSTERS_FEED_URL       = 'https://lobste.rs/rss'
LOBSTERS_MINIMUM_SCORE  = 10
LOBSTERS_LINK_ARTICLE   = False

# Functions

def fetch_article_json(url):
    response = requests.get(url + '.json')
    return response.json()

def fetch_all_articles(url=LOBSTERS_FEED_URL):
    feed = feedparser.parse(url)

    for entry in feed.entries:
        json = fetch_article_json(entry.comments)
        yield {
            'title'     : entry.title,
            'author'    : entry.author.split('@')[0],
            'link'      : entry.link,
            'comments'  : entry.comments,
            'published' : entry.published,
            'timestamp' : entry.published_parsed,
            'guid'      : entry.guid,
            'score'     : json['score'],
            'commentnum': len(json['comments'])
        }

        time.sleep(0.5)   # Work around rate limit

def write_articles_feed(articles):
    print('''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Lobsters</title>
<link>https://lobste.rs</link>
<description></description>''')

    for article in sorted(articles, key=lambda a: a['timestamp'], reverse=True):
        print('''<item>
<title><![CDATA[{article_title}]]></title>
<author>{article_author}</author>
<link>{rss_link}</link>
<guid isPermaLink="false">{article_guid}</guid>
<pubDate>{article_published}</pubDate>
<description><![CDATA[
<p>Article URL: <a href="{article_link}">{article_link}</a></p>
<p>Comments URL: <a href="{article_commments}">{article_commments}</a></p>
<p>Points: {article_score}</p>
<p># Comments: {article_commentnum}</p>
]]></description>
</item>'''.format(rss_link           = article['link'] if LOBSTERS_LINK_ARTICLE else article['comments'],
                  article_title      = article['title'],
                  article_author     = article['author'],
                  article_link       = article['link'],
                  article_guid       = article['guid'],
                  article_commments  = article['comments'],
                  article_score      = article['score'],
                  article_commentnum = article['commentnum'],
                  article_published  = article['published']))
    print('''</channel>
</rss>''')

# Main Execution

if __name__ == '__main__':
    write_articles_feed(a for a in fetch_all_articles() if a['score'] > LOBSTERS_MINIMUM_SCORE)
