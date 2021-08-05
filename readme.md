# connpassのイベント参加者のTwitter idを収集し、Twitterリストを作成するPythonスクリプト

## セットアップ
- Twitter APIの利用申請を行い、受理される
- Twitter APIのTokenを発行する
    - Twitter APIトークン発行時にはWrite権限を付与しておく必要があることに注意
- 必要なパッケージをインストール
  - `$ pip install -r requirements.txt`
- `create_participants_twitter_list.py`の`"ここは自分が生成したものを入力する"`を書き換える

## 使い方
処理は2段階に分かれています。

1. connpassのイベント参加者リストのスクレイピング
2. Twitterのリストを作成

それぞれを以下で説明します。
スクリプト自体は処理ごとに独立しているので、どちらか片方の処理だけを行うこともできます。


### connpassのイベント参加者リストのスクレイピング
`$ python get_participants_id_from_connpass.py <connpassのイベントURL> [オプション]`です。

下記は`python get_participants_id_from_connpass.py -h`のヘルプの説明文です。
```
usage: get_participants_id_from_connpass.py [-h] [-o OUTPUT_TXT]
                                            [-s {twitter,connpass}]
                                            [--exclude_cancel]
                                            url

positional arguments:
  url                   connpassのイベントURL

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_TXT, 
                        出力ファイルへのパス
  -s {twitter,connpass}, --service {twitter,connpass}
                        どのサービスのアカウントをリストとして取得するか
  --exclude_cancel      このオプションを追加すると、キャンセルしたユーザをリストに含めない
```

### Twitterのリストを作成
`$ python create_participants_twitter_list.py <ファイルパス> [リスト名]`

第1引数はTwitter idが1行ずつ記載されたファイルです。また第2引数はリスト名です。第2引数が設定されていない場合はファイル名がリスト名になります。
実行すると、APIと紐づくアカウントにTwitterリストが作られます。


## リンク
- 解説記事
    - [connpassのイベント参加者のTwitter idを収集し、Twitterリストを作成するPythonスクリプトを書いた](https://meow-memow.hatenablog.com/entry/2021/07/25/141047)
