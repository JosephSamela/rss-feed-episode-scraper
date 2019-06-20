import os
import threading
import requests
import xmltodict
from datetime import datetime, timedelta

class feed():
    def __init__(self, url):
        self.url   = url
        self.title = ""
        self.episodes = []

        self.parse_feed(self.url)

    def parse_feed(self, feed_url, days_past=5):
        # Get rss feed from url
        r = requests.get(feed_url)
        # Parse feed to dict
        feed = xmltodict.parse(r.text)
        # Read channel title
        self.title = feed['rss']['channel']['title']
        # Build list of channel episodes
        for ep in feed['rss']['channel']['item']:
            # First check date
            date  = ep['pubDate']
            date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S +%f')
            # Expect date in the format:
            # Wed, 05 Jun 2019 13:26:09 +0000

            # Find episodes released in the past 1 day
            if date > datetime.utcnow() - timedelta(days=days_past):
                self.episodes.append(episode(
                    self.title, # feedtitle 
                    ep['title'],# episode title
                    ep['guid'], # episode url
                    date        # episode date
                    ))

class episode():
    def __init__(self, feedtitle, title, url, date):
        self.feedtitle = title
        self.title = title
        self.url   = url
        self.date  = date
        # Download episode in new thread
        threading.Thread(target=self.download).start()

    def download(self):
        os.system('wget {} -O ./downloads/"{} - {}.{}"'.format(
            self.url,               # File url
            self.title,             # Episode title
            self.feedtitle,         # Feed title
            self.url.split('.')[-1] # File extension
            ))

def read_feed_list(path):
    # Read feeds from textfile
    with open(path) as f:
        feedlist = f.readlines()
    feeds = []
    # Remove comment lines beginning with `#`
    for line in feedlist:
        if line[0] != '#' and line[0] != '\n':
            url = line[:-1] # remove `\n` newline from url    
            feeds.append(url)
    return feeds

def main():
    feedlist = read_feed_list('feeds.txt')
    feeds = []
    for f in feedlist:
        feeds.append( feed(f) )
    return feeds

if __name__ == '__main__':
    feeds = main()