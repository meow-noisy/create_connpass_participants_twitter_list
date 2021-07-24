# ユーザのアカウントページからtwitter urlを取得

import sys

import requests
from bs4 import BeautifulSoup
import re

prog = re.compile("http://twitter.com/(.*)/?")


def get_twitter_account(commpass_user_page_url):

    r = requests.get(commpass_user_page_url)

    soup = BeautifulSoup(r.text, 'html.parser')

    social_links = soup.select('.social_link a')

    for link in social_links:
        url = link["href"]

        m = prog.match(url)
        if m:
            print(url)
            return m.group(1)


if __name__ == "__main__":
    # 自分のurlで試験
    # url = "https://connpass.com/user/meow_noisy/"

    url = sys.argv[1]

    account = get_twitter_account(url)

    print(account)
