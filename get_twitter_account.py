# ユーザのアカウントページからtwitter urlを取得
import requests
from bs4 import BeautifulSoup
import re

prog = re.compile("http://twitter.com/*")

# 自分のurlで試験
url = "https://connpass.com/user/meow_noisy/"

r = requests.get(url)

soup = BeautifulSoup(r.text, 'html.parser')

social_links = soup.select('.social_link a')

for link in social_links:
    url = link["href"]

    m = prog.match(url)
    if m:
        print(url)
