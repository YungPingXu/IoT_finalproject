from bs4 import BeautifulSoup
from selenium import webdriver
import time
from datetime import datetime

url = "https://sleague.tw/gameList.html"
driver = webdriver.Chrome() # 啟動瀏覽器
driver.get(url) # 取得網頁原始碼
driver.refresh() # 重新刷新網頁
time.sleep(2)
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find("table", {"class": "table table-hover same-bg"}).find("tbody")

current_date = datetime.now()

for i in table.find_all("tr"):
	text = list(i.stripped_strings)
	date = datetime.strptime(text[1], "%Y/%m/%d")
	if date >= current_date:
		print(text[1], end=" ") # 日期
		print(text[2]) # 時間
		print(text[3]) # 舉辦地點
		team = str(text[4]).replace("\t", "").replace("\n", " ").replace(" ", "").split("vs.") # 參賽隊伍
		print(team[0], end=" ") # 參賽隊伍1
		print(team[1]) # 參賽隊伍2
		print()

driver.quit() # 關閉瀏覽器