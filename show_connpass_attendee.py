# connpassのイベント参加者のTwitter idを取得するスクリプト。実行すると1行ごとにユーザidを格納したtxtファイルを生成する
# 実行方法: $ python show_connpass_attendee.py [connpassのURL]


import sys
import time
import re
import argparse

import requests
from bs4 import BeautifulSoup

from typing import List
IdList = List[str]


def get_participants_connpass_ids_in_one_page(participation_table_list) -> List[str]:
    """1ページ内のテーブルからconnpassユーザidを取得し、リストを作成する

    Args:
        participation_table_list ([type]): BeautifulSoupのオブジェクト。ルートにテーブルを持っている

    Returns:
        IdList: ページ内のconnpassユーザidのリスト
    """
    connpass_id_list = []
    for participating_user in participation_table_list.select('.user'):
        user_url = participating_user.select('.display_name a')[0]['href']
        m = re.match('https://connpass.com/user/(.*)/',
                     user_url)  # ユーザページのリンクからidを取得
        connpass_id_list.append(m.group(1).replace(
            "/open", ""))  # イベント関係者の場合、リンクに/openがつくので除去

    return connpass_id_list


def get_participants_twitter_ids_in_one_page(participation_table_list) -> List[str]:

    twitter_id_list = []

    for participating_user in participation_table_list.select('.social'):
        sns_list = participating_user.select('a')
        for sns in sns_list:
            url = sns['href']
            m = re.match('https://twitter.com/intent/user\?screen_name=(.*)/?',
                         url)  # ユーザページのリンクからidを取得
            if m:
                twitter_id_list.append(
                    m.group(1))  # イベント関係者の場合、リンクに/openがつくので除去
                break

    return twitter_id_list


def get_participants_id_list(event_url: str, service: str = "twitter", exclude_cancel: bool = False) -> List[str]:
    """イベント参加予定者のユーザidのリストを取得
    Args:
        event_url (str): イベントページのURL
    Returns:
        IdList: ユーザidのリスト
    """

    # 申込みをしたユーザのページを取得
    participants_url = f'{event_url}/participation'
    r = requests.get(participants_url)
    assert r.status_code == 200
    soup = BeautifulSoup(r.text, 'html.parser')

    master_participants_id_list = []

    # ユーザidを取得したいサービスの関数を選択
    if service == "twitter":
        get_id_func = get_participants_twitter_ids_in_one_page
    elif service == "connpass":
        get_id_func = get_participants_connpass_ids_in_one_page
    else:
        raise ValueError(f"{service} is not unsupported.")

    # イベント関係者
    for participation_table_list in soup.select('.concerned_area .participants_table'):
        master_participants_id_list += get_id_func(
            participation_table_list)

    # 一般参加者のユーザ一覧のテーブルからユーザidを取得
    for participation_table_list in soup.select('.applicant_area .participation_table_area'):

        # 100名以上いる場合は、別ページになっている
        another_page_list = participation_table_list.select('.empty')
        # 別ページがある場合は1ページずつ巡回してリストを取得
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

                master_participants_id_list += get_id_func(
                    participation_table_list[0])  # 別ページの場合は、1つのテーブルしかないはずなので、インデックスを指定

                # 次のページがあるかを判定
                page_cand = another_soup.select('.paging_area ul li')
                if "次へ" in page_cand[-1].text:
                    param = page_cand[-1].select('a')[0]["href"]
                    another_page_url = another_page_url_base + param
                else:
                    break

                # マナーとしてリクエスト間隔をあける
                time.sleep(1)
        # 一般参加者が100名未満の場合
        else:
            # ページ内のユーザidを取得
            master_participants_id_list += get_id_func(
                participation_table_list)

    if exclude_cancel is False:
        # 欠席者ユーザ一覧のテーブルからユーザidを取得
        for participation_table_list in soup.select('.applicant_area .cancelled_table_area'):
            master_participants_id_list += get_id_func(
                participation_table_list)

    # 重複するユーザidを除外
    # イベント関係者がイベント申し込み者にいる場合があるため。
    master_participants_id_list = list(set(master_participants_id_list))

    return master_participants_id_list


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help="connpassのイベントURL")
    parser.add_argument('-o', '--output_txt', default=None, help="出力ファイルへのパス")
    parser.add_argument('-s', '--service', type=str, default="twitter",
                        choices=["twitter", "connpass"], help="どのサービスのアカウントをリストとして取得するか")
    parser.add_argument('--exclude_cancel',
                        action="store_true", help="このオプションを追加すると、キャンセルしたユーザをリストに含めない")

    args = parser.parse_args()

    # output_txtが指定されていない場合は、URLを加工してファイル名を作る
    if args.output_txt is None:
        output_txt = args.url.replace(
            "https://", "").replace("/", "_") + f"{args.service}.txt"
    else:
        output_txt = args.output_txt

    # 参加者のidリストを取得
    id_list = get_participants_id_list(
        args.url, args.service, args.exclude_cancel)

    # 出力ファイルを生成する
    with open(output_txt, "w") as f:
        for id_ in id_list:
            f.write(f"{id_}\n")
