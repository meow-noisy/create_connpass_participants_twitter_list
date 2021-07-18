import sys
import time
import re

import requests
from bs4 import BeautifulSoup

from typing import List
IdList = List[str]


def get_participants_ids_in_one_page(participation_table_list) -> IdList:
    """1ページ内のテーブルからユーザidを取得する

    Args:
        participation_table_list ([type]): BeautifulSoupのオブジェクト。ルートにテーブルを持っている

    Returns:
        IdList: ページ内のユーザidのリスト
    """
    participants_id_list = []
    for participating_user in participation_table_list.select('.user'):
        user_url = participating_user.select('.display_name a')[0]['href']
        m = re.match('https://connpass.com/user/(.*)/',
                     user_url)  # ユーザページのリンクからidを取得
        participants_id_list.append(m.group(1).replace(
            "/open", ""))  # イベント関係者の場合、リンクに/openがつくので除去
    return participants_id_list


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

    master_participants_id_list = []

    # イベント関係者
    for participation_table_list in soup.select('.concerned_area .participants_table'):
        master_participants_id_list += get_participants_ids_in_one_page(
            participation_table_list)

    # 一般参加者のユーザ一覧のテーブルからユーザidを取得
    for participation_table_list in soup.select('.applicant_area .participation_table_area'):

        # 100名以上いる場合は、別ページになっている
        another_page_list = participation_table_list.select('.empty')
        # 別ページがある場合
        if len(another_page_list) > 0:
            another_page_url_base = another_page_list[0].select('a')[0]['href']

            another_page_url = another_page_url_base

            # ページ巡回
            while True:
                print(another_page_url)
                r = requests.get(another_page_url)
                another_soup = BeautifulSoup(r.text, 'html.parser')

                # ページ内のユーザidを取得
                participation_table_list = another_soup.select(
                    '.applicant_area .participation_table_area')

                master_participants_id_list += get_participants_ids_in_one_page(
                    participation_table_list[0])  # 別ページの場合は、1つのテーブルしかないはずなので、インデックスを指定

                page_cand = another_soup.select('.paging_area ul li')
                if "次へ" in page_cand[-1].text:
                    param = page_cand[-1].select('a')[0]["href"]
                    another_page_url = another_page_url_base + param
                else:
                    break

                time.sleep(1)
        # 一般参加者が100名未満の場合
        else:
            # ページ内のユーザidを取得
            master_participants_id_list += get_participants_ids_in_one_page(
                participation_table_list)

    # 欠席者ユーザ一覧のテーブルからユーザidを取得
    for participation_table_list in soup.select('.applicant_area .cancelled_table_area'):
        master_participants_id_list += get_participants_ids_in_one_page(
            participation_table_list)

    # 重複するユーザidを除外
    # イベント関係者がイベント申し込み者にいる場合があるため。
    master_participants_id_list = list(set(master_participants_id_list))

    return master_participants_id_list


url = sys.argv[1]


participants_id_list = get_participants_id_list(url)

import pdb
pdb.set_trace()
