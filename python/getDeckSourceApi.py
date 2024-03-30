from datetime import datetime
import sys
from googleChrome import GoogleChrome
from googleCloudPlatform import GoogleCloudPlatform

##### 定数 #####

# 大会結果一覧URL
COMPETITION_RESULT_LIST_URL = "https://players.pokemon-card.com/event/result/list?offset={offset}&order=4&result_resist=1&event_type=3:1&event_type=3:2&event_type=3:7"
# 大会結果オフセット（ページ数）
COMPETITION_RESULT_OFFSET = 0
# 入賞デッキ一覧URL
DECK_LIST_URL = "https://players.pokemon-card.com/event/detail/{competition_id}/result"
# 次ページに遷移するためのボタン情報
NEXT_PAGE_BUTTON = '//button[@class="btn" and text()="2"]'
# ソース記入用スプレッドシートID
INPUT_GSPREAD_ID = '1lG_M08B4vg9zn-wyEcmbEtgaDMQfGyY4VklHh4oD8wg'
# INPUT_GSPREAD_ID = '1ZIr135QzW6uXLU3LUH0eCduXxSC3UCgO_IfSMVlD0C4'
# 入力用ワークシート名
INPUT_WORK_SHEET_NAME = 'source'
# 大会ID一覧ファイル
COMPETITION_ID_FILE = '/Users/minakungooner/Desktop/python/pokemon_card/competition_id.txt'
# 最大追記数
MAX_WRITE_COUNT = 20


##### 処理 #####

# 開始
print('start:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 大会結果一覧URLのソースを取得（時間がかかるので5秒待機）
url = COMPETITION_RESULT_LIST_URL.format(offset=COMPETITION_RESULT_OFFSET)
competition_list_source = GoogleChrome.getInstance().getSource(url, 5)
# ソースから大会IDを取得
competition_source_elements = GoogleChrome.getInstance().getSourceElementAll(competition_list_source, 'a', 'eventListItem')
competition_ids = GoogleChrome.getInstance().getCompetitionId(competition_source_elements)

# 大会ID一覧ファイルを開いて中身を読み込む
with open(COMPETITION_ID_FILE, "r") as file:
    file_contents = file.read()

write_ids = []
# 大会IDが既に書き込み済みか確認
for competition_id in competition_ids:
    if competition_id in file_contents:
        continue

    # 書き込まれていなければ追記するIDを保持
    write_ids.append(competition_id)

# 追記する大会があればソース情報を取得してスプレッドシートに追記
if len(write_ids) > 0:
     # GCPのAPIを利用してスプレッドシート開く
    GoogleCloudPlatform.getInstance().openGspread(INPUT_GSPREAD_ID)
    GoogleCloudPlatform.getInstance().openWorkSheet(INPUT_WORK_SHEET_NAME)
    # 1(A列)を指定して入力されている最後の行を取得し、その次から追記していく
    last_row_index = GoogleCloudPlatform.getInstance().getWriteLastRow(1)
    add_row = last_row_index

    write_count = 0
    # 書き込まれていなければ新たに書き込み、その大会の入賞デッキソースを取得する
    with open(COMPETITION_ID_FILE, "a") as file:
        # 各大会のソースを取得してスプレッドシートに追記
        for write_id in write_ids:
            # 追記する最大数を超える場合終了
            if write_count >= MAX_WRITE_COUNT:
                break

            # 大会IDからURLを作成
            url = DECK_LIST_URL.format(competition_id=write_id)
            # ベスト8とベスト16のソースをそれぞれ取得
            top_source = GoogleChrome.getInstance().getSource(url, 1)
            bottom_source = GoogleChrome.getInstance().getClickSource(NEXT_PAGE_BUTTON)

            add_row += 1
            # A列に大会ID、B列にベスト8、C列にベスト16を追記
            GoogleCloudPlatform.getInstance().writeSheet(write_id, 'A'+''+str(add_row))
            GoogleCloudPlatform.getInstance().writeSheet(top_source, 'B'+''+str(add_row))
            # ベスト16のソースがあれば追記
            if bottom_source != '':
                GoogleCloudPlatform.getInstance().writeSheet(bottom_source, 'C'+''+str(add_row))

            # 大会ID一覧ファイルにも追記
            file.write(write_id + "\n")
            print('add_id:'+str(write_id))

            write_count += 1

 # WebDriverを終了
GoogleChrome.getInstance().quitDriver()

# 終了
print('finish:'+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
