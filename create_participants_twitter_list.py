# Twitter idの載ったファイルを読み込んで、プライベートのTwitterリストを作成するスクリプト
# 使用例: python create_participants_twitter_list.py $1 [$2]
# $1: Twitter idが1行ずつ書かれたテキストファイル
# $2(option): 作成時のTwitterリスト名。与えない場合は$1が使われる。

import sys

import tweepy

# 認証に必要なキーとトークン。トークンはWrite権限を付与する必要があることに注意
API_KEY = 'ここは自分が生成したものを入力する'
API_SECRET = 'ここは自分が生成したものを入力する'
ACCESS_TOKEN = 'ここは自分が生成したものを入力する'
ACCESS_TOKEN_SECRET = 'ここは自分が生成したものを入力する'

# APIの認証
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

filename = sys.argv[1]
if len(sys.argv) == 3:
    list_name = sys.argv[2]
else:
    list_name = filename

# Twitter idが1行ずつ書かれたテキストファイルをリスト形式で読み込む
with open(filename) as f:
    twitter_id_list = [s.strip() for s in f.readlines()]

# リストを作成(プライベートで作成)
new_twitter_list_obj = api.create_list(
    list_name, mode="private", description="for_api")
# リストのidを取得
twitter_list_id = new_twitter_list_obj.id

# リストにTwitterユーザを追加する
for twitter_id in twitter_id_list:
    try:
        api.add_list_members(list_id=twitter_list_id, user_id=[twitter_id])
    except tweepy.error.TweepError:
        print(f"id {twitter_id} doesn't exist.")
