import sys
import time
import re

import requests
from bs4 import BeautifulSoup

from typing import List
IdList = List[str]


def get_participants_id_list(event_url: str) -> IdList:
    """イベント参加予定者のユーザidのリストを取得
    Args:
        event_url (str): イベントページのURL
    Returns:
        IdList: ユーザidのリスト
    """

    # 申込みをしたユーザのページを取得
    participants_url = f'{event_url}/participation'
    r = requests.get(participants_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    participants_id_list = []

    # イベント関係者
    for participation_table_list in soup.select('.concerned_area .participation_table_area'):
        for participating_user in participation_table_list.select('.user'):
            user_url = participating_user.select('.display_name a')[0]['href']
            m = re.match('https://connpass.com/user/(.*)/', user_url)
            participants_id_list.append(m.group(1))

    # 一般参加者のユーザ一覧のテーブルからユーザidを取得
    for participation_table_list in soup.select('.applicant_area .participation_table_area'):

        # 100名以上いる場合は、別ページになっている
        another_page_list = participation_table_list.select('.empty')
        if len(another_page_list) > 0:
            another_page_url_base = another_page_list[0].select('a')[0]['href']

            another_page_url = another_page_url_base

            while True:
                print(another_page_url)
                r = requests.get(another_page_url)
                another_soup = BeautifulSoup(r.text, 'html.parser')

                participants_list = another_soup.select(
                    '.applicant_area .participation_table_area .user')
                for participating_user in participants_list:
                    user_url = participating_user.select(
                        '.display_name a')[0]['href']
                    m = re.match('https://connpass.com/user/(.*)/', user_url)
                    participants_id_list.append(m.group(1))

                page_cand = another_soup.select('.paging_area ul li')
                if "次へ" in page_cand[-1].text:
                    param = page_cand[-1].select('a')[0]["href"]
                    another_page_url = another_page_url_base + param
                else:
                    break

                time.sleep(1)
        # 一般参加者が100名未満の場合
        else:
            for participating_user in participation_table_list.select('.user'):
                user_url = participating_user.select(
                    '.display_name a')[0]['href']
                m = re.match('https://connpass.com/user/(.*)/', user_url)
                participants_id_list.append(m.group(1))

    # 欠席者ユーザ一覧のテーブルからユーザidを取得
    for participation_table_list in soup.select('.applicant_area .cancelled_table_area'):
        for participating_user in participation_table_list.select('.user'):
            user_url = participating_user.select('.display_name a')[0]['href']
            m = re.match('https://connpass.com/user/(.*)/', user_url)
            participants_id_list.append(m.group(1))

    # 重複するユーザidを除外
    # イベント関係者がイベント申し込み者にいる場合があるため。
    participants_id_list = list(set(participants_id_list))

    return participants_id_list


url = sys.args[1]


participants_id_list = get_participants_id_list(url)

import pdb
pdb.set_trace()
