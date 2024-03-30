from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
import re

# GoogleChromeクラス
class GoogleChrome:

    __instance = None
    __driver = None

    # シングルトン
    @staticmethod 
    def getInstance():
        if GoogleChrome.__instance == None:
            GoogleChrome()
        return GoogleChrome.__instance

    def __init__(self):
        if GoogleChrome.__instance != None:
            raise Exception("Singletonクラス")
        else:
            GoogleChrome.__instance = self
            self.initDriver()
    
    # Chromeドライバーの初期化
    def initDriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # ヘッドレスモードを有効にする場合
        self.__driver = webdriver.Chrome(options=chrome_options)
    
    # ソースを取得
    def getSource(self, url, sleep_time = 0):
        # ターゲットのURLにアクセス
        self.__driver.get(url)

        # ページが完全に読み込まれるのを待機
        self.__driver.implicitly_wait(10)  # 最大で10秒待機

        # 待機時間がある場合、指定の時間待機する
        if sleep_time > 0:
            time.sleep(sleep_time)

        #ソースを取得
        source = self.__driver.page_source

        return source

    # ボタンクリック後のソースを取得(直前に同じURLのクリック前のソースを取得している前提)
    def getClickSource(self, button_xpath):
        try:
            # ボタンがクリック可能になるまで待機
            button = self.__driver.find_element(By.XPATH, button_xpath)

            # ボタンクリック
            button.click()

            # ソースが反映されるまで少し待機
            time.sleep(0.5)

            # ソースを取得
            source = self.__driver.page_source

        except NoSuchElementException:
            # 要素が見つからない場合終了
            return ''

        return source

    # ソースから必要な要素を全て抽出
    def getSourceElementAll(self, source, tag, class_name):
        # BeautifulSoupを使用してHTMLを解析
        soup = BeautifulSoup(source, 'html.parser')

        # 指定のタグとクラス名から要素を全て取得
        elements = soup.find_all(tag, class_=class_name)

        return elements

    # 大会一覧ソースの要素から大会IDを取得
    def getCompetitionId(self, elements):
        competition_ids = []
        for elem in elements:
            # 大会名がシティリーグでなければ関係ないのでcontinue
            competition_name = elem.find('div', class_='title').get_text()
            if 'シティリーグ' not in competition_name:
                continue
                
            # hrefの要素から数値のみ取り出してIDを取得
            href = elem.attrs['href']
            number = re.findall(r'\d+', href)
            competition_ids.append(''.join(number))

        # 逆順にして返却（ページは新しい順に並んでいるので）
        competition_ids.reverse()
        return competition_ids

    # WebDriverを終了
    def quitDriver(self):
        self.__driver.quit()
        return
