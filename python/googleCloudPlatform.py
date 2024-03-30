import gspread
from oauth2client.service_account import ServiceAccountCredentials

# GoogleCloudPlatformクラス
class GoogleCloudPlatform:

    # GCPの認証サービスアカウントキーが記入されているjsonファイル
    GSPREAD_SERVICE_ACCOUNT = '/home/pokekadb/www/web/pokekaSheet/pokekaSheet/pokemon-card-league-f1d86294eaa3.json'

    __instance = None
    __client = None
    __spreadsheet = None
    __worksheet = None

    # シングルトン
    @staticmethod 
    def getInstance():
        if GoogleCloudPlatform.__instance == None:
            GoogleCloudPlatform()
        return GoogleCloudPlatform.__instance

    def __init__(self):
        if GoogleCloudPlatform.__instance != None:
            raise Exception("Singletonクラス")
        else:
            GoogleCloudPlatform.__instance = self
            self.accessGspread()

    # GCPのAPIにアクセスして初期化
    def accessGspread(self):
        # Google Sheets APIとDrive APIを使用してスプレッドシートにアクセス
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # 認証キーを渡して接続
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.GSPREAD_SERVICE_ACCOUNT, scope)
        self.__client = gspread.authorize(credentials)
        return
    
    # スプレッドシートを開く
    def openGspread(self, sheet_id):
        if self.__client == None:
            self.accessGspread()

        # スプレッドシートを開く
        self.__spreadsheet = self.__client.open_by_key(sheet_id)
        return

    # ワークシートを開く(既にスプレッドシートが開かれてる前提)
    def openWorkSheet(self, sheet_name):

        # ワークシートを開く
        self.__worksheet = self.__spreadsheet.worksheet(sheet_name)
        return

    # スプレッドシートに書き込む(既にワークシートが開かれてる前提)
    def writeSheet(self, source, cell):

        # スプレッドシートに書き込む
        self.__worksheet.update_acell(cell, source)
        return

    # 列を指定してその列の入力されている最後の行を取得
    def getWriteLastRow(self, column):
        # 指定の列の値を取得
        values = self.__worksheet.col_values(column)

        # 最後の空でない行を見つける
        last_row_index = len(values)

        return last_row_index
